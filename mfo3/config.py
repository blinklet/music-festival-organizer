from dotenv import load_dotenv
import os

if os.path.isfile(".env"):
    load_dotenv()
else:
    load_dotenv("dotenv.example")

database_server = os.getenv('DB_SERVER')
database_name = os.getenv('DB_NAME')
database_userid = os.getenv('DB_UID')
database_password = os.getenv('DB_PWD')
app_testing = os.getenv('TESTING')
app_debug = os.getenv('DEBUG')


class Config(object):
    TESTING = False

class ProductionConfig(Config):
    DATABASE_URI = 'mysql://user@localhost/foo'

class DevelopmentConfig(Config):
    DATABASE_URI = "sqlite:////tmp/foo.db"
    DEBUG = True
    SECRET_KEY = 'fake-key'

class TestingConfig(Config):
    DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True