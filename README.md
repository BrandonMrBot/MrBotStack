# MrBot Stack
[Pyramid]( https://trypyramid.com/) is a great framework for developing web applications that also supports the development of ["Extensible" and "Pluggable"]( http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/extending.html) software based on certain rules. However, there is no much documentation on how to create such type of applications.

[CKAN]( https://ckan.org/) is an excellent example of a Web application that can be extended or customized using plug-ins. It relies on [PyUtilib Component Architecture]( https://pypi.python.org/pypi/PyUtilib) (PCA) to declare a series of interfaces and extension points that then are used by plug-ins to hook in. It also implements a series of [Jinja2]( http://jinja.pocoo.org/) extension (notably CKAN_EXTENDS) that allows easily template inheritance between CKAN and connected plug-ins.

During the development of [FormShare](https://github.com/qlands/FormShare), [ClimMob](https://climmob.net/blog/), and other tools we borrowed certain concepts and code from CKAN to create a series of technologies to make these Pyramid Web Applications extensible and pluggable. These technologies are now stacked in MrBot Stack (MrStack).

MrStack is a CookieCutter template to create scaffolding for scalable and pluggable Pyramid Web Applications. It can be used as a starting point to develop more complex Pyramid Web Applications. The resulting project will have:

- Easy JS and CSS resource declaration and injection using Jinja2 Tags
- Database migrations using Alembic
- PCA extensibility
  - Adding new routes
   - Adding and overwriting templates
   - Adding and injecting new static resources
   - Adding and injecting new JS or CSS resources
 - [AdminLTE](https://adminlte.io) (3.0.5) HTML template system
 - Basic user registration and login using MySQL with password encryption using Fernet

## Requirements

MrBot stack depends on MySQL, Redis and Python VirtualEnv

```sh
# On Ubuntu 20.04
sudo apt-get install -y redis-server mysql-server python3.8-venv mysql-client-core-8.0 
```

## How to create a MrStack project

```sh
python3 -m venv myproject_env
. ./myproject_env/bin/activate
pip install cookiecutter
cookiecutter https://github.com/BrandonMrBot/MrBotStack
# Cookicutter will ask you the details of your project. For example project_name
cd [project_name]
# Install requirements
pip install -r ./requirements.txt
python setup.py develop
# Create an initial configuration. Change all [parameters] as appropiate
create_config --mysql_host=[mysql_host] --mysql_schema=[project_name] --mysql_user_name=[mysql_user] --mysql_user_password=[my_secure_password] ./config.ini
# Create a MySQL schema for your project
mysql -u [mysql_user] -p --execute='CREATE SCHEMA [project_name]'
# Create the initial schema
alembic upgrade head
# Run your MrStack App
pserve ./config.ini
```

## Notes

- The MrStack CookieCutter assumes that your MySQL server root account has a password. If your account does not have a password then edit the config.ini file to remove the colons (:) between the user the password. The same for alembic.ini and run again "alembic upgrade head"

  ```ini
  sqlalchemy.url = mysql+mysqlconnector://root@localhost/test_project?charset=utf8&ssl_disabled=True
  ```

- In some Linux distributions MySQL cannot connect to localhost but to 127.0.0.1. If you get a connexion refused edit the config.ini file to change localhost to 127.0.0.1. The same for alembic.ini and run again "alembic upgrade head"

  ```ini
  sqlalchemy.url = mysql+mysqlconnector://root@127.0.0.1/test_project?charset=utf8&ssl_disabled=True
  ```

  
