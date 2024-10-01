# mfo/home/views.py

import flask
import flask_security
from sqlalchemy import select
from flask_security.utils import verify_and_update_password

from mfo.database.base import db
import mfo.database.users as users
from mfo.database.models import Profile
from mfo.database.users import Role, User
from mfo.account.forms.edit_profile import ProfileEdit
import mfo.database.utilities
from mfo.database.models import Festival, Season
from mfo.home.forms import ExtendedLoginForm

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

    if flask_security.current_user and flask_security.current_user.is_authenticated:
        if any('admin' in role.permissions for role in flask_security.current_user.roles):
            return flask.redirect(flask.url_for('admin.dashboard'))
        else:
            return flask.redirect(flask.url_for('home.dashboard'))

    return flask.render_template('/home/index.html')


@bp.get ('/dashboard')
@flask_security.auth_required()
def dashboard():
    return flask.render_template('/home/dashboard.html')


@bp.get('/new_user')
@flask_security.auth_required()
def new_user():
    role_name = "Participant"
    user = flask_security.current_user
    users.user_datastore.add_role_to_user(user, role_name)
    stmt = select(Role).where(Role.name == role_name)
    role = db.session.execute(stmt).scalars().first()

    primary_profile = Profile()
    primary_profile.email = user.email
    user, primary_profile = mfo.database.utilities.set_primary_profile(user, primary_profile)
    for role in user.roles:
        primary_profile.roles.append(role)

    primary_profile.users.append(user)

    db.session.add(primary_profile)
    db.session.commit()

    form = ProfileEdit(obj=primary_profile)

    return flask.render_template('/account/edit_profile.html', form=form)

@bp.get('/login')
def custom_login_get():
    form = ExtendedLoginForm(flask.request.form)
    return flask.render_template('security/login_user.html', login_user_form=form)

@bp.post('/login')
def custom_login_post():
    form = ExtendedLoginForm(flask.request.form)
    if form.validate():
        stmt = select(User).where(User.email == form.email.data)
        user = db.session.execute(stmt).scalars().first()
        
        if user and verify_and_update_password(form.password.data, user):
            # Check if the user has access to the specified Festival and Season
            stmt = select(Festival).where(Festival.name == form.festival.data)
            festival = db.session.execute(stmt).scalars().first()
            
            if festival:
                stmt = select(Season).where(
                    Season.name == form.season.data, 
                    Season.festival_id == festival.id
                    )
                season = db.session.execute(stmt).scalars().first()
                
                if season and user_has_access(user, festival, season):
                    flask_security.login_user(user, remember=form.remember.data)
                    return flask.redirect(flask.url_for('home.index'))
                else:
                    flask.flash('Invalid Season', 'error')
            else:
                flask.flash('Invalid Festival', 'error')
        else:
            flask.flash('Invalid email or password', 'error')
            return flask.render_template('security/login_user.html', login_user_form=form)
    
def user_has_access(user, festival, season):
    # Implement your logic to check if the user has access to the festival and season
    # For example, you might check if the user is associated with the festival and season
    return True  # Replace with actual access check logic
