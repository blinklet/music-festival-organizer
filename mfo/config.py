# mfo/config.py

import os
import dotenv
from cachelib import SimpleCache

app_dir = os.path.abspath(os.path.dirname(__file__))
project_dir = os.path.dirname(app_dir)
dotenv.load_dotenv()

# General Config
ENVIRONMENT = os.environ.get("FLASK_ENVIRONMENT")
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
EXPLAIN_TEMPLATE_LOADING = os.environ.get("FLASK_EXPLAIN_TEMPLATE_LOADING")

# Flask-Security variables
SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
# The docs recommend SECURITY_ANONYMOUS_USER_DISABLED be set to True
# See: https://flask-security-too.readthedocs.io/en/stable/changelog.html#notes
SECURITY_ANONYMOUS_USER_DISABLED = True 
# Allow new users to register new accounts
SECURITY_REGISTERABLE = True
# Disable e-mail confirmation of new users (because we don't have an e-mail server set up)
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_CHANGEABLE = True
SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
SECURITY_POST_LOGIN_VIEW = '/'
SECURITY_POST_REGISTER_VIEW = '/new_user'

# Flask-SQLAlchemy variables
if ENVIRONMENT == "development":
    # For development, use a SQLite database located in the project folder
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")\
        or 'sqlite:///' + os.path.join(project_dir, 'app.sqlite')
else:
    # For production, get the database URI from environment variable
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO")
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
# The docs made the following recommendation to set the SQLAlchemy Engine Options 
# See: https://flask-security-too.readthedocs.io/en/stable/quickstart.html#sqlalchemy-application
# See: https://docs.sqlalchemy.org/en/20/core/pooling.html#disconnect-handling-pessimistic
SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}  

# Flask-Session variables
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = os.path.join(project_dir, 'session')
SESSION_FILE_THRESHOLD = 50
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True
#SESSION_SERIALIZATION_FORMAT = 'json'



# Roles defined
# Roles (name, description, set of permissions)
ROLES  = {
    'PARTICIPANT': {
        'name': 'Participant',
        'description': 'Normal user',
        'permissions': { 'user' }
    },
    'GROUP': {
        'name': 'Group',
        'description': 'Normal user',
        'permissions': { 'user' }
    },
    'ADMIN': {
        'name': 'Admin',
        'description': 'Administrator',
        'permissions': { 'admin' }
    },
    'TEACHER': {
        'name': 'Teacher',
        'description': 'Music teacher',
        'permissions': { 'user' }
    },
    'GUARDIAN': {
        'name': 'Guardian',
        'description': 'Parent or guardian',
        'permissions': { 'user' }
    },
    'ACCOMPANIST': {
        'name': 'Accompanist',
        'description': 'Accompanist',
        'permissions': { 'user' }
    },
    'TEACHER': {
        'name': 'Teacher',
        'description': 'Music teachers',
        'permissions': { 'user' }
    },
    'ADJUDICATOR': {
        'name': 'Adjudicator',
        'description': 'Festival adjudicator',
        'permissions': { 'user' }
    },
}

TEST_USERS_FILE = os.environ.get("TEST_USERS_FILE")

# Class default data
DEFAULT_ADJUDICATION_TIME = {
    'Solo': 600,  # times are in seconds
    'Recital': 900,
    'Duet': 900,
    'Trio': 1200,
    'Quartet': 1500,
    'Quintet': 1800,
    'Ensemble': 2100,
    'Composition': 600,
}
DEFAULT_MOVE_TIME = {
    'Solo': 120, # times are in seconds
    'Recital': 240,
    'Duet': 180,
    'Trio': 240,
    'Quartet': 300,
    'Quintet': 300,
    'Ensemble': 300,
    'Composition': 120,
}
DEFAULT_FEE = {
    'Solo': 12,
    'Recital': 16,
    'Duet': 12,
    'Trio': 12,
    'Quartet': 12,
    'Quintet': 12,
    'Ensemble': 25,
    'Composition': 12,
}

DISCIPLINES = [
    "Vocal", 
    "Piano", 
    "Organ", 
    "Strings",
    "Recorder",
    "Woodwinds",
    "Brass",
    "Percussion",
    "Instrumental",
    "Musical Theatre",
    ]

