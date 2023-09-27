import argparse
import os
import random
import string

from jinja2 import Environment, FileSystemLoader


def random_password(size):
    """Generate a random password """
    random_source = string.ascii_letters + string.digits + string.punctuation
    password = random.choice(string.ascii_lowercase)
    password += random.choice(string.ascii_uppercase)
    password += random.choice(string.digits)
    password += random.choice(string.punctuation)
    for i in range(size):
        password += random.choice(random_source)
    password_list = list(password)
    random.SystemRandom().shuffle(password_list)
    password = "".join(password_list)
    return password


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ini_path", help="Path to ini file to create")
    parser.add_argument("--mysql_host", default="localhost", help="MySQL host server to use. Default to localhost")
    parser.add_argument(
        "--mysql_port", default=3306, help="MySQL port to use. Default to 3306"
    )
    parser.add_argument(
        "--mysql_schema",
        default="{{ cookiecutter.project_name }}",
        help="MySQL schema to use. Default to '{{ cookiecutter.project_name }}'",
    )
    parser.add_argument(
        "--mysql_user_name",
        required=True,
        help="MySQL user name to use to create the schema",
    )
    parser.add_argument(
        "--mysql_user_password", required=True, help="MySQL user name password"
    )
    parser.add_argument(
        "--repository_path", required=True, help="Path to the {{ cookiecutter.project_name }} repository"
    )
    parser.add_argument(
        "--forwarded_allow_ip",
        required=True,
        help="IP of the proxy server calling {{ cookiecutter.project_name }}",
    )
    parser.add_argument(
        "--pid_file",
        required=True,
        help="File that will store the {{ cookiecutter.project_name }} process ID",
    )
    parser.add_argument(
        "--error_log_file",
        required=True,
        help="File that will store the {{ cookiecutter.project_name }} logs",
    )
    parser.add_argument(
        "-d",
        "--daemon",
        action="store_true",
        help="Start as {{ cookiecutter.project_name }} in detached mode",
    )
    parser.add_argument(
        "-c",
        "--capture_output",
        action="store_true",
        help="Start as {{ cookiecutter.project_name }} in detached mode",
    )
    parser.add_argument("--{{ cookiecutter.project_name }}_host", required=True, help="Host name for {{ cookiecutter.project_name }}")
    parser.add_argument("--{{ cookiecutter.project_name }}_port", required=True, help="Port for {{ cookiecutter.project_name }}")
    args = parser.parse_args()
    {{ cookiecutter.project_name }}_path = "."
    if not os.path.exists(os.path.join({{ cookiecutter.project_name }}_path, "templates")):
        print("You need to execute this in the directory {{ cookiecutter.project_name }}")
        exit(1)
    main_secret = random_password(13).replace("%", "~")
    redis_sessions_secret = random_password(13).replace("%", "~")
    auth_secret = random_password(13).replace("%", "#")
    aes_key = random_password(28).replace("%", "#")

    template_environment = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join({{ cookiecutter.project_name }}_path, "templates")),
        trim_blocks=False,
    )

    context = {
        "mysql_host": args.mysql_host,
        "mysql_port": args.mysql_port,
        "mysql_schema": args.mysql_schema,
        "mysql_user_name": args.mysql_user_name,
        "mysql_user_password": args.mysql_user_password,
        "main_secret": main_secret,
        "auth_secret": auth_secret,
        "aes_key": aes_key,
        "redis_sessions_secret": redis_sessions_secret,
        "repository_path": args.repository_path,
        "{{ cookiecutter.project_name }}_host": args.{{ cookiecutter.project_name }}_host,
        "{{ cookiecutter.project_name }}_port": args.{{ cookiecutter.project_name }}_port,
        "daemon": args.daemon,
        "pid_file": args.pid_file,
        "error_log_file": args.error_log_file,
        "forwarded_allow_ip": args.forwarded_allow_ip,
    }

    rendered_template = template_environment.get_template("config.template").render(
        context
    )
    ini_path = os.path.abspath(args.ini_path)
    alembic_context = {
        "mysql_host": args.mysql_host,
        "mysql_port": args.mysql_port,
        "mysql_schema": args.mysql_schema,
        "mysql_user_name": args.mysql_user_name,
        "mysql_user_password": args.mysql_user_password,
        "config_path": ini_path,
    }
    rendered_alembic = template_environment.get_template("alembic.template").render(
        alembic_context
    )
    alembic_file = os.path.dirname(ini_path) + "/alembic.ini"

    if not os.path.exists(args.ini_path):
        with open(args.ini_path, "w") as f:
            f.write(rendered_template)
        with open(alembic_file, "w") as f:
            f.write(rendered_alembic)
        print("{{ cookiecutter.project_name }} INI file created at {}".format(args.ini_path))
    else:
        print("INI file {} already exists".format(args.ini_path))
