# mfo/admin/services/data_services.py

from werkzeug.exceptions import Forbidden
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select

from mfo.database.base import db
from mfo.database.models import Profile, FestivalClass


def get_profiles(profile_type, sort_by=None):
    if sort_by == 'name':
        stmt = select(Profile).where(Profile.roles.any(name=profile_type)).order_by(Profile.name, Profile.email)
    elif sort_by == 'email':
        stmt = select(Profile).where(Profile.roles.any(name=profile_type)).order_by(Profile.email, Profile.name)
    else:
        stmt = select(Profile).where(Profile.roles.any(name=profile_type))
    return db.session.execute(stmt).scalars().all()