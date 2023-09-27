import logging

import {{ cookiecutter.project_name }}.plugins as p
from {{ cookiecutter.project_name }}.plugins.utilities import add_route

from {{ cookiecutter.project_name }}.views.public_views import (
    NotFoundView,
    HomeView,
    log_out_view,
    LoginView,
    RegisterView,
    RefreshSessionView,
    ErrorView,
    Gravatar,
)
from {{ cookiecutter.project_name }}.views.private_views import UserPrivatePageView

log = logging.getLogger("{{ cookiecutter.project_name }}")

route_list = []


def append_to_routes(route_array):
    """
    #This function append or overrides the routes to the main list
    :param route_array: Array of routes
    """
    for new_route in route_array:
        found = False
        pos = 0
        for curr_route in route_list:
            if curr_route["path"] == new_route["path"]:
                found = True
                break
            pos = pos + 1
        if not found:
            route_list.append(new_route)
        else:
            route_list[pos]["name"] = new_route["name"]
            route_list[pos]["view"] = new_route["view"]
            route_list[pos]["renderer"] = new_route["renderer"]


def load_routes(config):
    """
    Call connected to plugins to add any routes before {{ cookiecutter.project_name }}
    :param config: Pyramid config
    """
    routes = []
    for plugin in p.PluginImplementations(p.IRoutes):
        routes = plugin.before_mapping(config)
        append_to_routes(routes)

    # {{ cookiecutter.project_name }} public routes
    routes.append(add_route("home", "/", HomeView, "public/index.jinja2"))
    routes.append(
        add_route("refresh", "/refresh", RefreshSessionView, "generic/refresh.jinja2")
    )
    routes.append(add_route("login", "/login", LoginView, "user/login.jinja2"))
    routes.append(add_route("register", "/join", RegisterView, "user/register.jinja2"))
    routes.append(add_route("recover","/recover", RecoverPasswordView, "recover.jinja2"))
    routes.append(add_route("reset_password","/reset/{reset_key}/password", ResetPasswordView, "reset_password.jinja2"))

    routes.append(add_route("logout", "/logout", log_out_view, None))
    routes.append(add_route("gravatar", "/gravatar", Gravatar, None))

    # {{ cookiecutter.project_name }} private routes
    routes.append(
        add_route(
            "private", "/user/{userid}", UserPrivatePageView, "private/index.jinja2"
        )
    )

    append_to_routes(routes)

    # Add the not found route
    config.add_notfound_view(NotFoundView, renderer="generic/404.jinja2")

    if log.level == logging.WARN:
        config.add_view(ErrorView, context=Exception, renderer="generic/500.jinja2")

    # Call connected plugins to add any routes after {{ cookiecutter.project_name }}
    for plugin in p.PluginImplementations(p.IRoutes):
        routes = plugin.after_mapping(config)
        append_to_routes(routes)

    # Now add the routes and views to the Pyramid config
    for curr_route in route_list:
        config.add_route(curr_route["name"], curr_route["path"])
        config.add_view(
            curr_route["view"],
            route_name=curr_route["name"],
            renderer=curr_route["renderer"],
        )
