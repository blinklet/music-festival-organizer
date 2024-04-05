import flask

bp = flask.Blueprint(
    'account',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/account',
    )

@bp.route('/')
def index():
    return flask.render_template('/account/index.html')

@bp.route('/login')
def login():
    return flask.render_template('/account/login.html')

@bp.route('/register')
def register():
    return flask.render_template('/account/register.html')