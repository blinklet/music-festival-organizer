from flask_security.models import fsqla_v3 as fsqla
from flask_security import SQLAlchemyUserDatastore, UserMixin
from mfo.database.base import db
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, relationship, mapped_column
from typing import List, Optional

from mfo.database.models import Profile, profiles_users, profiles_roles, UserFestivalsRoles
from mfo.database.utilities import get_current_festival

fsqla.FsModels.set_db_info(db)

class CustomUserMixin(UserMixin):
    @property
    def roles(self):
        festival = get_current_festival()  # Implement this function to get the current festival
        return user_datastore.get_user_roles(self, festival)

    @property
    def role_names(self):
        festival = get_current_festival()  # Implement this function to get the current festival
        return user_datastore.get_user_role_names(self, festival)
    

class Role(db.Model, fsqla.FsRoleMixin):
    profiles: Mapped[list["Profile"]] = relationship(
        secondary=profiles_roles, 
        back_populates="roles"
    )
    users_festivals: Mapped[List["UserFestivalsRoles"]] = relationship(
        'UserFestivalsRoles',
        back_populates='role'
    )


class User(db.Model, fsqla.FsUserMixin, CustomUserMixin):
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

    
class CustomSQLAlchemyUserDatastore(SQLAlchemyUserDatastore):
    def add_role_to_user(self, user, role, festival):
        association = UserFestivalsRoles(user=user, role=role, festival=festival)
        db.session.add(association)
        db.session.commit()

    def remove_role_from_user(self, user, role, festival):
        stmt = select(UserFestivalsRoles).where(
            UserFestivalsRoles.user == user,
            UserFestivalsRoles.role == role,
            UserFestivalsRoles.festival == festival
        )
        association = db.session.execute(stmt).scalars().one_or_none()
        if association:
            db.session.delete(association)
            db.session.commit()

    def get_user_roles(self, user, festival):
        stmt = select(Role).join(UserFestivalsRoles).where(
            UserFestivalsRoles.user_id == user.id,
            UserFestivalsRoles.festival_id == festival.id,
            UserFestivalsRoles.role_id == Role.id
        )
        roles = db.session.execute(stmt).scalars().all()
        return roles
    
    def get_user_role_names(self, user, festival):
        roles = self.get_user_roles(user, festival)
        role_names = [role.name for role in roles]
        return role_names


user_datastore = CustomSQLAlchemyUserDatastore(db, User, Role)