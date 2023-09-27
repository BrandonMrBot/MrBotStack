import os
import sys

from jinja2 import Environment, FileSystemLoader


def usage(argv):
    cmd = os.path.basename(argv[0])
    print(
        "usage: %s <path_to_ini_file> \n"
        "(example: %s ./development.ini )" % (cmd, cmd)
    )
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    {{ cookiecutter.project_name }}_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    {{ cookiecutter.project_name }}_ini_file = os.path.abspath(argv[1])
    if not os.path.exists({{ cookiecutter.project_name }}_ini_file):
        print("Ini file {} does not exists".format({{ cookiecutter.project_name }}_ini_file))
        sys.exit(1)
    {{ cookiecutter.project_name }}_celery_app = os.path.join(
        {{ cookiecutter.project_name }}_path, *["{{ cookiecutter.project_name }}", "config", "celery_app.py"]
    )

    template_environment = Environment(
        autoescape=False,
        loader=FileSystemLoader(os.path.join({{ cookiecutter.project_name }}_path, "templates")),
        trim_blocks=False,
    )

    context = {"{{ cookiecutter.project_name|upper }}_INI_FILE": {{ cookiecutter.project_name }}_ini_file}

    rendered_template = template_environment.get_template(
        "celery_app_template.template"
    ).render(context)

    with open({{ cookiecutter.project_name }}_celery_app, "w") as f:
        f.write(rendered_template)


if __name__ == "__main__":
    main()
