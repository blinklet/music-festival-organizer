# mfo/admin/views.py

import flask
import flask_security
import mfo.admin.forms
from werkzeug.exceptions import Forbidden
from werkzeug.utils import secure_filename
import os
import io
import pandas as pd

bp = flask.Blueprint(
    'admin',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/admin',
    )


@bp.route('/', methods=['GET', 'POST'])
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def index():
    form = mfo.admin.forms.UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(io.StringIO(file.stream.read().decode("utf-8")))
            elif file.filename.endswith('.ods'):
                print('READING?')
                df = pd.read_excel(file, engine='odf')
                print('READING DONE?')
            else:
                flask.flash('Unsupported file format', 'danger')
                return flask.redirect(flask.url_for('admin.index'))

            # Display the first few rows of the dataframe as a flash message
            flask.flash(f'File uploaded successfully. Here are the first few rows:\n{df.head()}', 'success')
        except Exception as e:
            flask.flash(f'Error reading file: {e}', 'danger')

            return flask.redirect(flask.url_for('admin.index'))
        
            
        print('DONE?')
        print(df.columns.values)
        return flask.redirect(flask.url_for('admin.index'))

    return flask.render_template('/admin/index.html', form=form)

@bp.errorhandler(Forbidden)
def handle_forbidden(e):
    return flask.render_template('forbidden.html', role="Admin")