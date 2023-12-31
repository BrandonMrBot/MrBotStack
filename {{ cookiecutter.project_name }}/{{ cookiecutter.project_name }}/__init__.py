import sys

if sys.version_info[0] == 3 and sys.version_info[1] >= 6:
    import gevent.monkey

    gevent.monkey.patch_all()


from pyramid.config import Configurator
import os

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_authstack import AuthenticationStackPolicy
from {{ cookiecutter.project_name }}.config.environment import load_environment
from configparser import ConfigParser, NoOptionError

def main(global_config, **settings):
    apppath = os.path.dirname(os.path.abspath(__file__))

    if global_config is not None:  # pragma: no cover
        config = ConfigParser()
        config.read(global_config["__file__"])
        try:
            threads = config.get("server:main", "threads")
        except NoOptionError:
            threads = "1"
        settings["apppath"] = apppath
        settings["server:threads"] = threads
        settings["global:config:file"] = global_config["__file__"]

    """This function returns a Pyramid WSGI application."""

    auth_policy = AuthenticationStackPolicy()
    policy_array = []

    main_policy = AuthTktAuthenticationPolicy(
        settings["auth.main.secret"],
        timeout=7200,
        cookie_name=settings["auth.main.cookie"],
    )
    auth_policy.add_policy("main", main_policy)
    policy_array.append({"name": "main", "policy": main_policy})

    # Secondary authorization. Optional
    # assistant_policy = AuthTktAuthenticationPolicy(
    #     settings["auth.secondary.secret"],
    #     timeout=7200,
    #     cookie_name=settings["auth.secondary.cookie"],
    # )
    # auth_policy.add_policy("secondary", assistant_policy)
    # policy_array.append({"name": "asecondary", "policy": assistant_policy})

    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(
        settings=settings,
        authentication_policy=auth_policy,
        authorization_policy=authz_policy,
    )

    config.include(".models")
    # Load and configure the host application
    load_environment(settings, config, apppath, policy_array)

    return config.make_wsgi_app()
