# mfo/app.py

import flask
from flask_security import Security
from flask_bootstrap import Bootstrap5

import mfo.database.users as users
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

    # Register Bootstrap-Flask
    bootstrap = Bootstrap5()
    bootstrap.init_app(app)

    # Register blueprints
    import mfo.home.views
    import mfo.admin.views
    import mfo.database.commands
    app.register_blueprint(mfo.home.views.bp)
    app.register_blueprint(mfo.admin.views.bp)
    app.register_blueprint(mfo.database.commands.bp)

    return app
