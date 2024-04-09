import flask
from mfo.database.models.users import User
from mfo.database.setup import db
from mfo.home import home
from flask_security import Security, current_user, auth_required, hash_password, \
     SQLAlchemySessionUserDatastore, permissions_accepted

bp = flask.Blueprint(
    'home',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/',
    )

@bp.route('/')
@auth_required()
def index():
    return flask.render_template('/home/index.html', name=current_user.email)

@bp.route('/test/<email>/<first>/<last>')
def test(email, first, last):

    user1 = User()
    user1.email = email
    user1.first_name = first
    user1.last_name = last
    db.session.add(user1)
    db.session.commit()

    users = db.session.execute(db.select(User))
    print("Users")
    print(users)

    return flask.redirect(flask.url_for('home.index'))