# mfo/app.py

import flask

from flask_security import Security

from mfo.database.setup import db, create_database
from mfo.database.models.users import User, Role
from flask_security import Security, SQLAlchemyUserDatastore


app = flask.Flask(__name__)
app.config.from_pyfile('config.py', silent=True)

# Configure Flask-SQLAlchemy
db.init_app(app)

# Configure Flask_Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
app.security = Security(app, user_datastore)

# Register blueprints
from mfo.admin import admin
from mfo.home import home
# from mfo.account import account
app.register_blueprint(home.bp)
# app.register_blueprint(account.bp)
app.register_blueprint(admin.bp)

# Create application database, if one does not exist
with app.app_context():
    create_database()






if __name__ == "__main__":
    print("MAIN")
    app.run()