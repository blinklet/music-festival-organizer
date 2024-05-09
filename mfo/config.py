# mfo/config.py

import os
import dotenv

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

# Roles defined
ROLES  = {
    'USER': {
        'name': 'User',
        'description': 'Normal users',
        'permissions': { 'read', 'write' }
    },
    'ADMIN': {
        'name': 'Admin',
        'description': 'Administrators',
        'permissions': { 'read', 'write', 'database' }
    },
}