from flask_security.models import fsqla_v3 as fsqla
from flask_security import SQLAlchemyUserDatastore
from mfo.database.base import db
from sqlalchemy.orm import Mapped, relationship

from .profiles import profiles_users

fsqla.FsModels.set_db_info(db)

class Role(db.Model, fsqla.FsRoleMixin):
    pass

class User(db.Model, fsqla.FsUserMixin):
    profiles: Mapped[list["Profile"]] = relationship(
    secondary=profiles_users, back_populates="users"
)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
