# mfo/app.py

import flask
from flask_security import Security

import mfo.home.views
import mfo.admin.views
import mfo.database.users as users
import mfo.database.commands
import mfo.database.base as base

def create_app():

    # Create app object
    app = flask.Flask(__name__)

    # Configure the app
    app.config.from_pyfile('config.py')

    # Register Flask-SQLAlchemy
    base.db.init_app(app)

    # Register Flask-Security-Too
    app.security = Security(app, users.user_datastore)

    # Register blueprints
    app.register_blueprint(mfo.home.views.bp)
    app.register_blueprint(mfo.admin.views.bp)
    app.register_blueprint(mfo.database.commands.bp)

    return app
