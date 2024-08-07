# mfo/account/views.py

import flask

from mfo.database.base import db
import mfo.database.utilities
import flask_security
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from mfo.account.forms.edit_profile import ProfileEdit
from mfo.database.users import Role
from mfo.database.models import Profile

bp = flask.Blueprint(
    'account',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/account',
    )

@bp.get('/')
@flask_security.auth_required()
def index():
    user = flask_security.current_user
    primary_profile = mfo.database.utilities.find_primary_profile(user)

    # Eagerly load the profile with its roles so they are available to the template context
    stmt = select(Profile).options(selectinload(Profile.roles)).filter_by(id=primary_profile.id)
    primary_profile = db.session.execute(stmt).scalar_one_or_none()

    return flask.render_template('/account/index.html', user=user, profile=primary_profile)

@bp.post('/edit_profile')
@flask_security.auth_required()
def edit_profile_post():
    user = flask_security.current_user
    profile = mfo.database.utilities.find_primary_profile(user)
    
    profile.rolenames = [role.name for role in profile.roles]
    form = ProfileEdit(obj=profile)

    if form.validate_on_submit():
        profile.name = form.name.data
        profile.birthdate = form.birthdate.data if form.birthdate.data else None
        profile.address = form.address.data if form.address.data else None
        profile.city = form.city.data if form.city.data else None
        profile.province = form.province.data if form.province.data else None
        profile.postal_code = form.postal_code.data if form.postal_code.data else None
        profile.phone = form.phone.data if form.phone.data else None
        profile.school = form.school.data if form.school.data else None
        profile.teacher = form.teacher.data if form.teacher.data else None
        profile.comments = form.comments.data if form.comments.data else None
        profile.national_festival = form.national_festival.data if form.national_festival.data else None

        # Get all role names except admin
        stmt = select(Role).where(Role.name != 'Admin')
        all_roles = db.session.execute(stmt).scalars().all()
        all_role_names = {role.name for role in all_roles}

        selected_role_names = set(form.rolenames.data)

        # Remove unselected roles from profile
        for role in all_roles:
            if role.name not in selected_role_names:
                if role in profile.roles:
                    profile.roles.remove(role)
                if role in user.roles: 
                    user.roles.remove(role)

        # add new selected roles to profile   
        for selected_role in selected_role_names:
            # Only allow Admin users to add Admin role
            if selected_role == 'Admin' and 'Admin' not in user.roles:
                print(f'#### ERROR!! User {user.email} tried to add Admin role')
                continue
            # Only a role if it is not already in the profile
            stmt = select(Role).where(Role.name==selected_role)
            role = db.session.execute(stmt).scalars().first()
            if role not in profile.roles:
                profile.roles.append(role)
            # Also add roles to user because I do not have the
            # automatic cascading set up
            if role not in user.roles:
                user.roles.append(role)

        db.session.commit()
        return flask.redirect(flask.url_for('account.index'))
    
    return flask.render_template('/account/edit_profile.html', form=form)


@bp.get('/edit_profile')
@flask_security.auth_required()
def edit_profile_get():
    user = flask_security.current_user
    profile = mfo.database.utilities.find_primary_profile(user)
    if profile is None:
        profile = Profile()
        profile.id = user.id
        profile.email = user.email
        for role in user.roles:
            profile.roles.append(role)
        db.session.add(profile)
        db.session.commit()
    profile.rolenames = [role.name for role in profile.roles]
    form = ProfileEdit(obj=profile)
    return flask.render_template('/account/edit_profile.html', form=form)