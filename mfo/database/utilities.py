# mfo/database/utilities.py

import flask
from sqlalchemy import select

from mfo.database.base import db
from mfo.database.models import Festival

def find_primary_profile(user):
    return user.primary_profile

def find_primary_user(profile):
    return profile.user if profile.primary else None

def set_primary_profile(user, profile):
    # Unset the current primary profile if it exists
    if user.primary_profile:
        user.primary_profile.primary = False
    
    # Set the new primary profile
    profile.primary = True
    user.primary_profile = profile
    user.primary_profile_id = profile.id

    return user, profile

def get_current_festival():
    festival_id = flask.session.get('current_festival')
    stmt = select(Festival).where(Festival.id == festival_id)
    festival = db.session.execute(stmt).scalars().one_or_none()
    return festival