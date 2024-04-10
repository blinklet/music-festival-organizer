# Flask APP configuration file
import os
import dotenv

app_dir = os.path.abspath(os.path.dirname(__file__))
project_dir, _unused = os.path.split(app_dir)

# Load variables from `.env` file, if it exists
# basedir = os.path.abspath(os.path.dirname(__file__))
# dotenv.load_dotenv(os.path.join(basedir, ".env"))
dotenv.load_dotenv()

# General Config
ENVIRONMENT = os.environ.get("FLASK_ENVIRONMENT")
DEBUG = os.environ.get("FLASK_DEBUG")
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
SERVER_NAME = os.environ.get("FLASK_SERVER_NAME")
EXPLAIN_TEMPLATE_LOADING = os.environ.get("FLASK_EXPLAIN_TEMPLATE_LOADING")

# Flask-SQLAlchemy variables
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")\
     or 'sqlite:///' + os.path.join(project_dir, 'app.sqlite')
SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO")
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

# Flask-Security variables
SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT")
SECURITY_ANONYMOUS_USER_DISABLED = True # See: https://flask-security-too.readthedocs.io/en/stable/changelog.html#notes
SECURITY_REGISTERABLE = True

# Flask-Session variables
SESSION_TYPE = os.environ.get("SESSION_TYPE")
SESSION_PERMANENT = os.environ.get("SESSION_PERMANENT")
SESSION_KEY_PREFIX = os.environ.get("SESSION_KEY_PREFIX")
SESSION_SQLALCHEMY = os.environ.get("SESSION_SQLALCHEMY")
REMEMBER_COOKIE_SAMESITE = "strict"
SESSION_COOKIE_SAMESITE = "strict"