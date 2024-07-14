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
def index():
    if '_flashes' in flask.session:
        flask.session['_flashes'].clear()
    return flask.render_template('/home/index.html')
