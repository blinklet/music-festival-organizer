# mfo/home/views.py

import flask

bp = flask.Blueprint(
    'home',
    __name__,
    static_folder='static',
    template_folder='templates',
    static_url_path='/home/static',
    url_prefix='/'
    )

@bp.route('/')
def index():
    return flask.render_template('/home/index.html')
