import flask
from flask_security import roles_required
from werkzeug.exceptions import Forbidden

bp = flask.Blueprint(
    'admin',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/admin',
    )


@bp.route('/')
@roles_required('Admin')
def index():
    return flask.render_template('/admin/index.html')

@bp.errorhandler(Forbidden)
def handle_forbidden(e):
    return flask.render_template('forbidden.html', role="Admin")