# mfo/app.py

import flask

from flask_security import Security

from mfo.database.setup import db
from mfo.database.models.users import user_datastore
from mfo.admin import admin
from mfo.home import home
from mfo.account import account


app = flask.Flask(__name__)
app.config.from_pyfile('config.py', silent=True)

# Configure Flask extensions
db.init_app(app)

with app.app_context():
    db.create_all()

app.security = Security(app, user_datastore)

# Register blueprints
app.register_blueprint(home.bp)
app.register_blueprint(account.bp)
app.register_blueprint(admin.bp)


if __name__ == "__main__":
    app.run()