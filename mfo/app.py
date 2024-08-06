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

    # Define helper functions
    def update_sort(column, sort_by, sort_order):
        if column in sort_by:
            # Move the existing column to the end of the list
            sort_by.remove(column)
            sort_by.append(column)
        else:
            # Or, add the new column to the end of the list
            sort_by.append(column)
        return sort_by

    def update_order(column, sort_by, sort_order):
        if column in sort_by:
            # If column altready exists in sort_by list,
            # find its corresponding sort_order value,
            # reverse it, and move it to the end of the list
            index = sort_by.index(column)
            order = sort_order.pop(index)
            if order == 'asc':
                sort_order.append('desc')
            else:
                sort_order.append('asc')
        else:
            # Or, add the sort_order value for the new column 
            # to the end of the list
            sort_order.append('asc')
        return sort_order

    # Add helper functions to Jinja2 environment
    app.jinja_env.globals.update(update_sort=update_sort)
    app.jinja_env.globals.update(update_order=update_order)

    return app


