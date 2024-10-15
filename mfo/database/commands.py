# mfo/database/commands.py

import flask
from flask_security import hash_password
from datetime import datetime
from pathlib import Path
import json
import os
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from mfo.database.base import db
from mfo.database.users import User, Role
from mfo.database.models import Profile, Festival, Season, UserFestivalsRoles
import mfo.database.utilities


bp = flask.Blueprint('database', __name__,)


messages = {
    'adding_test_users': '===============================================\n==              Adding test users            ==\n===============================================',
    'completed_adding_test_users': '===============================================\n==       Completed adding test users         ==\n===============================================',
    'adding_test_festivals': '===============================================\n==           Adding test festivals           ==\n===============================================',
}


@bp.cli.command('test_data')
@flask.cli.with_appcontext
def test_data():
    test_festivals()
    test_users()

def open_json_file(environment_variable):
    try:
        file = flask.current_app.config[environment_variable]
    except KeyError:
        print(f"{environment_variable} environment variable is not defined")
        return

    file_path = Path(file)
    if os.path.isfile(file_path):
        pass
        print(f"found {environment_variable} file")
    else:
        print(f"file defined in {environment_variable} environment variable does not exist")
        return

    with file_path.open() as source:
        data_list = json.load(source)
    return data_list

def test_festivals():
    festivals_list = open_json_file('TEST_FESTIVALS_FILE')
    print(messages['adding_test_festivals'])

    for festival_dict in festivals_list:
        stmt = select(Festival).where(Festival.name == festival_dict['name'])
        festival = db.session.execute(stmt).scalars().first()
        if festival:
            print(f"Festival {festival.name} already exists. Skipping this festival.")
        else:
            festival = Festival()
            festival.name = festival_dict['name']
            festival.nickname = festival_dict['nickname']
            festival.location = festival_dict['location']
            festival.notes = festival_dict['notes']
            print(f"Added festival: {festival.name}")
            for season in festival_dict['seasons']:
                stmt = select(Season).where(Season.name == season['name'])
                season_entry = db.session.execute(stmt).scalars().first()
                if season_entry:
                    print(f"Season {season_entry.name} already exists. Skipping this season.")
                    continue
                season_entry = Season()
                season_entry.name = season['name']
                season_entry.primary = season['primary']
                season_entry.start_date = datetime.strptime(season['start_date'], "%Y-%m-%d").date()
                season_entry.registration_start_date = datetime.strptime(season['registration_start_date'], "%Y-%m-%d").date()
                season_entry.registration_end_date = datetime.strptime(season['registration_end_date'], "%Y-%m-%d").date()
                season_entry.end_date = datetime.strptime(season['end_date'], "%Y-%m-%d").date()
                festival.seasons.append(season_entry)
                print(f"Added season: {season_entry.name}")
            db.session.add(festival)
            


def test_users():
    users_list = open_json_file('TEST_USERS_FILE')
    print(messages['adding_test_users'])

    for user_dict in users_list:
        if flask.current_app.security.datastore.find_user(email=user_dict['email']):
            print(f"userid {user_dict['email']} already exists. Skipping this user.")
        else:
            user = flask.current_app.security.datastore.create_user(
                        email=user_dict['email'],
                        password=hash_password(user_dict['password']),
                    )
            
            festivals = user_dict['festivals']
            for festival_dict in festivals:
                festival_name = festival_dict['name']
                stmt = select(Festival).where(Festival.name == festival_name)
                festival = db.session.execute(stmt).scalars().first()
                if not festival:
                    print(f"Festival {festival_name} does not exist. Skipping this festival.")
                    continue

                roles_list = festival_dict['roles']
                for role in roles_list:
                    stmt = select(Role).where(Role.name == role)
                    role = db.session.execute(stmt).scalars().first()
                    if not role:
                        print(f"Role {role} does not exist. Skipping this role.")
                        continue
                    
                    # Check if the association already exists
                    stmt = select(UserFestivalsRoles).where(
                        UserFestivalsRoles.user == user,
                        UserFestivalsRoles.role == role,
                        UserFestivalsRoles.festival == festival
                    )
                    association = db.session.execute(stmt).scalars().one_or_none()
                    if association:
                        print("Association already exists.")
                    else:
                        association = UserFestivalsRoles(user=user, role=role, festival=festival)
                        db.session.add(association)
                        print(f"Added {user_dict['email']} role {role.name} to festival {festival.name}")

            primary_profile = user_dict['primary_profile']
            primary_profile['birthdate'] = datetime.strptime(primary_profile['birthdate'], "%Y-%m-%d").date()
            profile_entry=Profile(**primary_profile)
            user, profile_entry = mfo.database.utilities.set_primary_profile(user, profile_entry)
            
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

