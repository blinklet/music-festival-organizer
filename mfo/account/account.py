import flask
from flask_security import auth_required


bp = flask.Blueprint(
    'account',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/account',
    )


@bp.route('/')
@auth_required()
def index():
    return flask.render_template('/account/index.html')

@bp.route('/login')
@auth_required()
def login():
    return flask.render_template('/account/login.html')

@bp.route('/register')
@auth_required()
def register():
    return flask.render_template('/account/register.html')