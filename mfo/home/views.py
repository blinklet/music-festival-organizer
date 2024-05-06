# mfo/home/views.py

import flask
import flask_security

bp = flask.Blueprint(
    'home',
    __name__,
    static_folder='static',
    template_folder='templates',
    static_url_path='/home/static',
    url_prefix='/'
    )


@bp.route('/')
@flask_security.auth_required()
def index():
    return flask.render_template('/home/index.html')
