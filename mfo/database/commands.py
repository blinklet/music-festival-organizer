# mfo/database.commands.py

import flask
from flask_security import hash_password
from datetime import datetime
from pathlib import Path
import json
import os

from mfo.database.base import db
from mfo.database.users import User
from mfo.database.models import Profile
import mfo.database.utilities


bp = flask.Blueprint('database', __name__,)


messages = {
    'adding_test_users': '===============================================\n==              Adding test users            ==\n===============================================',
    'completed_adding_test_users': '===============================================\n==       Completed adding test users         ==\n==============================================='
}


@bp.cli.command('test_users')
@flask.cli.with_appcontext
def test_users():
    try:
        users_file = flask.current_app.config['TEST_USERS_FILE']
    except KeyError:
        print("TEST_USERS_FILE environment variable is not defined")
        return
    
    users_file_path = Path(users_file)
    if os.path.isfile(users_file_path):
        pass
        print("found TEST_USERS_FILE file")
    else:
        print("file defined in TEST_USERS_FILE environment variable does not exist")
        return

    with users_file_path.open() as source:
        users_list = json.load(source)

    print(messages['adding_test_users'])

    for user_dict in users_list:
        if flask.current_app.security.datastore.find_user(email=user_dict['email']):
            print(f"userid {user_dict['email']} already exists. Skipping this user.")
        else:
            user = flask.current_app.security.datastore.create_user(
                        email=user_dict['email'],
                        password=hash_password(user_dict['password']),
                        roles=user_dict['roles'],
                    )
            primary_profile = user_dict['primary_profile']
            primary_profile['birthdate'] = datetime.strptime(primary_profile['birthdate'], "%Y-%m-%d").date()
            profile_entry=Profile(**primary_profile)
            user, profile_entry = mfo.database.utilities.set_primary_profile(user, profile_entry)
            # add roles to profile
            for role in user.roles:
                profile_entry.roles.append(role)
            db.session.add(user)
            db.session.add(profile_entry)
            print(f"Added userid: {user.email}")

            

    db.session.commit()
    
    print(messages['completed_adding_test_users'])
        

@bp.cli.command('create')
@flask.cli.with_appcontext
def create():
    db.drop_all()
    db.create_all()

    roles_dict = flask.current_app.config['ROLES']
    roles_keys = roles_dict.keys()
    for key in roles_keys:
        role=roles_dict[key]
        flask.current_app.security.datastore.find_or_create_role(
            name=role['name'], 
            description=role['description'],
            permissions=role['permissions'],
    )
    flask.current_app.security.datastore.commit()

