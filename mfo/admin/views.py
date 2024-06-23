# mfo/admin/views.py

import flask
import flask_security
import mfo.admin.forms
from werkzeug.exceptions import Forbidden
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import pandas as pd
import os

from mfo.database.base import db
import mfo.admin.services.spreadsheet as spreadsheet

bp = flask.Blueprint(
    'admin',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/admin',
    )


@bp.get('/')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def index_get():
    form = mfo.admin.forms.UploadForm()
    return flask.render_template('admin/index.html', form=form)


@bp.post('/')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def index_post():
    form = mfo.admin.forms.UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        df, succeeded, message = spreadsheet.read_sheet(file)

        if not succeeded:
            flask.flash(message, 'danger')
            return flask.redirect(flask.url_for('admin.index_get'))

        flask.flash(message, 'success')

        spreadsheet.convert_to_db(df)
        
        return flask.render_template('admin/index.html', form=form)
    

@bp.route('/confirm', methods=['POST'])
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def confirm():
    form = mfo.admin.forms.ConfirmForm()
    if form.validate_on_submit():
        if form.confirm.data:
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flask.flash("Commit failed due to integrity error.", 'danger')
            except SQLAlchemyError as e:
                db.session.rollback()
                flask.flash(f"Commit failed due to error: {e}", 'danger')
            else:
                flask.flash("Changes committed to the database.", 'success')

        elif form.cancel.data:
            db.session.rollback()  # Roll back any uncommitted changes
            flask.flash("Changes were not committed to the database.", 'warning')
        else:
            flask.flash("Changes were not committed to the database.", 'danger')
    
    return flask.redirect(flask.url_for('admin.index'))


@bp.errorhandler(Forbidden)
def handle_forbidden(e):
    return flask.render_template('forbidden.html', role="Admin")