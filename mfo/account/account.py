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


