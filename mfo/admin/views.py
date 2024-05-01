# admin/views.py

import flask

bp = flask.Blueprint(
    'admin',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/admin',
    )

@bp.route('/')
def index():
    return flask.render_template('/admin/index.html')
