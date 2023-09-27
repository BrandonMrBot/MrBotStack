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
            create_config --mysql_host=localhost --mysql_schema={{ cookiecutter.project_name }} --mysql_user_name=root --mysql_user_password=[my_secure_password] ./config.ini 

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
