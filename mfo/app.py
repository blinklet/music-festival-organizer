# mfo/app.py

import flask

from flask_security import Security

from mfo.database.setup import db
from mfo.database.models.users import user_datastore
from mfo.admin import admin
from mfo.home import home
from mfo.account import account
from flask_security import Security, current_user, auth_required, hash_password, \
     SQLAlchemySessionUserDatastore, permissions_accepted


app = flask.Flask(__name__)
app.config.from_pyfile('config.py', silent=True)

# Configure Flask extensions
db.init_app(app)
app.security = Security(app, user_datastore)
with app.app_context():
    db.create_all()
    if not app.security.datastore.find_user(email="test@me.com"):
        app.security.datastore.create_user(email="test@me.com", password=hash_password("password"))
    db.session.commit()



# Register blueprints
app.register_blueprint(home.bp)
app.register_blueprint(account.bp)
app.register_blueprint(admin.bp)


if __name__ == "__main__":
    app.run()