# mfo/database/setup.py
 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask import current_app

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create database, if none 
def create_database():
    with current_app.app_context():
        security = current_app.security
        security.datastore.db.create_all()