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
from mfo.home.utilities import get_identity_attributes

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
        festival = mfo.database.utilities.get_current_festival()

        if festival is None:
            flask.flash('No active festival', 'danger')
            return flask.redirect(flask.url_for('home.custom_login_get'))

        festival_users = [ufr.user for ufr in festival.roles_users]
        if flask_security.current_user not in festival_users:
            flask.flash('User not registered with festival', 'danger')
            return flask.redirect(flask.url_for('home.custom_login_get'))

        user_role_names = flask_security.current_user.role_names

        if 'Admin' in user_role_names:
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

@bp.get('/clogin')
def custom_login_get():
    form = ExtendedLoginForm()

    identity_attributes = get_identity_attributes()
    # if festival_nickname:
    #     stmt = select(Festival).where(Festival.nickname.ilike(festival_nickname))
    #     festival = db.session.execute(stmt).scalars().first()
    #     if festival:
    #         form.festival.data = festival.name
    #     else:
    #         flask.flash('Invalid Festival', 'danger')

    return flask.render_template(
        'security/custom_login_user.html', 
        identity_attributes=identity_attributes, 
        login_user_form=form
    )

@bp.post('/clogin')
def custom_login_post():
    form = ExtendedLoginForm()
    identity_attributes = get_identity_attributes()

    if form.validate():
        stmt = select(User).where(User.email == form.email.data)
        user = db.session.execute(stmt).scalars().first()

        if not user:
            flask.flash('Invalid email or password', 'error')
            return flask.render_template(
                'security/custom_login_user.html', 
                identity_attributes=identity_attributes,
                login_user_form=form
            )
        
        # Check if the user is associated with the selected festival
        festival_name = form.festival.data
        stmt = select(Festival).where(Festival.name == festival_name)
        festival = db.session.execute(stmt).scalars().one_or_none()

        if not festival:
            flask.flash('Invalid Festival', 'error')
            return flask.render_template(
                'security/custom_login_user.html', 
                identity_attributes=identity_attributes,
                login_user_form=form
            )

        user_festivals = [ufr.festival.name for ufr in user.roles_festivals]
        print(user_festivals)
        if festival.name not in user_festivals:
            flask.flash(f'User is not associated with {festival.name}', 'error')
            return flask.render_template(
                'security/custom_login_user.html', 
                identity_attributes=identity_attributes,
                login_user_form=form
            )

        success = flask_security.login_user(user, authn_via=["password"], remember=form.remember.data)
        print(f"****  {success}  ****************************************")
        if success:
            flask.session['current_festival'] = festival.id  # Store festival ID in session for future use
            # print(f"User: {flask_security.current_user.email}")
            # print(festival_name)
            # print(f"Festival: {flask.session['festival_id']}")
            return flask.redirect(flask.url_for('home.index'))
        else:
            flask.flash('Invalid email or password', 'error')
            return flask.render_template(
                'security/custom_login_user.html', 
                identity_attributes=identity_attributes,
                login_user_form=form
            )
    else:
        flask.flash('Invalid email or password validation', 'error')
        return flask.render_template(
                'security/custom_login_user.html', 
                identity_attributes=identity_attributes,
                login_user_form=form
            )

        
        # if user and verify_and_update_password(form.password.data, user):
        #     # Check if the user has access to the specified Festival and Season
        #     stmt = select(Festival).where(Festival.name == form.festival.data)
        #     festival = db.session.execute(stmt).scalars().first()
            
        #     if festival:
        #         stmt = select(Season).where(
        #             Season.primary == True, 
        #             Season.festival_id == festival.id
        #             )
        #         season = db.session.execute(stmt).scalars().first()
        #         print(f'Season: {season.name}')
                
        #         if season and user_has_access(user, festival, season):
        #             flask_security.login_user(user, remember=form.remember.data)
        #             return flask.redirect(flask.url_for('home.index'))
        #         else:
        #             flask.flash('No active season', 'error')
        #     else:
        #         flask.flash('Invalid Festival', 'error')
        #         return flask.render_template('security/login_user.html', login_user_form=form)
        # else:
        #     flask.flash('Invalid email or password', 'error')
        #     return flask.render_template('security/login_user.html', login_user_form=form)
    
def user_has_access(user, festival, season):
    # Implement your logic to check if the user has access to the festival 
    return True  # Replace with actual access check logic
