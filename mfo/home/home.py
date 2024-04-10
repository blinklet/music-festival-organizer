import flask
from flask_security import current_user

bp = flask.Blueprint(
    'home',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/',
    )

@bp.route('/')
def index():
    return flask.render_template('/home/index.html')