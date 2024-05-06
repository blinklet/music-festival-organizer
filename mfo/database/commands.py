# mfo/database.commands.py

import flask
import flask_security
import click

import mfo.database.base as base


bp = flask.Blueprint('database', __name__,)

@bp.cli.command('create')
@flask.cli.with_appcontext
def create():
    base.db.create_all()