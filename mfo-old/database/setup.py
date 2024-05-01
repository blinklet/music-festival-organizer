# mfo/database/setup.py
 
from flask_security import hash_password
from mfo.database.base import db

# Create database, if none 
def create_database(app):
    security = app.security
    security.datastore.db.create_all()

# Create roles in database
def create_roles(app):
    roles_dict = app.config['ROLES']
    roles_keys = roles_dict.keys()
    for key in roles_keys:
        role=roles_dict[key]
        app.security.datastore.find_or_create_role(
            name=role['name'], 
            description=role['description'],
            permissions=role['permissions']
    )
    app.security.datastore.commit()


# Create first admin user
# Run this _after_ roles created in database
def create_superuser(app):
    if app.security.datastore.find_user(email=app.config['SUPERUSER_EMAIL']):
        print('### Superuser already configured ###')
    else:
        app.security.datastore.create_user(
            email=app.config['SUPERUSER_EMAIL'],
            password=hash_password(app.config['SUPERUSER_PASSWORD']),
            roles=app.config['SUPERUSER_ROLES']
        )
        app.security.datastore.commit()
