# mfo/home/views.py

import flask
import flask_security
from sqlalchemy import select

import mfo.database.users as users
import mfo.database.base as base
from mfo.database.models import Profile
from mfo.database.users import Role
from mfo.account.forms.edit_profile import ProfileEdit

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

@bp.get('/new_user')
@flask_security.auth_required()
def new_user():
    role_name = "Participant"
    user = flask_security.current_user
    users.user_datastore.add_role_to_user(user, role_name)
    stmt = select(Role).where(Role.name == role_name)
    role = base.db.session.execute(stmt).scalars().first()
    profile = Profile(email=user.email)
    profile.users.append(user)
    profile.roles.append(role)
    base.db.session.add(profile)
    base.db.session.commit()
    form = ProfileEdit(obj=profile)
    return flask.render_template('/account/edit_profile.html', form=form)
