from mfo.database.setup import db
from flask_security.models import fsqla_v3 as fsqla
from flask_security import SQLAlchemyUserDatastore

fsqla.FsModels.set_db_info(db)

class Role(db.Model, fsqla.FsRoleMixin):
    pass

class User(db.Model, fsqla.FsUserMixin):
    pass

user_datastore = SQLAlchemyUserDatastore(db, User, Role)