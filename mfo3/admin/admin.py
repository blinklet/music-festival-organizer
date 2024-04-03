import flask

bp = flask.Blueprint(
    'admin',
    __name__,
    static_folder='static/admin',
    template_folder='templates/admin',
    url_prefix='/',
    )

@bp.route('/')
def index():
    return flask.render_template('/home/index.html')