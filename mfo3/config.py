# Flask APP configuration file
import os
import dotenv


# Load variables from `.env` file, if it exists
basedir = os.path.abspath(os.path.dirname(__file__))
dotenv.load_dotenv(os.path.join(basedir, ".env"))


# General Config
# 
ENVIRONMENT = os.environ.get("ENVIRONMENT")
FLASK_APP = os.environ.get("FLASK_APP")
FLASK_DEBUG = os.environ.get("FLASK_DEBUG")
SECRET_KEY = os.environ.get("SECRET_KEY")
SERVER_NAME = os.environ.get("SERVER_NAME")

# Flask-SQLAlchemy variables
# The connection string of the app's database.
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
# Print database-related actions to the console for debugging purposes.
SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO")


# Flask-Session variables
# Session information can be handled via Redis, Memcached, filesystem, MongoDB, or SQLAlchemy.
SESSION_TYPE = os.environ.get("SESSION_TYPE")
# A True/False value that states whether or not user sessions should last forever.
SESSION_PERMANENT = os.environ.get("SESSION_PERMANENT")
# Modifies the key names in session key/value pairs to always have a particular prefix.
SESSION_KEY_PREFIX = os.environ.get("SESSION_KEY_PREFIX")
# URI of a database to store session information.
SESSION_SQLALCHEMY = os.environ.get("SESSION_SQLALCHEMY")