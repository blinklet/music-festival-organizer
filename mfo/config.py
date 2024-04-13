# mfo/config.py

import os
import dotenv


app_dir = os.path.abspath(os.path.dirname(__file__))
project_dir = os.path.dirname(app_dir)
dotenv.load_dotenv()

# General Config
ENVIRONMENT = os.environ.get("FLASK_ENVIRONMENT")
DEBUG = os.environ.get("FLASK_DEBUG")
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
SERVER_NAME = os.environ.get("FLASK_SERVER_NAME")
EXPLAIN_TEMPLATE_LOADING = os.environ.get("FLASK_EXPLAIN_TEMPLATE_LOADING")

# Flask-SQLAlchemy variables
if ENVIRONMENT == "development":
     SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")\
          or 'sqlite:///' + os.path.join(project_dir, 'app.sqlite')
else:
     SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO")
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True} # From Flask-Security-Too configuration recommendations. 
# See: https://flask-security-too.readthedocs.io/en/stable/quickstart.html#sqlalchemy-application
# See: https://docs.sqlalchemy.org/en/20/core/pooling.html#disconnect-handling-pessimistic

# Flask-Security variables
SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
SECURITY_ANONYMOUS_USER_DISABLED = True # See: https://flask-security-too.readthedocs.io/en/stable/changelog.html#notes
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_CHANGEABLE = True
SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False


# Flask-Session variables
SESSION_TYPE = os.environ.get("SESSION_TYPE")
SESSION_PERMANENT = os.environ.get("SESSION_PERMANENT")
SESSION_KEY_PREFIX = os.environ.get("SESSION_KEY_PREFIX")
SESSION_SQLALCHEMY = os.environ.get("SESSION_SQLALCHEMY")
REMEMBER_COOKIE_SAMESITE = "strict"
SESSION_COOKIE_SAMESITE = "strict"


# Roles (name, description, set of permissions)
ROLES  = {
    'USER': {
        'name': 'User',
        'description': 'Normal users',
        'permissions': { 'read', 'write' }
    },
    'ADMIN': {
        'name': 'Admin',
        'description': 'Administrators',
        'permissions': { 'read', 'write' }
    },
}


# The first admin user, called "superuser"
SUPERUSER_EMAIL = os.environ.get("SUPERUSER_ID")
SUPERUSER_PASSWORD = os.environ.get("SUPERUSER_PASSWORD")
SUPERUSER_ROLES = [role['name'] for role in ROLES.values()]


# Nav bar links
from collections import namedtuple
Link = namedtuple("Link", "text route roles")
NAV_LINKS = [
    Link(text='Home', route='home.index', roles={'Admin','User'}),
    Link(text='Admin', route='home.index', roles={'Admin'}),
    Link(text='Account', route='home.index', roles={'Admin','User'}),
    Link(text='Login', route='home.index', roles={'Admin','User'}),
    Link(text='Register', route='home.index', roles={'Admin','User'}),
    Link(text='Logout', route='home.index', roles={'Admin','User'}),
]
