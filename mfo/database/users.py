from flask_security.models import fsqla_v3 as fsqla
from flask_security import SQLAlchemyUserDatastore
from mfo.database.base import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from typing import List, Optional

from mfo.database.models import Profile, profiles_users, profiles_roles, UserFestivalsRoles

fsqla.FsModels.set_db_info(db)

class Role(db.Model, fsqla.FsRoleMixin):
    profiles: Mapped[list["Profile"]] = relationship(
        secondary=profiles_roles, 
        back_populates="roles"
    )
    users_festivals: Mapped[List["UserFestivalsRoles"]] = relationship(
        'UserFestivalsRoles',
        back_populates='role'
    )

class User(db.Model, fsqla.FsUserMixin):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    primary_profile_id: Mapped[Optional[int]] = mapped_column(ForeignKey('profile.id'), nullable=True)

    primary_profile: Mapped[Optional["Profile"]] = relationship(
        "Profile", 
        uselist=False, 
        foreign_keys=[primary_profile_id]
    )
    profiles: Mapped[list["Profile"]] = relationship(
        secondary=profiles_users, 
        back_populates="users"
    )
    roles_festivals: Mapped[List["UserFestivalsRoles"]] = relationship(
        'UserFestivalsRoles',
        back_populates='user'
    )

    

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
