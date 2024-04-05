# Flask APP configuration file
import os
import dotenv


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
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO")


# Flask-Session variables
SESSION_TYPE = os.environ.get("SESSION_TYPE")
SESSION_PERMANENT = os.environ.get("SESSION_PERMANENT")
SESSION_KEY_PREFIX = os.environ.get("SESSION_KEY_PREFIX")
SESSION_SQLALCHEMY = os.environ.get("SESSION_SQLALCHEMY")