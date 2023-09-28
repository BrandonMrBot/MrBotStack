import validators
from sqlalchemy import func

from {{ cookiecutter.project_name }}.models import User as userModel, map_from_schema
from {{ cookiecutter.project_name }}.plugins.core import PluginImplementations
from {{ cookiecutter.project_name }}.plugins.interfaces import IUserAuthentication
from {{ cookiecutter.project_name }}.config.encdecdata import decode_data
from {{ cookiecutter.project_name }}.models import map_from_schema
import datetime
from dateutil.relativedelta import relativedelta

class User(object):
    """
    This class represents a user in the system
    """

    def __init__(self, user_data):
        self.id = user_data["user_id"]
        self.email = user_data["user_email"]
        self.userData = user_data
        self.login = user_data["user_id"]
        self.name = user_data["user_name"]
        self.role = user_data["user_role"]
        self.gravatarURL = "#"
        if user_data["user_about"] is None:
            self.about = ""
        else:
            self.about = user_data["user_about"]
        self.apikey = user_data["user_apikey"]

    def check_password(self, password, request):
        self.set_gravatar_url(request, self.name, 45)
        # Load connected plugins and check if they modify the password authentication
        plugin_result = None
        for plugin in PluginImplementations(IUserAuthentication):
            plugin_result = plugin.on_authenticate_password(
                request, self.login, password
            )
            break  # Only one plugging will be called to extend authenticate_user
        if plugin_result is None:
            return check_login(self.login, password, request)
        else:
            return plugin_result

    def set_gravatar_url(self, request, name, size):
        self.gravatarURL = request.route_url(
            "gravatar", _query={"name": name, "size": size}
        )


def get_{{ cookiecutter.project_name }}_user_data(request, user, is_email):
    if is_email:
        return map_from_schema(
            request.dbsession.query(userModel)
            .filter(func.lower(userModel.user_email) == func.lower(user))
            .filter(userModel.user_active == 1)
            .first()
        )
    else:
        return map_from_schema(
            request.dbsession.query(userModel)
            .filter(userModel.user_id == user)
            .filter(userModel.user_active == 1)
            .first()
        )


def get_user_data(user, request):
    email_valid = validators.email(user)
    # Load connected plugins and check if they modify the user authentication
    plugin_result = None
    plugin_result_dict = {}
    for plugin in PluginImplementations(IUserAuthentication):
        plugin_result, plugin_result_dict = plugin.on_authenticate_user(
            request, user, email_valid
        )
        break  # Only one plugging will be called to extend authenticate_user
    if plugin_result is not None:
        if plugin_result:
            # The plugin authenticated the user. Check now that such user exists in {{ cookiecutter.project_name }}.
            internal_user = get_{{ cookiecutter.project_name }}_user_data(request, user, email_valid)
            if internal_user:
                return User(plugin_result_dict)
            else:
                return None
        else:
            return None
    else:
        result = get_{{ cookiecutter.project_name }}_user_data(request, user, email_valid)
        if result:
            result["user_password"] = ""  # Remove the password form the result
            return User(result)
        return None

def getUserByEmail(email, request):
    result = (
        request.dbsession.query(userModel)
        .filter_by(user_email=email)
        .filter_by(user_active=1)
        .first()
    )
    if result is not None:
        return (
            User(map_from_schema(result)),
            decode_data(request, result.user_password).decode("utf-8"),
        )
    return None, None

def check_login(user, password, request):
    result = (
        request.dbsession.query(userModel)
        .filter(userModel.user_id == user)
        .filter(userModel.user_active == 1)
        .first()
    )
    if result is None:
        return False
    else:
        cpass = decode_data(request, result.user_password.encode())
        if cpass == bytearray(password.encode()):
            return True
        else:
            return False

def setPasswordResetToken(request, userId, reset_key, reset_token):
    token_expires_on = datetime.datetime.now() + relativedelta(hours=+24)
    request.dbsession.query(userModel).filter(userModel.user_id == userId).update(
        {
            "user_password_reset_key": reset_key,
            "user_password_reset_token": reset_token,
            "user_password_reset_expires_on": token_expires_on,
        }
    )

def resetKeyExists(request, reset_key):
    res = (
        request.dbsession.query(userModel)
        .filter(userModel.user_password_reset_key == reset_key)
        .first()
    )
    if res is not None:
        return True
    return False

def resetPassword(request, user_id, reset_key, reset_token, new_password):
    request.dbsession.query(userModel).filter(userModel.user_id == user_id).filter(
        userModel.user_password_reset_key == reset_key
    ).filter(userModel.user_password_reset_token == reset_token).update(
        {
            "user_password_reset_key": None,
            "user_password_reset_token": None,
            "user_password_reset_expires_on": None,
            "user_password": new_password,
        }
    )

def getUserByResetKeyAnToken(request, reset_key, reset_token):
    res = map_from_schema(
        request.dbsession.query(userModel)
        .filter(userModel.user_password_reset_key == reset_key)
        .filter(userModel.user_password_reset_token == reset_token)
        .first()
    )

    return res