import datetime
import logging
import re
import traceback
import uuid
from ast import literal_eval

import validators
from formencode.variabledecode import variable_decode
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.security import remember
from pyramid.session import check_csrf_token
import {{ cookiecutter.project_name }}.plugins as p
from {{ cookiecutter.project_name }}.config.encdecdata import encode_data
from {{ cookiecutter.project_name }}.processes.avatar import Avatar
from {{ cookiecutter.project_name }}.views.classes import PublicView
from {{ cookiecutter.project_name }}.config.auth import get_user_data, resetKeyExists, getUserByEmail, setPasswordResetToken, resetPassword
from {{ cookiecutter.project_name }}.processes.db import (
    register_user,
    update_last_login,
)
from {{ cookiecutter.project_name }}.config.jinja_extensions import jinjaEnv, ExtendThis
from {{ cookiecutter.project_name }}.utility.helpers import readble_date
from email.mime.text import MIMEText
from email.header import Header
from email import utils
from jinja2 import ext
from time import time
import smtplib
import secrets

log = logging.getLogger("{{ cookiecutter.project_name }}")

def render_template(template_filename, context):
    return jinjaEnv.get_template(template_filename).render(context)

class HomeView(PublicView):
    def process_view(self):
        return {"activeUser": None}


class NotFoundView(PublicView):
    def process_view(self):
        self.request.response.status = 404
        return {}


class Gravatar(PublicView):
    def process_view(self):
        self.returnRawViewResult = True
        try:
            size = int(self.request.params.get("size", 45))
        except ValueError:
            size = 45
        name = self.request.params.get("name", "#")
        avatar = Avatar.generate(size, name, "PNG")
        headers = [("Content-Type", "image/png")]
        return Response(avatar, 200, headers)


class ErrorView(PublicView):
    def process_view(self):
        user = None
        i_user_authorization = p.PluginImplementations(p.IUserAuthorization)
        continue_authorization = True
        for plugin in i_user_authorization:
            continue_authorization = plugin.before_check_authorization(self.request)
            break  # Only only plugin will be called for before_check_authorization
        if continue_authorization:
            policy = get_policy(self.request, "main")
            login_data = policy.authenticated_userid(self.request)
            if login_data is not None:
                login_data = literal_eval(login_data)
                if login_data["group"] == "mainApp":
                    user = login_data["login"]
        else:
            authorized = False
            user_authorized = None
            for plugin in i_user_authorization:
                authorized, user_authorized = plugin.custom_authorization(self.request)
                break  # Only only plugin will be called for custom_authorization
            if authorized:
                user = user_authorized

        if user is None:
            policy = get_policy(self.request, "assistant")
            login_data = policy.authenticated_userid(self.request)
            if login_data is not None:
                login_data = literal_eval(login_data)
                if login_data["group"] == "collaborator":
                    user = login_data["login"]

        if user is None:
            user = "Unknown"
        log.error(
            "Server Error in URL {}.\nAccount: {}\nError: \n{}".format(
                self.request.url, user, traceback.format_exc()
            )
        )
        self.request.response.status = 500
        return {}


class LoginView(PublicView):
    def process_view(self):
        # If we logged in then go to private
        next_page = self.request.params.get("next")
        if self.request.method == "GET":
            policy = get_policy(self.request, "main")
            login_data = policy.authenticated_userid(self.request)
            if login_data is not None:
                login_data = literal_eval(login_data)
                if login_data["group"] == "mainApp":
                    current_user = get_user_data(login_data["login"], self.request)
                    if current_user is not None:
                        self.returnRawViewResult = True
                        return HTTPFound(
                            location=self.request.route_url(
                                "private", userid=current_user.login
                            ),
                            headers={"FS_error": "true"},
                        )
        else:
            if (
                self.request.registry.settings.get("perform_post_checks", "true")
                == "true"
            ):
                safe = check_csrf_token(self.request, raises=False)
                if not safe:
                    raise HTTPNotFound()
            data = variable_decode(self.request.POST)

            login = data["email"]
            passwd = data["passwd"]
            user = get_user_data(login, self.request)
            login_data = {"login": login, "group": "mainApp"}
            if user is not None:
                if user.check_password(passwd, self.request):
                    continue_login = True
                    # Load connected plugins and check if they modify the login authorization
                    for plugin in p.PluginImplementations(p.IUserAuthentication):
                        continue_with_login, error_message = plugin.after_login(
                            self.request, user
                        )
                        if not continue_with_login:
                            self.append_to_errors(error_message)
                            continue_login = False
                        break  # Only one plugging will be called to extend after_login
                    if continue_login:
                        update_last_login(self.request, user.login)
                        headers = remember(
                            self.request, str(login_data), policies=["main"]
                        )
                        next_page = self.request.params.get(
                            "next"
                        ) or self.request.route_url("private", userid=user.login)
                        self.returnRawViewResult = True
                        return HTTPFound(location=next_page, headers=headers)
                else:
                    log.error(
                        "Logging into account {} provided an invalid password".format(
                            login
                        )
                    )
                    self.append_to_errors(
                        self._(
                            "The user account does not exists or the password is invalid"
                        )
                    )
            else:
                log.error("User account {} does not exist".format(login))
                self.append_to_errors(
                    self._(
                        "The user account does not exists or the password is invalid"
                    )
                )
        return {"next": next_page}


class RefreshSessionView(PublicView):
    def process_view(self):
        return {}


def get_policy(request, policy_name):
    policies = request.policies()
    for policy in policies:
        if policy["name"] == policy_name:
            return policy["policy"]
    return None


def log_out_view(request):
    policy = get_policy(request, "main")
    headers = policy.forget(request)
    loc = request.route_url("home")
    raise HTTPFound(location=loc, headers=headers)


class RegisterView(PublicView):
    def process_view(self):
        # If we logged in then go to private
        if self.request.method == "GET":
            data = {}
        else:
            if (
                self.request.registry.settings.get("perform_post_checks", "true")
                == "true"
            ):
                safe = check_csrf_token(self.request, raises=False)
                if not safe:
                    raise HTTPNotFound()
            data = variable_decode(self.request.POST)

            if validators.email(data["user_email"]):
                if data["user_password"] != "":
                    if re.match(r"^[A-Za-z0-9._]+$", data["user_id"]):
                        if data["user_password"] == data["user_password2"]:
                            if len(data["user_password"]) <= 50:
                                data["user_cdate"] = datetime.datetime.now()
                                if "user_apikey" not in data.keys():
                                    data["user_apikey"] = str(uuid.uuid4())
                                data["user_password"] = encode_data(
                                    self.request, data["user_password"]
                                )
                                data["user_active"] = 1
                                # Load connected plugins and check if they modify the registration of an user
                                continue_registration = True
                                for plugin in p.PluginImplementations(p.IRegistration):
                                    (
                                        data,
                                        continue_with_registration,
                                        error_message,
                                    ) = plugin.before_register(self.request, data)
                                    if not continue_with_registration:
                                        self.append_to_errors(error_message)
                                        continue_registration = False
                                    break  # Only one plugging will be called to extend before_register
                                if continue_registration:
                                    added, error_message = register_user(
                                        self.request, data
                                    )
                                    if not added:
                                        self.append_to_errors(error_message)
                                    else:
                                        # Load connected plugins so they perform actions after the registration
                                        # is performed
                                        next_page = self.request.route_url(
                                            "private", userid=data["user_id"]
                                        )
                                        plugin_next_page = ""
                                        for plugin in p.PluginImplementations(
                                            p.IRegistration
                                        ):
                                            plugin_next_page = plugin.after_register(
                                                self.request, data
                                            )
                                            break  # Only one plugging will be called to extend after_register
                                        if plugin_next_page is not None:
                                            if plugin_next_page != "":
                                                if plugin_next_page != next_page:
                                                    next_page = plugin_next_page
                                        if next_page == self.request.route_url(
                                            "private", userid=data["user_id"]
                                        ):
                                            login_data = {
                                                "login": data["user_id"],
                                                "group": "mainApp",
                                            }
                                            headers = remember(
                                                self.request,
                                                str(login_data),
                                                policies=["main"],
                                            )
                                            self.returnRawViewResult = True
                                            return HTTPFound(
                                                location=self.request.route_url(
                                                    "private", userid=data["user_id"]
                                                ),
                                                headers=headers,
                                            )
                                        else:
                                            self.returnRawViewResult = True
                                            return HTTPFound(next_page)
                            else:
                                self.append_to_errors(
                                    self._(
                                        "The password must be less than 50 characters"
                                    )
                                )
                        else:
                            log.error(
                                "Password {} and confirmation {} are not the same".format(
                                    data["user_password"], data["user_password2"]
                                )
                            )
                            self.append_to_errors(
                                self._(
                                    "The password and its confirmation are not the same"
                                )
                            )
                    else:
                        log.error(
                            "Registering user {} has invalid characters".format(
                                data["user_id"]
                            )
                        )
                        self.append_to_errors(
                            self._(
                                "The user id has invalid characters. Only underscore "
                                "and dot are allowed"
                            )
                        )
                else:
                    log.error(
                        "Registering user {} has empty password".format(data["user_id"])
                    )
                    self.append_to_errors(self._("The password cannot be empty"))
            else:
                log.error("Invalid email {}".format(data["user_email"]))
                self.append_to_errors(self._("Invalid email"))
        return {"next": next, "userdata": data}

class RecoverPasswordView(PublicView):
    def send_password_by_email(self, body, target_name, target_email, mail_from):
        msg = MIMEText(body.encode("utf-8"), "plain", "utf-8")
        ssubject = self._("{{ cookiecutter.project_name }} - Password reset request")
        subject = Header(ssubject.encode("utf-8"), "utf-8")
        msg["Subject"] = subject
        msg["From"] = "{} <{}>".format("{{ cookiecutter.project_name }}", mail_from)
        recipient = "{} <{}>".format(target_name.encode("utf-8"), target_email)
        msg["To"] = Header(recipient, "utf-8")
        msg["Date"] = utils.formatdate(time())
        try:
            smtp_server = self.request.registry.settings.get(
                "email.server", "localhost"
            )
            smtp_user = self.request.registry.settings.get("email.user")
            smtp_password = self.request.registry.settings.get("email.password")

            server = smtplib.SMTP(smtp_server, 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.sendmail(mail_from, [target_email], msg.as_string())
            server.quit()

        except Exception as e:
            print(str(e))

    def send_password_email(self, email_to, reset_token, reset_key, user_dict):
        jinjaEnv.add_extension(ext.i18n)
        jinjaEnv.add_extension(ExtendThis)
        _ = self.request.translate
        email_from = self.request.registry.settings.get("email.from", None)
        if email_from is None:
            log.error(
                "{{ cookiecutter.project_name }} has no email settings in place. Email service is disabled."
            )
            return False
        if email_from == "":
            return False
        date_string = readble_date(datetime.datetime.now(), self.request.locale_name)
        reset_url = self.request.route_url("reset_password", reset_key=reset_key)
        text = render_template(
            "email/recover_email.jinja2",
            {
                "recovery_date": date_string,
                "reset_token": reset_token,
                "user_dict": user_dict,
                "reset_url": reset_url,
                "_": _,
            },
        )

        self.send_password_by_email(text, user_dict.name, email_to, email_from)

    def process_view(self):

        # If we logged in then go to dashboard
        policy = get_policy(self.request, "main")
        login = policy.authenticated_userid(self.request)
        currentUser = get_user_data(login, self.request)
        if currentUser is not None:
            raise HTTPNotFound()

        if "submit" in self.request.POST:
            email = self.request.POST.get("user_email", None)
            if email is not None:
                user, password = getUserByEmail(email, self.request)
                if user is not None:

                    reset_key = str(uuid.uuid4())
                    reset_token = secrets.token_hex(16)
                    setPasswordResetToken(
                        self.request, user.login, reset_key, reset_token
                    )
                    self.send_password_email(user.email, reset_token, reset_key, user)
                    self.returnRawViewResult = True
                    return HTTPFound(location=self.request.route_url("login"))
                else:
                    self.append_to_errors(
                        self._(
                            "Cannot find an user with such email address"
                        )
                    )
            else:

                self.append_to_errors(
                    self._(
                        "You need to provide an email address"
                    )
                )

        return {}


class ResetPasswordView(PublicView):
    def process_view(self):
        dataworking = {}

        reset_key = self.request.matchdict["reset_key"]

        if not resetKeyExists(self.request, reset_key):
            raise HTTPNotFound()

        if self.request.method == "POST":

            safe = check_csrf_token(self.request, raises=False)
            if not safe:
                raise HTTPNotFound()

            dataworking = self.get_post_dict()
            login = dataworking["user"]
            token = dataworking["token"]
            new_password = dataworking["password"].strip()
            new_password2 = dataworking["password2"].strip()
            user = dataworking["user"]
            if user != "":
                log.error(
                    "Suspicious bot password recovery from IP: {}. Agent: {}. Email: {}".format(
                        self.request.remote_addr,
                        self.request.user_agent,
                        dataworking["email"],
                    )
                )
            user = get_user_data(login, self.request)

            if user is not None:
                if user.userData["user_password_reset_key"] == reset_key:
                    if user.userData["user_password_reset_token"] == token:
                        if (
                            user.userData["user_password_reset_expires_on"]
                            > datetime.datetime.now()
                        ):
                            if new_password != "":
                                if new_password == new_password2:
                                    new_password = encode_data(
                                        self.request, new_password
                                    )
                                    resetPassword(
                                        self.request,
                                        user.userData["user_name"],
                                        reset_key,
                                        token,
                                        new_password,
                                    )
                                    self.returnRawViewResult = True
                                    return HTTPFound(
                                        location=self.request.route_url("login")
                                    )
                                else:

                                    self.append_to_errors(
                                        self._(
                                            "The password and the confirmation are not the same"
                                        )
                                    )
                            else:
                                self.append_to_errors(
                                    self._(
                                        "The password cannot be empty"
                                    )
                                )
                        else:

                            self.append_to_errors(
                                self._(
                                    "Invalid token"
                                )
                            )
                    else:

                        self.append_to_errors(
                            self._(
                                "Invalid token"
                            )
                        )
                else:

                    self.append_to_errors(
                        self._(
                            "Invalid key"
                        )
                    )
            else:

                self.append_to_errors(
                    self._(
                        "User does not exist"
                    )
                )

        return {"dataworking": dataworking}