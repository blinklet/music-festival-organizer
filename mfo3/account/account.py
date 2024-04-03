import flask

bp = flask.Blueprint(
    'account',
    __name__,
    static_folder='static/account',
    template_folder='templates/account',
    url_prefix='/account',
    )

@bp.route('/')
def index():
    return flask.render_template('/index.html')

@bp.route('/login')
def login():
    return flask.render_template('/login.html')

@bp.route('/register')
def register():
    return flask.render_template('/register.html')