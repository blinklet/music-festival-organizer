# mfo/admin/views.py

import flask
import flask_security
from werkzeug.exceptions import Forbidden

bp = flask.Blueprint(
    'admin',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/admin',
    )

@bp.route('/')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def index():
    return flask.render_template('/admin/index.html')

@bp.errorhandler(Forbidden)
def handle_forbidden(e):
    return flask.render_template('forbidden.html', role="Admin")