# mfo/app.py

import flask
from flask_security import Security
from flask_bootstrap import Bootstrap5
from flask_security.signals import user_registered
import flask_session

import mfo.database.users as users
import mfo.database.base as base
from mfo.database.models import Profile

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

    # Register Flask-Session
    flask_session.Session(app)

    # Register blueprints
    import mfo.home.views
    import mfo.admin.views
    import mfo.account.views
    import mfo.database.commands
    app.register_blueprint(mfo.home.views.bp)
    app.register_blueprint(mfo.admin.views.bp)
    app.register_blueprint(mfo.account.views.bp)
    app.register_blueprint(mfo.database.commands.bp)

    # Assign "User" role to all newly-registered users
    # And create primary profile for each new user
    @user_registered.connect_via(app)
    def user_registered_sighandler(sender, user, **extra):
        role = "Participant"
        users.user_datastore.add_role_to_user(user, role)
        profile = Profile(email=user.email)
        profile.users.append(user)
        base.db.session.add(profile)
        base.db.session.commit()

    return app
