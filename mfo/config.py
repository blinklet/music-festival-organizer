# mfo/config.py

import os
from dotenv import load_dotenv
from decimal import Decimal
import redis
from datetime import timedelta
from cachelib import FileSystemCache


app_dir = os.path.abspath(os.path.dirname(__file__))
project_dir = os.path.dirname(app_dir)

FLASK_ENV = os.getenv('FLASK_ENV')
load_dotenv(dotenv_path=f'{project_dir}/{FLASK_ENV}.env')

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
if ENVIRONMENT == "development" or ENVIRONMENT == "lightweight":
    # For development, use a SQLite database located in the project folder
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(project_dir, 'app.sqlite')
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
SESSION_TYPE = os.environ.get('SESSION_TYPE')
SESSION_PERMANENT = True
PERMANENT_SESSION_LIFETIME = timedelta(
    seconds=int(os.environ.get("PERMANENT_SESSION_LIFETIME"))
)

if SESSION_TYPE == 'filesystem':
    SESSION_TYPE = 'cachelib'
    SESSION_THRESHOLD = int(os.environ.get('SESSION_THRESHOLD')) 
    SESSION_CACHELIB = FileSystemCache(
        threshold=SESSION_THRESHOLD, 
        cache_dir=os.path.join(project_dir, 'session'),
        default_timeout=PERMANENT_SESSION_LIFETIME.total_seconds()
    )
else:
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.Redis.from_url(os.environ.get('REDIS_URL'))


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

if ENVIRONMENT == "development" or ENVIRONMENT == "lightweight":
    TEST_USERS_FILE = os.environ.get("TEST_USERS_FILE")
    TEST_USERS_FILE = os.path.join(project_dir, TEST_USERS_FILE)
else:
    TEST_USERS_FILE = os.environ.get("TEST_USERS_FILE")


# Class default data

DEFAULT_ADJUDICATION_TIME = {
    "None" : {
        "Solo": 300,
        "Recital": 300,
        "Duet": 300,
        "Trio": 300,
        "Quartet": 300,
        "Quintet": 300,
        "Ensemble": 300,
        "Composition": 300,
    },
    "Vocal" : {
        "Solo": 600,
        "Recital": 900,
        "Duet": 900,
        "Trio": 1200,
        "Quartet": 1500,
        "Quintet": 1800,
        "Ensemble": 2100,
        "Composition": 600,
    }, 
    "Piano": {
        "Solo": 600,
        "Recital": 900,
        "Duet": 900,
        "Trio": 1200,
        "Quartet": 1500,
        "Quintet": 1800,
        "Ensemble": 2100,
        "Composition": 600,
    },
    "Organ": {
        "Solo": 600,
        "Recital": 900,
        "Duet": 900,
        "Trio": 1200,
        "Quartet": 1500,
        "Quintet": 1800,
        "Ensemble": 2100,
        "Composition": 600,
    },
    "Strings": {
        "Solo": 600,
        "Recital": 900,
        "Duet": 900,
        "Trio": 1200,
        "Quartet": 1500,
        "Quintet": 1800,
        "Ensemble": 2100,
        "Composition": 600,
    },
    "Recorder": {
        "Solo": 600,
        "Recital": 900,
        "Duet": 900,
        "Trio": 1200,
        "Quartet": 1500,
        "Quintet": 1800,
        "Ensemble": 2100,
        "Composition": 600,
    },
    "Woodwinds": {
        "Solo": 600,
        "Recital": 900,
        "Duet": 900,
        "Trio": 1200,
        "Quartet": 1500,
        "Quintet": 1800,
        "Ensemble": 2100,
        "Composition": 600,
    },
    "Brass": {
        "Solo": 600,
        "Recital": 900,
        "Duet": 900,
        "Trio": 1200,
        "Quartet": 1500,
        "Quintet": 1800,
        "Ensemble": 2100,
        "Composition": 600,
    },
    "Percussion": {
        "Solo": 600,
        "Recital": 900,
        "Duet": 900,
        "Trio": 1200,
        "Quartet": 1500,
        "Quintet": 1800,
        "Ensemble": 2100,
        "Composition": 600,
    },
    "Instrumental": {
        "Solo": 600,
        "Recital": 900,
        "Duet": 900,
        "Trio": 1200,
        "Quartet": 1500,
        "Quintet": 1800,
        "Ensemble": 2100,
        "Composition": 600,
    },
    "Musical Theatre": {
        "Solo": 600,
        "Recital": 900,
        "Duet": 900,
        "Trio": 1200,
        "Quartet": 1500,
        "Quintet": 1800,
        "Ensemble": 2100,
        "Composition": 600,
    },
}

DEFAULT_MOVE_TIME = {
    "None" : {
        "Solo": 300,
        "Recital": 300,
        "Duet": 300,
        "Trio": 300,
        "Quartet": 300,
        "Quintet": 300,
        "Ensemble": 300,
        "Composition": 300,
    },
    "Vocal" : {
        "Solo": 120,
        "Recital": 240,
        "Duet": 180,
        "Trio": 240,
        "Quartet": 300,
        "Quintet": 300,
        "Ensemble": 300,
        "Composition": 120,
    }, 
    "Piano": {
        "Solo": 120,
        "Recital": 240,
        "Duet": 180,
        "Trio": 240,
        "Quartet": 300,
        "Quintet": 300,
        "Ensemble": 300,
        "Composition": 120,
    },
    "Organ": {
        "Solo": 120,
        "Recital": 240,
        "Duet": 180,
        "Trio": 240,
        "Quartet": 300,
        "Quintet": 300,
        "Ensemble": 300,
        "Composition": 120,
    },
    "Strings": {
        "Solo": 120,
        "Recital": 240,
        "Duet": 180,
        "Trio": 240,
        "Quartet": 300,
        "Quintet": 300,
        "Ensemble": 300,
        "Composition": 120,
    },
    "Recorder": {
        "Solo": 120,
        "Recital": 240,
        "Duet": 180,
        "Trio": 240,
        "Quartet": 300,
        "Quintet": 300,
        "Ensemble": 300,
        "Composition": 120,
    },
    "Woodwinds": {
        "Solo": 120,
        "Recital": 240,
        "Duet": 180,
        "Trio": 240,
        "Quartet": 300,
        "Quintet": 300,
        "Ensemble": 300,
        "Composition": 120,
    },
    "Brass": {
        "Solo": 120,
        "Recital": 240,
        "Duet": 180,
        "Trio": 240,
        "Quartet": 300,
        "Quintet": 300,
        "Ensemble": 300,
        "Composition": 120,
    },
    "Percussion": {
        "Solo": 120,
        "Recital": 240,
        "Duet": 180,
        "Trio": 240,
        "Quartet": 300,
        "Quintet": 300,
        "Ensemble": 300,
        "Composition": 120,
    },
    "Instrumental": {
        "Solo": 120,
        "Recital": 240,
        "Duet": 180,
        "Trio": 240,
        "Quartet": 300,
        "Quintet": 300,
        "Ensemble": 300,
        "Composition": 120,
    },
    "Musical Theatre": {
        "Solo": 120,
        "Recital": 240,
        "Duet": 180,
        "Trio": 240,
        "Quartet": 300,
        "Quintet": 300,
        "Ensemble": 300,
        "Composition": 120,
    },
}

DEFAULT_FEE = {
    'Solo': Decimal('12.00'),
    'Recital': Decimal('16.00'),
    'Duet': Decimal('12.00'),
    'Trio': Decimal('12.00'),
    'Quartet': Decimal('14.00'),
    'Quintet': Decimal('14.00'),
    'Ensemble': Decimal('25.00'),
    'Composition': Decimal('14.00'),
    }

# DEFAULT_FEE = {
#     "None" : {
#        "Solo": 300,
#        "Recital": 300,
#        "Duet": 300,
#        "Trio": 300,
#        "Quartet": 300,
#        "Quintet": 300,
#        "Ensemble": 300,
#        "Composition": 300,
#    },
#    "Vocal" : {
#         "Solo": Decimal("12.00"),
#         "Recital": Decimal("16.00"),
#         "Duet": Decimal("12.00"),
#         "Trio": Decimal("12.00"),
#         "Quartet": Decimal("14.00"),
#         "Quintet": Decimal("14.00"),
#         "Ensemble": Decimal("25.00"),
#         "Composition": Decimal("14.00"),
#     }, 
#     "Piano": {
#         "Solo": Decimal("12.00"),
#         "Recital": Decimal("16.00"),
#         "Duet": Decimal("12.00"),
#         "Trio": Decimal("12.00"),
#         "Quartet": Decimal("14.00"),
#         "Quintet": Decimal("14.00"),
#         "Ensemble": Decimal("25.00"),
#         "Composition": Decimal("14.00"),
#     },
#     "Organ": {
#         "Solo": Decimal("12.00"),
#         "Recital": Decimal("16.00"),
#         "Duet": Decimal("12.00"),
#         "Trio": Decimal("12.00"),
#         "Quartet": Decimal("14.00"),
#         "Quintet": Decimal("14.00"),
#         "Ensemble": Decimal("25.00"),
#         "Composition": Decimal("14.00"),
#     },
#     "Strings": {
#         "Solo": Decimal("12.00"),
#         "Recital": Decimal("16.00"),
#         "Duet": Decimal("12.00"),
#         "Trio": Decimal("12.00"),
#         "Quartet": Decimal("14.00"),
#         "Quintet": Decimal("14.00"),
#         "Ensemble": Decimal("25.00"),
#         "Composition": Decimal("14.00"),
#     },
#     "Recorder": {
#         "Solo": Decimal("12.00"),
#         "Recital": Decimal("16.00"),
#         "Duet": Decimal("12.00"),
#         "Trio": Decimal("12.00"),
#         "Quartet": Decimal("14.00"),
#         "Quintet": Decimal("14.00"),
#         "Ensemble": Decimal("25.00"),
#         "Composition": Decimal("14.00"),
#     },
#     "Woodwinds": {
#         "Solo": Decimal("12.00"),
#         "Recital": Decimal("16.00"),
#         "Duet": Decimal("12.00"),
#         "Trio": Decimal("12.00"),
#         "Quartet": Decimal("14.00"),
#         "Quintet": Decimal("14.00"),
#         "Ensemble": Decimal("25.00"),
#         "Composition": Decimal("14.00"),
#     },
#     "Brass": {
#         "Solo": Decimal("12.00"),
#         "Recital": Decimal("16.00"),
#         "Duet": Decimal("12.00"),
#         "Trio": Decimal("12.00"),
#         "Quartet": Decimal("14.00"),
#         "Quintet": Decimal("14.00"),
#         "Ensemble": Decimal("25.00"),
#         "Composition": Decimal("14.00"),
#     },
#     "Percussion": {
#         "Solo": Decimal("12.00"),
#         "Recital": Decimal("16.00"),
#         "Duet": Decimal("12.00"),
#         "Trio": Decimal("12.00"),
#         "Quartet": Decimal("14.00"),
#         "Quintet": Decimal("14.00"),
#         "Ensemble": Decimal("25.00"),
#         "Composition": Decimal("14.00"),
#     },
#     "Instrumental": {
#         "Solo": Decimal("12.00"),
#         "Recital": Decimal("16.00"),
#         "Duet": Decimal("12.00"),
#         "Trio": Decimal("12.00"),
#         "Quartet": Decimal("14.00"),
#         "Quintet": Decimal("14.00"),
#         "Ensemble": Decimal("25.00"),
#         "Composition": Decimal("14.00"),
#     },
#     "Musical Theatre": {
#         "Solo": Decimal("12.00"),
#         "Recital": Decimal("16.00"),
#         "Duet": Decimal("12.00"),
#         "Trio": Decimal("12.00"),
#         "Quartet": Decimal("14.00"),
#         "Quintet": Decimal("14.00"),
#         "Ensemble": Decimal("25.00"),
#         "Composition": Decimal("14.00"),
#     },
# }

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

