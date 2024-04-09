from mfo.database.setup import db
from sqlalchemy.orm import Mapped, mapped_column
from flask_security.models import fsqla_v3 as fsqla
from flask_security import SQLAlchemyUserDatastore

# class User(db.Model):
#     __tablename__ = "users"
#     email: Mapped[str] = mapped_column(primary_key=True)
#     first_name: Mapped[str]
#     last_name: Mapped[str]

#     def __repr__(self):
#         return f'<{self.email} {self.first_name} {self.last_name}>'


fsqla.FsModels.set_db_info(db)

class Role(db.Model, fsqla.FsRoleMixin):
    pass

class User(db.Model, fsqla.FsUserMixin):
    pass

user_datastore = SQLAlchemyUserDatastore(db, User, Role)