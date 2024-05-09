# mfo/database.commands.py

import flask

import mfo.database.base as base


bp = flask.Blueprint('database', __name__,)

@bp.cli.command('create')
@flask.cli.with_appcontext
def create():
    base.db.create_all()

    roles_dict = flask.current_app.config['ROLES']
    roles_keys = roles_dict.keys()
    for key in roles_keys:
        role=roles_dict[key]
        flask.current_app.security.datastore.find_or_create_role(
            name=role['name'], 
            description=role['description'],
            permissions=role['permissions'],
    )
    flask.current_app.security.datastore.commit()