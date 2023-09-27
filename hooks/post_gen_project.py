from textwrap import dedent


def main():
    display_actions_message()


def display_actions_message():

    vars = dict(separator="=" * 79)
    msg = dedent(
        """
        %(separator)s
        This is a scaffolding of a project based on MrBot Stack. You can use it
        to create complex and pluggable web applications.
        %(separator)s

        To make run this project do:
                
        Change directory into your newly created project.
            cd {{ cookiecutter.project_name }}
            
        Install all dependencies.
            pip install -r ./requirements.txt

        Build the project
            python setup.py develop
            
        Create an initial configuration
            create_config development.ini  --mysql_user_name=root --mysql_user_password=[my_secure_password] --repository_path=/home --forwarded_allow_ip=127.0.0.1 --pid_file=a.pi --error_log_file=no --testmrbotstack_host=127.0.0.1 --testmrbotstack_port=1234

        Create a schema called {{ cookiecutter.project_name }} in the MySQL server
        
        Build the initial database
            alembic upgrade head
        
        Run the application
            pserve ./config.ini
                
        """
        % vars
    )
    print(msg)


if __name__ == "__main__":
    main()
