# mfo/app.py
import flask
from flask_security import Security
from mfo.database import setup
from mfo.database.base import db
from mfo.database.users import user_datastore
from flask_security.signals import user_registered
from flask_bootstrap import Bootstrap5


app = flask.Flask(__name__)
app.config.from_pyfile('config.py', silent=True)

# Register Bootstrap-Flask
bootstrap = Bootstrap5(app)

# Register Flask-SQLAlchemy
db.init_app(app)

# Register Flask-Security-Too
app.security = Security(app, user_datastore)

# Register blueprints
from mfo.admin import admin
from mfo.home import home
from mfo.account import account
app.register_blueprint(home.bp)
app.register_blueprint(account.bp)
app.register_blueprint(admin.bp)

# Create application database, if one does not exist
with app.app_context():
    setup.create_database(flask.current_app)
    setup.create_roles(flask.current_app)
    setup.create_superuser(flask.current_app)


# Assign "User" role to all newly-registered users
@user_registered.connect_via(app)
def user_registered_sighandler(sender, user, **extra):
    role = "Participant"
    user_datastore.add_role_to_user(user, role)

if __name__ == "__main__":
    app.run()