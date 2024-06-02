# mfo/admin/views.py

import flask
import flask_security
import mfo.admin.forms
from werkzeug.exceptions import Forbidden
from werkzeug.utils import secure_filename

import mfo.admin.spreadsheet as spreadsheet

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
        df, succeeded, message = spreadsheet.read_sheet(file)

        if not succeeded:
            flask.flash(message, 'danger')
            return flask.redirect(flask.url_for('admin.index'))

        flask.flash(message, 'success')
        spreadsheet.convert_to_db(df)
        return flask.redirect(flask.url_for('admin.index'))

    return flask.render_template('/admin/index.html', form=form)
    

@bp.errorhandler(Forbidden)
def handle_forbidden(e):
    return flask.render_template('forbidden.html', role="Admin")