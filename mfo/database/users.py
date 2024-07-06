from flask_security.models import fsqla_v3 as fsqla
from flask_security import SQLAlchemyUserDatastore
from mfo.database.base import db
from sqlalchemy.orm import Mapped, relationship

from .models import profiles_users, profiles_roles

fsqla.FsModels.set_db_info(db)

class Role(db.Model, fsqla.FsRoleMixin):
    profiles: Mapped[list["Profile"]] = relationship(
        secondary=profiles_roles, back_populates="roles"
    )

class User(db.Model, fsqla.FsUserMixin):
    profiles: Mapped[list["Profile"]] = relationship(
        secondary=profiles_users, back_populates="users"
    )

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
