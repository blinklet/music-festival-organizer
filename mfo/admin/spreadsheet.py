# mfo/admin/spreadsheet.py

"""
This needs a major re-write. There is so much duplicate code here.
The functions are too long and do too much. They need to be broken up
into smaller functions that do one thing each. This will make the code
easier to read and maintain.
"""

import pandas as pd
import io
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import flask
from datetime import datetime
from itertools import chain

import mfo.admin.spreadsheet_columns
import mfo.utilities
from mfo.database.base import db
from mfo.database.models import Profile, FestivalClass, Repertoire, School, Entry

def read_sheet(file):
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(file.stream.read().decode("utf-8")))
        elif file.filename.endswith('.ods'):
            df = pd.read_excel(file, sheet_name='Form Responses 1', engine='odf')
        else:
            df = None
            succeeded = False
            if file.filename == "":
                message = 'Please select a file'
            else:
                message = "Unsupported file format"
            return df, succeeded, message

        # check if the spreadsheet columns are what we expect
        spreadsheet_columns = list(mfo.admin.spreadsheet_columns.names.keys())
        expected_columns = df.columns.values.tolist()
        for i in range(min(len(spreadsheet_columns), len(expected_columns))):
            if spreadsheet_columns[i] != expected_columns[i]:
                print("    *****SPREADSHEET IMPORT: COLUMNS ERROR ******")
                print(f"    File: {file.filename}")
                print(f"    Spreadsheet column name: '{spreadsheet_columns[i]}'")
                print(f"    Expected column name:    '{expected_columns[i]}'")
                print("    *********************************************")
                df = None
                succeeded = False
                message = 'Columns do not match expected schema'
                return df, succeeded, message

        succeeded = True
        message = 'File uploaded successfully'
        return df, succeeded, message

    except Exception as e:
        df = None
        succeeded = False
        message = f'Error reading file: {e}'
        return df, succeeded, message

def names_to_df(sheet_data):
    df = sheet_data.rename(mapper=mfo.admin.spreadsheet_columns.names, axis=1)
    return df

def all_profiles(input_df, issues, info):

    teachers = input_df[['teacher']].dropna().drop_duplicates()

    for index, row in teachers.iterrows():

        teacher_name = str(row.teacher).strip()
        stmt = select(Profile).where(Profile.name == teacher_name)
        existing_teacher = db.session.execute(stmt).scalar_one_or_none()

        if existing_teacher:
            info.append(f"** Row {index + 2}: Teacher profile for {teacher_name} already exists")
        else:
            teacher_profile = Profile(name=teacher_name)
            db.session.add(teacher_profile)
            info.append(f"** Row {index + 2}: Teacher profile for {teacher_name} added")

    group_teachers = input_df[['group_teacher']].dropna().drop_duplicates()

    for index, row in group_teachers.iterrows():
    
        group_teacher_name = str(row.group_teacher).strip()
        stmt = select(Profile).where(Profile.name == group_teacher_name)
        existing_teacher = db.session.execute(stmt).scalar_one_or_none()

        if existing_teacher:
            info.append(f"** Row {index + 2}: Group teacher profile for {group_teacher_name} already exists")
        else:
            teacher_profile = Profile(name=str(group_teacher_name))
            db.session.add(teacher_profile)
            info.append(f"** Row {index + 2}: Group Teacher {group_teacher_name}: added new record")

    accompanist_name_columns = [
        col for col in input_df.columns if col.startswith('accompanist_name_')
        ]

    accompanist_phone_columns = [
        col for col in input_df.columns if col.startswith('accompanist_phone_')
        ]

    accompanist_email_columns = [
        col for col in input_df.columns if col.startswith('accompanist_email_')
        ]

    accompanist_columns = list(
        zip(
            accompanist_name_columns, 
            accompanist_phone_columns, 
            accompanist_email_columns
            )
        )

    accompanists = []
    for index, row in input_df.iterrows():
        for name_col, phone_col, email_col in accompanist_columns:
            
            name = row[name_col]
            if pd.notna(name):
                name = str(name).strip()

                phone = row[phone_col]
                if pd.isna(phone):
                    phone = None
                elif isinstance(phone, (int, float)):
                    phone = str(int(phone))
                elif isinstance(phone, str):
                    phone = phone.strip()
                else:
                    phone = None

                email = row[email_col]
                if pd.notna(email):
                    email = (str(email)).lower().strip()
                else:
                    email = None
                    
                accompanists.append({'name': name, 'phone': phone, 'email': email, 'index': index})
            else:
                pass

    for accompanist in accompanists:
        name = accompanist['name']
        phone = accompanist['phone']
        email = accompanist['email']
        index = accompanist['index']

        stmt = select(Profile).where(Profile.name == name)
        existing_accompanist = db.session.execute(stmt).scalar_one_or_none()

        if existing_accompanist:
            if pd.notna(existing_accompanist.phone) and pd.notna(existing_accompanist.email):
                info.append(
                    f"** Row {index +2}: Accompanist '{name}': "
                    f"already exists and has email and phone"
                )
                if pd.notna(phone) and (existing_accompanist.phone != phone):
                    issues.append(
                        f"**** Row {index +2}: Accompanist '{name}': "
                        f"found a different phone number '{phone}'. "
                        f"Keeping original phone number '{existing_accompanist.phone}'"
                    )
                if pd.notna(email) and (existing_accompanist.email != email):
                    issues.append(
                        f"**** Row {index +2}: Accompanist '{name}': "
                        f"found a different email '{email}'. "
                        f"Keeping original email '{existing_accompanist.email}'"
                    )
            if pd.isna(existing_accompanist.phone) and pd.notna(phone):
                existing_accompanist.phone = phone
                info.append(
                    f"** Row {index +2}: Accompanist {name}: "
                    f"add phone number to existing record"
                )
            if pd.isna(existing_accompanist.email) and pd.notna(email):
                existing_accompanist.email = email
                info.append(
                    f"** Row {index +2}: Accompanist {name}: "
                    f"add email to existing record"
                )
        else:
            new_accompanist = Profile(
                name=name, 
                phone=phone,
                email=email,
            )
            db.session.add(new_accompanist)
            info.append(f"** Row {index +2}: Added accompanist '{name}', phone: '{phone}', email: '{email}'")

    for index, participant in input_df.iterrows():
        if participant.type == "Group participant":
            group_name = str(participant.group_name).strip()
            email = str(participant.email).lower()

            stmt = select(Profile).where(
                Profile.group_name == group_name,
            )
            existing_group = db.session.execute(stmt).scalar_one_or_none()

            if not existing_group:
                if pd.notna(participant.phone):
                    phone = participant.phone
                    if isinstance(phone, (int, float)):
                        phone = str(int(phone))
                    elif isinstance(phone, str):
                        phone = phone.strip()
                    else:
                        phone = None
                else:
                    if pd.notna(participant.group_phone):
                        phone = participant.group_phone
                        if isinstance(phone, (int, float)):
                            phone = str(int(phone))
                        elif isinstance(phone, str):
                            phone = phone.strip()
                        else:
                            phone = None
                
                if pd.notna(participant.group_address):
                    address = str(participant.group_address).strip()
                else:
                    address = None

                if pd.notna(participant.group_city):
                    city = str(participant.group_city).strip()
                else:
                    city = None

                if pd.notna(participant.group_postal_code):
                    postal_code = str(participant.group_postal_code).strip()
                else:
                    postal_code = None

                if pd.notna(participant.group_province):
                    province = str(participant.group_province).strip()
                else:
                    province = None

                new_group = Profile(
                    group_name=group_name,
                    email=email,
                    phone=phone,
                    address=address,
                    city=city,
                    postal_code=postal_code,
                    province=province,
                )
                db.session.add(new_group)
                info.append(f"** Row {index +2}: Group {group_name} {phone} {email}: added new record")

            else:
                info.append(f"** Row {index +2}: Group {group_name} {phone} {email}: already exists")

        elif participant.type == "Individual participant (Solo, Recital, Duet, Trio,  Quartet, or Quintet Class)":
            if pd.isna(participant.first_name):
                full_name = str(participant.last_name).strip()
            elif pd.isna(participant.last_name):
                full_name = str(participant.first_name).strip()
            else:
                full_name = str(participant.first_name).strip() + ' ' + str(participant.last_name).strip()
            email = str(participant.email).lower()
            
            stmt = select(Profile).where(Profile.name == full_name)

            existing_participant = db.session.execute(stmt).scalar_one_or_none()
            if not existing_participant:
                if pd.notna(participant.phone):
                    phone = str(int(participant.phone))
                else:
                    phone = None

                if pd.notna(participant.address):
                    address = str(participant.address).strip()
                else:
                    address = None

                if pd.notna(participant.city):
                    city = str(participant.city).strip()
                else:
                    city = None

                if pd.notna(participant.postal_code):
                    postal_code = str(participant.postal_code).strip()
                else:
                    postal_code = None

                if pd.notna(participant.province):
                    province = str(participant.province).strip()
                else:
                    province = None

                new_participant = Profile(
                    name=full_name,
                    email=email,
                    phone=phone,
                    address=address,
                    city=city,
                    postal_code=postal_code,
                    province=province,
                )
                db.session.add(new_participant)
                info.append(f"** Row {index +2}: Participant {full_name} {phone} {email}: added new record")
            else:
                info.append(f"** Row {index +2}: Participant {full_name} {email}: already exists")
                if not existing_participant.phone:
                    if pd.notna(participant.phone):
                        phone = str(int(participant.phone))
                    else:
                        phone = None
                    if phone:
                        existing_participant.phone = phone
                        info.append(f"** Row {index +2}: Participant {full_name} {phone} {email}: added phone number")
                if not existing_participant.email:
                    if pd.notna(participant.email):
                        email = str(participant.email).lower()
                    else:
                        email = None
                    if email:
                        existing_participant.email = email
                        info.append(f"** Row {index +2}: Participant {full_name} {phone} {email}: added email")
                if not existing_participant.address:
                    if pd.notna(participant.address):
                        address = str(participant.address).strip()
                    else:
                        address = None
                    if address:
                        existing_participant.address = address
                        info.append(f"** Row {index +2}: Participant {full_name}: added address")
                if not existing_participant.city:
                    if pd.notna(participant.city):
                        city = str(participant.city).strip()
                    else:
                        city = None
                    if city:
                        existing_participant.city = city
                        info.append(f"** Row {index +2}: Participant {full_name}: added city")
                if not existing_participant.postal_code:
                    if pd.notna(participant.postal_code):
                        postal_code = str(participant.postal_code).strip()
                    else:
                        postal_code = None
                    if postal_code:
                        existing_participant.postal_code = postal_code
                        info.append(f"** Row {index +2}: Participant {full_name}: added postal code")
                if not existing_participant.province:
                    if pd.notna(participant.province):
                        province = str(participant.province).strip()
                    else:
                        province = None
                    if province:
                        existing_participant.province = province
                        info.append(f"** Row {index +2}: Participant {full_name}: added province")

        else:
            issues.append(f"Spreadsheet error: Row {index +2}: invalid entry in 'group or individual' column: '{participant.type}'")

def related_profiles(input_df, issues, info):
    
    students_and_teachers = input_df[['teacher', 'first_name', 'last_name']].dropna(how='all').drop_duplicates()

    for index, row in students_and_teachers.iterrows():
        if pd.notna(row.teacher) :

            teacher_name = str(row.teacher).strip()
            student_first_name = row.first_name
            student_last_name = row.last_name

            if pd.isna(student_first_name):
                student_full_name = str(student_last_name).strip()
            elif pd.isna(student_last_name):
                student_full_name = str(student_first_name).strip()
            else:
                student_full_name = str(student_first_name).strip() + ' ' + str(student_last_name).strip()

            stmt = select(Profile).where(Profile.name == teacher_name)
            teacher = db.session.execute(stmt).scalar_one_or_none()
            stmt = select(Profile).where(Profile.name == student_full_name)
            student = db.session.execute(stmt).scalar_one_or_none()

            if student in teacher.students:
                info.append(f"** Row {index +2}: Student {student_full_name} already associated with Teacher {teacher_name}")
            else:
                teacher.students.append(student)
                info.append(f"** Row {index +2}: Added Student {student_full_name} to Teacher {teacher_name}")

    groups_and_teachers = input_df[['group_name', 'group_teacher']].dropna().drop_duplicates()

    for index, row in groups_and_teachers.iterrows():
        
        group_teacher_name = str(row.group_teacher).strip()

        stmt = select(Profile).where(Profile.name == group_teacher_name)
        teacher = db.session.execute(stmt).scalar_one_or_none()

        group_name = str(row.group_name).strip()
        stmt = select(Profile).where(Profile.group_name == group_name)
        group = db.session.execute(stmt).scalar_one_or_none()

        if group in teacher.group:
            info.append(f"**Row {index +2}: Group {group_name} already associated with Teacher {group_teacher_name}")
        else:
            teacher.group.append(group)
            info.append(f"** Row {index +2}: Added Group {group_name} to Teacher {group_teacher_name}")

        if group in teacher.students:
            info.append(f"**Row {index +2}: Group {group_name} already associated (as a student) with Teacher {group_teacher_name}")
        else:
            teacher.students.append(group)
            info.append(f"** Row {index +2}: Added Group {group_name} (as a student) to Teacher {group_teacher_name}")

def classes(input_df, issues, info):

    class_number_columns = [
        col for col in input_df.columns if col.startswith('class_number_')
    ]

    class_suffix_columns = [
        col for col in input_df.columns if col.startswith('class_suffix_')
    ]

    class_columns = list(
        zip(
            class_number_columns, 
            class_suffix_columns
        )
    )


    classes = []
    class_column_type = mfo.admin.spreadsheet_columns.class_column_type
    class_repertoire_columns = mfo.admin.spreadsheet_columns.class_repertoire_columns

    #DEBUG
    from pprint import pprint
    pprint(input_df.columns)

    for index, row in input_df.iterrows():
        for class_num_col, class_suf_col in class_columns:

            number = row[class_num_col]
            suffix = row[class_suf_col]


            if pd.notna(number) & pd.isna(suffix):
                if isinstance(number, (int, float)):
                    number=str(int(number)).zfill(4)
                else:
                    number=number.strip()
                suffix = None
                good_number = True
            elif pd.notna(number) & pd.notna(suffix):
                if isinstance(number, (int, float)):
                    number=str(int(number)).zfill(4)
                else:
                    number=number.strip()
                suffix = str(suffix).strip()
                good_number = True
            elif pd.isna(number) & pd.notna(suffix):
                issues.append(f"**** Row {index+2}: Error: Class number missing")
                good_number = False
            elif pd.isna(number) & pd.isna(suffix):
                good_number = False
            else:
                pass

            if good_number:
                parts = class_num_col.rsplit('_')

                if len(parts) > 1:
                    col_num = str(parts[-1]) 
                else:
                    col_num = str(class_num_col)
                
                type = class_column_type[col_num]

                repertoire_columns = class_repertoire_columns[col_num]

                test_pieces = []

                for columns in repertoire_columns:
                    title_col = columns['title']
                    duration_col = columns['duration']
                    composer_col = columns['composer']

                    title = row[title_col]
                    duration = row[duration_col]
                    composer = row[composer_col]

                    if pd.notna(title) and pd.notna(composer):
                        title = str(title).strip()
                        if pd.notna(duration):
                            duration = int(duration)
                        else:
                            duration = None
                        composer = str(composer).strip()

                        test_pieces.append(
                            {
                                'title': title,
                                'duration': duration,
                                'composer': composer
                            }
                        )

                classes.append({'number': number, 'suffix': suffix, 'type': type, 'test_pieces': test_pieces, 'index': index})

    for row in classes:
        number = row['number']
        suffix = row['suffix']
        index = row['index']
        type = row['type']
        test_pieces = row['test_pieces']

        stmt = select(FestivalClass).where(
            FestivalClass.number == number,
            FestivalClass.suffix == suffix,
        )
        festival_class = db.session.execute(stmt).scalar_one_or_none()

        if pd.isna(suffix):
            print_suffix = ""
        else:
            print_suffix = suffix
        
        if festival_class:
            info.append(f"** Row {index+2}: Class {number}{print_suffix}, type: '{festival_class.class_type}'--'{type}', already exists")

            if pd.notna(festival_class.class_type):
                if festival_class.class_type != type:
                    issues.append(f"**** Row {index+2}: Class {number}{print_suffix} may be recorded as wrong type.\n  ** It was previously recorded as type: {festival_class.class_type} and has been found again as type: {type}\n  ** Currently-recorded type will remain unchanged")
                    type = festival_class.class_type
                    
            existing_pieces = {(piece.title, piece.composer) for piece in festival_class.test_pieces}
            
            for test_piece in test_pieces:
                title = test_piece['title']
                duration = test_piece['duration']
                composer = test_piece['composer']

                if (title, composer) in existing_pieces:
                    continue
                else:
                    stmt = select(Repertoire).where(
                        Repertoire.title == title,
                        Repertoire.composer == composer,
                    )
                    existing_piece = db.session.execute(stmt).scalar_one_or_none()

                    if existing_piece:
                        festival_class.test_pieces.append(existing_piece)
                        info.append(f"** Row {index+2}: Added test piece '{title}' by '{composer}' to class '{number}{print_suffix}'")
                    else:
                        # If the repertoire piece does not exist, create it and append
                        new_piece = Repertoire(
                            title=title,
                            duration=duration,
                            composer=composer,
                        )
                        db.session.add(new_piece)
                        festival_class.test_pieces.append(new_piece)
                        info.append(f"** Row {index+2}: Created new test piece '{title}' by '{composer}' and added it to class '{number}{print_suffix}'")

        else:
            new_festival_class = FestivalClass(
                number=number,
                suffix=suffix,
                class_type=type,
            )
            db.session.add(new_festival_class)
            info.append(f"** Row {index+2}: Class {number}{print_suffix}, type: {type},  added")

            for x in test_pieces:
                title = x['title']
                duration = x['duration']
                composer = x['composer']

                if pd.notna(title) and pd.notna(composer):
                    # Check if the repertoire piece exists in the database
                    stmt = select(Repertoire).where(
                        Repertoire.title == title,
                        Repertoire.composer == composer,
                    )
                    existing_piece = db.session.execute(stmt).scalar_one_or_none()

                    if existing_piece:
                        new_festival_class.test_pieces.append(existing_piece)
                        info.append(f"** Row {index+2}: Added test piece '{title}' by '{composer}' to class '{number}{print_suffix}'")
                    else:
                        # If the repertoire piece does not exist, create it and append
                        new_piece = Repertoire(
                            title=title,
                            duration=duration,
                            composer=composer,
                        )
                        db.session.add(new_piece)
                        new_festival_class.test_pieces.append(new_piece)
                        info.append(f"** Row {index+2}: Created new test piece '{title}' by '{composer}' and added it to class '{number}{print_suffix}'")

            db.session.add(new_festival_class)


def schools(input_df, issues, info):
    schools_columns = ['school', 'group_school']
    existing_schools = set()
    school_names = []
    for index, row in input_df.iterrows():
        for name_col in schools_columns:
            name = row[name_col]
            if pd.notna(name):
                name = str(name).strip()
                if name not in existing_schools:
                    existing_schools.add(name)
                    school_names.append({'name': name, 'index': index})

    for school_name in school_names:
        name = school_name['name']
        index = school_name['index']

        stmt = select(School).where(
            School.name == name,
        )
        existing_school = db.session.execute(stmt).scalar_one_or_none()

        if existing_school:
            info.append(f"** Row {index+2}: School '{name}' already exists **")
        else:
            new_school = School(name=name)
            db.session.add(new_school)
            info.append(f"** Row {index+2}: School {name} added")
    
    participants_and_schools = input_df[['first_name', 'last_name', 'school', 'teacher']].dropna(how='all').drop_duplicates()

    for index, row in participants_and_schools.iterrows():
        
        if  pd.isna(row.school) or row.school == "NA":
            pass
        else:
            student_first_name = str(row.first_name).strip()
            student_last_name = str(row.last_name).strip()
            school_name = str(row.school).strip()
            teacher_name = str(row.teacher).strip()

            stmt = select(School).where(
                School.name == school_name,
            )
            school = db.session.execute(stmt).scalar_one_or_none()

            if pd.isna(student_first_name):
                student_full_name = str(student_last_name).strip()
            elif pd.isna(student_last_name):
                student_full_name = str(student_first_name).strip()
            else:
                student_full_name = str(student_first_name).strip() + ' ' + str(student_last_name).strip()

            stmt = select(Profile).where(Profile.name == student_full_name)
            student = db.session.execute(stmt).scalar_one_or_none()

            stmt = select(Profile).where(Profile.name == teacher_name)
            teacher = db.session.execute(stmt).scalar_one_or_none()

            if student in school.students_or_groups:
                info.append(f"** Row {index+2}: Student '{student_full_name}' already associated with School: '{school_name}'")
            else:
                school.students_or_groups.append(student)
                info.append(f"** Row {index+2}: Added Student '{student_full_name}' to School: '{school_name}'")
            
            if teacher in school.teachers:
                info.append(f"** Row {index+2}: Teacher '{teacher_name}' already associated with School: '{school_name}'")
            else:
                school.teachers.append(teacher)
                info.append(f"** Row {index+2}: Added teacher '{teacher_name}' to School: '{school_name}'")

    groups_and_schools = input_df[['group_name', 'group_teacher', 'group_school']].dropna().drop_duplicates()

    for index, row in groups_and_schools.iterrows():
        if  pd.isna(row.group_school) or row.group_school == "NA":
            pass
        else:
            group_school = row.group_school.strip()
            group_name = row.group_name.strip()
            group_teacher = row.group_teacher.strip()

            stmt = select(School).where(
                School.name == group_school
            )
            school = db.session.execute(stmt).scalar_one_or_none()

            stmt = select(Profile).where(
                Profile.group_name == row.group_name
            )
            group = db.session.execute(stmt).scalar_one_or_none()

            stmt = select(Profile).where(
                Profile.name == group_teacher
            )
            teacher = db.session.execute(stmt).scalar_one_or_none()

            if group in school.students_or_groups:
                info.append(f"** Row {index+2}: Group {group_name} already associated with School {group_school}")
            else:
                school.students_or_groups.append(group)
                info.append(f"** Row {index+2}: Added Group {group_name} to School {group_school}")

            if teacher in school.teachers:
                info.append(f"** Row {index+2}: Group Teacher {group_teacher} already associated with School {group_school}")
            else:
                school.teachers.append(teacher)
                info.append(f"** Row {index+2}: Added Group Teacher {group_teacher} to School {group_school}")


def repertoire(input_df, issues, info):
    title_columns = [
        col for col in input_df.columns if col.startswith('repertoire_title_')
    ]

    duration_columns = [
        col for col in input_df.columns if col.startswith('repertoire_duration_')
    ]

    composer_columns = [
        col for col in input_df.columns if col.startswith('composer_')
    ]

    repertoire_columns = list(
        zip(
            title_columns, 
            duration_columns,
            composer_columns
        )
    )

    repertoire_pieces = []
    
    for index, row in input_df.iterrows():
        for title_col, duration_col, composer_col in repertoire_columns:
            title = row[title_col]
            duration = row[duration_col]
            composer = row[composer_col]
            index = index
            if not pd.isna(title) and not pd.isna(duration) and not pd.isna(composer):
                if pd.notna(title):
                    if isinstance(title, (int, float)):
                        title=str(int(title))
                    else:
                        title=str(title).strip()
                else:
                    issues.append(f"**** Row: {index+2}: Repertoire has missing title")
                    title = None

                if pd.notna(duration):
                    if isinstance(duration, (int, float)):
                        duration=int(duration)
                    else:
                        issues.append(f"**** Row: {index+2}: Repertoire has invalid duration: '{duration}'")
                        duration = None
                else:
                    issues.append(f"**** Row: {index+2}: Repertoire has invalid duration: '{duration}'")
                    duration = None

                if pd.notna(composer):
                    if isinstance(composer, (int, float)):
                        issues.append(f"**** Row: {index+2}: Repertoire has invalid composer: '{composer}'")
                        composer = None
                    else:
                        composer = str(composer).strip()      
                else:
                    issues.append(f"**** Row: {index+2}: Repertoire has invalid composer: '{composer}'")
                    composer = None
            
                repertoire_pieces.append({'title': title, 'duration': duration, 'composer': composer, 'index': index})

    for row in repertoire_pieces:
        title = row['title']
        duration = row['duration']
        composer = row['composer']
        index = row['index']

        stmt = select(Repertoire).where(
            Repertoire.title == title,
            Repertoire.composer == composer,
        )
        existing_repertoire = db.session.execute(stmt).scalar_one_or_none()

        if existing_repertoire:
            info.append(f"** Row: {index+2}: Repertore {title} by {composer} already exists **")
            if existing_repertoire.duration != duration:
                issues.append(f"**** Row: {index+2}: Repertore {title} by {composer} already exists but duration is different. Existing duration was {existing_repertoire.duration} minutes long, duplicate entry was {duration} minutes long")
        else:
            new_repertoire = Repertoire(
                title=title,
                duration=duration,
                composer=composer,
            )

            db.session.add(new_repertoire)
            info.append(f"** Row: {index+2}: Repertore {title} by {composer} duration {duration} minutes added")

def entries(input_df, issues, info):
    """
    Each row in the dataframe is an entry.
    Each entry is a combination of a profile, a class, and a repertoire.
    The profile is either a student or a group.
    The class is a festival class.
    The repertoire is a list of pieces.
    Occasionally, the same student or group may make multiple entries (rows in the spreadsheet)
    We assume these are additional entries, not duplicates. Though they might be attempts
    at corrections or additions to the original entry. We will highlight the second entry 
    as an issue to be verified.
    """
    repertoire_columns = mfo.admin.spreadsheet_columns.class_repertoire_columns

    for index, row in input_df.iterrows():
        # test if this is an individual entry or a group entry
        if row.type.strip() == "Group participant":
            group_name = str(row.group_name).strip()

            stmt = select(Profile).where(Profile.group_name == group_name)
            group = db.session.execute(stmt).scalar_one_or_none()

            for group_index in range(15,18):
                group_class_number_col = "class_number_" + str(group_index)
                class_number = row[group_class_number_col]

                if pd.notna(class_number):
                    group_class_suffix_col = "class_suffix_" + str(group_index)
                    class_suffix = row[group_class_suffix_col]
                    print_suffix = str(class_suffix).strip()

                    if pd.notna(class_number) & pd.isna(class_suffix):
                        if isinstance(class_number, (int, float)):
                            class_number=str(int(class_number)).zfill(4)
                        else:
                            class_number=class_number.strip()
                        class_suffix = None
                        print_suffix = ""
                    elif pd.notna(class_number) & pd.notna(class_suffix):
                        if isinstance(class_number, (int, float)):
                            class_number=str(int(class_number)).zfill(4)
                        else:
                            class_number=class_number.strip()
                        class_suffix = str(class_suffix).strip()
                        print_suffix = class_suffix
                    else:
                        pass

                    stmt = select(FestivalClass).where(
                        FestivalClass.number == class_number,
                        FestivalClass.suffix == class_suffix
                    )
                    festival_class = db.session.execute(stmt).scalar_one_or_none()

                    new_entry = Entry(
                        festival_class=festival_class,
                        participants=[group],
                        repertoire=[],
                        timestamp=datetime.now(),
                        comments=None
                    )
                    db.session.add(new_entry)
                    info.append(f"** Row {index+2}: Added large group entry for '{group_name}' in class {class_number}{print_suffix}")

                    accompanist_name_col = "accompanist_name_" + str(group_index)
                    accompanist_phone_col = "accompanist_phone_" + str(group_index)
                    accompanist_email_col = "accompanist_email_" + str(group_index)

                    accompanist_name = row[accompanist_name_col]
                    accompanist_phone = row[accompanist_phone_col]
                    accompanist_email = row[accompanist_email_col]

                    if pd.notna(accompanist_name):
                        accompanist_name = str(accompanist_name).strip()
                        stmt = select(Profile).where(Profile.name == accompanist_name)
                        accompanist = db.session.execute(stmt).scalar_one_or_none()
                        new_entry.accompanists.append(accompanist)
                        info.append(f"** Row {index+2}: Added accompanist {accompanist_name} to large group entry")
                    
                    entry_repertoire_columns = repertoire_columns[str(group_index)]

                    for columns in entry_repertoire_columns:
                        title_col = columns['title']
                        duration_col = columns['duration']
                        composer_col = columns['composer']

                        title = row[title_col]
                        duration = row[duration_col]
                        composer = row[composer_col]

                        if pd.notna(title) and pd.notna(composer):
                            title = str(title).strip()
                            if pd.notna(duration):
                                duration = int(duration)
                            else:
                                duration = None
                            composer = str(composer).strip()

                            stmt = select(Repertoire).where(
                                Repertoire.title == title,
                                Repertoire.composer == composer
                            )

                            repertoire_piece = db.session.execute(stmt).scalar_one_or_none()
                            if repertoire_piece:
                                new_entry.repertoire.append(repertoire_piece)
                                info.append(f"** Row {index+2}: Added repertoire '{title}' by '{composer}' to large group entry for {group_name} in class {class_number}{print_suffix}")
                            else:
                                issues.append(f"**** Row {index+2}: Repertoire '{title}' by '{composer}' in class {class_number}{print_suffix} in large group entry for {group_name} not found in database. Will add repertoire to DB. Check that this is not a misspelling")
                                new_repertoire = Repertoire(title=title, duration=duration, composer=composer)
                                db.session.add(new_repertoire)
                                new_entry.repertoire.append(new_repertoire)

        elif row.type.strip() == "Individual participant (Solo, Recital, Duet, Trio,  Quartet, or Quintet Class)":
            if pd.isna(row.first_name):
                full_name = str(row.last_name).strip()
            elif pd.isna(row.last_name):
                full_name = str(row.first_name).strip()
            else:
                full_name = str(row.first_name).strip() + ' ' + str(row.last_name).strip()

            stmt = select(Profile).where(Profile.name == full_name)
            participant = db.session.execute(stmt).scalar_one_or_none()
 
            # solo, recital, and small group entries are numbers 014
            for solo_class_index in range(15):
                solo_class_number_col = "class_number_" + str(solo_class_index)
                class_number = row[solo_class_number_col]

                if pd.notna(class_number):
                    solo_class_suffix_col = "class_suffix_" + str(solo_class_index)
                    # repertoire_title_col = "repertoire_title_" + str(solo_class_index)
                    # repertoire_duration_col = "repertoire_duration_" + str(solo_class_index)
                    # repertoire_composer_col = "composer_" + str(solo_class_index)
                    accompanist_name_col = "accompanist_name_" + str(solo_class_index)
                    accompanist_phone_col = "accompanist_phone_" + str(solo_class_index)
                    accompanist_email_col = "accompanist_email_" + str(solo_class_index)
                    
                    class_suffix = row[solo_class_suffix_col]

                    if pd.notna(class_number) & pd.isna(class_suffix):
                        if isinstance(class_number, (int, float)):
                            class_number=str(int(class_number)).zfill(4)
                        else:
                            class_number=class_number.strip()
                        class_suffix = None
                        print_suffix = ""
                    elif pd.notna(class_number) & pd.notna(class_suffix):
                        if isinstance(class_number, (int, float)):
                            class_number=str(int(class_number)).zfill(4)
                        else:
                            class_number=class_number.strip()
                        class_suffix = str(class_suffix).strip()
                        print_suffix = class_suffix
                    else:
                        pass

                    stmt = select(FestivalClass).where(
                        FestivalClass.number == class_number,
                        FestivalClass.suffix == class_suffix
                    )
                    festival_class = db.session.execute(stmt).scalar_one_or_none()

                    accompanist_name = row[accompanist_name_col]
                    accompanist_phone = row[accompanist_phone_col]
                    accompanist_email = row[accompanist_email_col]

                    # This is a solo or small group class so all items are entered once
                    new_entry = Entry(
                        festival_class=festival_class,
                        participants=[participant],
                        repertoire=[],
                        timestamp=datetime.now(),
                        comments=None
                    )
                    db.session.add(new_entry)
                    info.append(f"** Row {index+2}: Added entry for {full_name} in class {class_number}{print_suffix}")

                    if pd.notna(accompanist_name):
                        accompanist_name = str(accompanist_name).strip()
                        stmt = select(Profile).where(Profile.name == accompanist_name)
                        accompanist = db.session.execute(stmt).scalar_one_or_none()
                        new_entry.accompanists.append(accompanist)
                        info.append(f"** Row {index+2}: Added accompanist {accompanist_name} to entry for {full_name} in class {class_number}{print_suffix}")

                    # find participant columns for additional participants in the same class
                    # prevent '1' matching '11' for example
                    participant_columns = []

                    for col in input_df.columns:
                        col_number = col.rsplit('_')[-1]
                        if len(str(col_number)) == len(str(solo_class_index)):
                            if str(col_number) == str(solo_class_index):
                                if col.startswith('participant_'):
                                    if pd.notna(row[col]):
                                        participant_columns.append(col)

                    if len(participant_columns) > 0:
                        for participant_col in participant_columns:
                            participant_name = str(row[participant_col]).strip()
                            stmt = select(Profile).where(Profile.name == participant_name)
                            additional_participant = db.session.execute(stmt).scalar_one_or_none()
                            if additional_participant:
                                new_entry.participants.append(additional_participant)
                                info.append(f"** Row {index+2}: Added additional participant {participant_name} to entry for {full_name} in {festival_class.class_type} class {class_number}{print_suffix}")
                            else:
                                issues.append(f"**** Row {index+2}: Additional participant '{participant_name}' in entry class {class_number}{print_suffix} not found in database. Will add participant to DB. Check that this is not a misspelling")
                                new_participant = Profile(name=participant_name)
                                db.session.add(new_participant)
                                new_entry.participants.append(new_participant)                   
                    
                    # The recital class is a special case where the same participant plays multiple repertoire
                    # so I created a generalization were all repertoire is appended to an empty list
                    # this works for every class where there is 1 or more repertoire pieces
                    entry_repertoire_columns = repertoire_columns[str(solo_class_index)]

                    for columns in entry_repertoire_columns:
                        title_col = columns['title']
                        duration_col = columns['duration']
                        composer_col = columns['composer']

                        title = row[title_col]
                        duration = row[duration_col]
                        composer = row[composer_col]

                        if pd.notna(title) and pd.notna(composer):
                            title = str(title).strip()
                            if pd.notna(duration):
                                duration = int(duration)
                            else:
                                duration = None
                            composer = str(composer).strip()

                            stmt = select(Repertoire).where(
                                Repertoire.title == title,
                                Repertoire.composer == composer
                            )

                            repertoire_piece = db.session.execute(stmt).scalar_one_or_none()
                            if repertoire_piece:
                                new_entry.repertoire.append(repertoire_piece)
                                info.append(f"** Row {index+2}: Added repertoire '{title}' by '{composer}' to entry for {full_name} in {festival_class.class_type} class {class_number}{print_suffix}")
                            else:
                                issues.append(f"**** Row {index+2}: Repertoire '{title}' by '{composer}' in entry class {class_number}{print_suffix} not found in database. Will add repertoire to DB. Check that this is not a misspelling")
                                new_repertoire = Repertoire(title=title, duration=duration, composer=composer)
                                db.session.add(new_repertoire)
                                new_entry.repertoire.append(new_repertoire)

                else:
                    pass
            
        else:
            pass




def gather_issues(input_df):
    issues = mfo.utilities.CustomList()
    info = mfo.utilities.CustomList()
    all_profiles(input_df, issues, info)
    related_profiles(input_df, issues, info)
    repertoire(input_df, issues, info)
    classes(input_df, issues, info)
    schools(input_df, issues, info)
    entries(input_df, issues, info)
    return issues, info

# def convert_to_db():
#     try:
#         db.session.commit()
#     except IntegrityError:
#         db.session.rollback()
#         raise
#     except Exception as e:
#         db.session.rollback()
#         raise





def convert_to_db(sheet_data):
    df = names_to_df(sheet_data)
    issues, info = gather_issues(df)

    print("\n\n\nISSUES:")
    for issue in issues:
        print(issue)

    # user_response = input("Do you want to commit these changes to the database? (yes/no): ")
    # if user_response.lower() == 'yes':
    try:
        db.session.commit()
        print("Changes committed to the database.")
    except IntegrityError:
        db.session.rollback()
        print("Commit failed due to integrity error.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Commit failed due to error: {e}")
    # else:
    #     db.session.rollback()
    #     print("Changes were not committed to the database.")
