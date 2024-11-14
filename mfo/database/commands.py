# mfo/database/commands.py

import flask
from flask_security import hash_password
from datetime import datetime
from pathlib import Path
import json
import os
from sqlalchemy import select
from sqlalchemy.sql import func
from decimal import Decimal

from mfo.database.base import db
from mfo.database.users import User
from mfo.database.models import Profile, Discipline, PerformanceType, Level, DefaultTimes, DefaultFee
import mfo.database.utilities


bp = flask.Blueprint('database', __name__,)


messages = {
    'adding_test_users': '===============================================\n==              Adding test users            ==\n===============================================',
    'completed_adding_test_users': '===============================================\n==       Completed adding test users         ==\n===============================================',
    'completed_adding_test_data': '===============================================\n==              Adding test data             ==\n===============================================',
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
    #db.drop_all()
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


@bp.cli.command('test_data')
@flask.cli.with_appcontext
def test_users():
    try:
        data_file = flask.current_app.config['TEST_DATA_FILE']
    except KeyError:
        print("TEST_DATA_FILE environment variable is not defined")
        return
    
    data_file_path = Path(data_file)
    if os.path.isfile(data_file_path):
        pass
        print("found TEST_DATA_FILE file")
    else:
        print("file defined in TEST_DATA_FILE environment variable does not exist")
        return

    with data_file_path.open() as source:
        data = json.load(source)

    for item in data:
        print(item)

    for discipline in data['DISCIPLINES']:
        # CHECK IF DISCIPLINE EXISTS using select statement
        if db.session.execute(
            select(Discipline)
            .where(func.lower(Discipline.name) == discipline.lower())
        ).scalar():
            print(f"Discipline {discipline} already exists. Skipping this discipline.")
            continue
        discipline_entry = Discipline()
        discipline_entry.name = discipline
        discipline_entry.description = ""
        db.session.add(discipline_entry)
    db.session.commit()

    for class_type in data['TYPES']:
        if db.session.execute(
            select(PerformanceType)
            .where(func.lower(PerformanceType.name) == class_type.lower())
        ).scalar():
            print(f"PerformanceType {class_type} already exists. Skipping this PerformanceType.")
            continue
        performance_type = PerformanceType()
        performance_type.name = class_type
        performance_type.description = ""
        db.session.add(performance_type)
    db.session.commit()

    for level in data['LEVELS']:
        if db.session.execute(select(Level).where(Level.name == level)).scalar():
            print(f"Level {level} already exists. Skipping this Level.")
            continue
        level_entry = Level(name=level, description="")
        db.session.add(level_entry)
    db.session.commit()

    for type, fee in data['DEFAULT_FEE'].items():
        if db.session.execute(
                select(DefaultFee)
                .where(func.lower(PerformanceType.name) == type.lower())
                .join(DefaultFee.performance_type)
            ).scalar():
            print(f"DefaultFee for {type} already exists. Skipping this DefaultFee.")
            continue

        performance_type = db.session.execute(
            select(PerformanceType).where(PerformanceType.name == type)
        ).scalar()
        if performance_type:
            default_fee = DefaultFee(
                performance_type=performance_type,
                fee=Decimal(fee)
            )
            db.session.add(default_fee)
    db.session.commit()

    for discipline, levels in data['DEFAULT_ADJUDICATION_TIME'].items():
        discipline_entry = db.session.execute(
            select(Discipline)
            .where(func.lower(Discipline.name) == discipline.lower())
        ).scalar()

        for level, time in levels.items():
            level_entry = db.session.execute(
                select(Level)
                .where(func.lower(Level.name) == level.lower())
            ).scalar()
            if discipline_entry and level_entry:
                if db.session.execute(
                        select(DefaultTimes)
                        .where(DefaultTimes.discipline_id == discipline_entry.id)
                        .where(DefaultTimes.level_id == level_entry.id)
                        .where(func.lower(DefaultTimes.time_type) == 'adjudication')
                    ).scalar():
                    print(f"Default adjudication time for {discipline} and {level} already exists. ",
                          f"Skipping this Default adjudication time.")
                    continue
                default_adjudication_time = DefaultTimes(
                    discipline_id=discipline_entry.id,
                    level_id=level_entry.id,
                    time_type='adjudication',
                    time=time
                )
                db.session.add(default_adjudication_time)


    for discipline, types in data['DEFAULT_MOVE_TIME'].items():
        discipline_entry = db.session.execute(
            select(Discipline)
            .where(func.lower(Discipline.name) == discipline.lower())
        ).scalar()

        for type, time in types.items():
            type_entry = db.session.execute(
                select(PerformanceType)
                .where(func.lower(PerformanceType.name) == type.lower())
            ).scalar()
            if discipline_entry and type_entry:
                if db.session.execute(
                        select(DefaultTimes)
                        .where(DefaultTimes.discipline_id == discipline_entry.id)
                        .where(DefaultTimes.performance_type_id == type_entry.id)
                        .where(DefaultTimes.time_type == 'move')
                    ).scalar():
                    print(f"Default move time for {discipline} and {type} already exists. ",
                          f"Skipping this Default move time.")
                    continue
                
                default_time = DefaultTimes(
                    discipline_id=discipline_entry.id,
                    performance_type_id=type_entry.id,
                    time_type='move',
                    time=time
                )
                db.session.add(default_time)
    db.session.commit()
  
    print(messages['completed_adding_test_data'])
    
