# mfo/admin/spreadsheet.py

# Functions and Classes that support reading data from 
# spreadsheets and importing it into the SQL database

import pandas as pd
import io
from sqlalchemy import select, or_, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import flask

import mfo.admin.spreadsheet_columns
import mfo.utilities
from mfo.database.base import db
from mfo.database.models import Profile, FestivalClass, Repertoire, School

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
        # -- Specific to Queens County Music Festival responses from Google form
        spreadsheet_columns = list(mfo.admin.spreadsheet_columns.names.keys())
        expected_columns = df.columns.values.tolist()
        for i in range(min(len(spreadsheet_columns),len(expected_columns))):
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
        message = 'Error reading file: {e}'
        return df, succeeded, message

def names_to_df(sheet_data):
    df = sheet_data.rename(mapper=mfo.admin.spreadsheet_columns.names, axis=1)
    return df

def all_profiles(input_df):

    # First, find teachers and make a profile for each.
    # Note that we only get teachers' names in the spreadsheet
    # and do not have other teacher info unless they are also a
    # participant or an accompanist.

    teachers = input_df[['teacher']].dropna().drop_duplicates()

    for index, row in teachers.iterrows():

        teacher_name = str(row.teacher).strip()
        stmt = select(Profile).where(Profile.name == teacher_name)
        existing_teacher = db.session.execute(stmt).scalar_one_or_none()

        if existing_teacher:
            print(f"** Row {index + 2}: Teacher profile for {teacher_name} already exists")
        else:
            teacher_profile = Profile(name=teacher_name)
            db.session.add(teacher_profile)
            print(f"** Row {index + 2}: Teacher profile for {teacher_name} added")

        try:
            db.session.commit()
        
        except IntegrityError:
            db.session.rollback()
            print(f"**** Row {index + 2}: Commit failed: Teacher profile for {teacher_name} already exists")
            
        except Exception as e:
            db.session.rollback()
            print(e)

    # Add group teachers from the large group entries
    group_teachers = input_df[['group_teacher']].dropna().drop_duplicates()

    for index, row in group_teachers.iterrows():
    
        group_teacher_name = str(row.group_teacher).strip()
        stmt = select(Profile).where(Profile.name == group_teacher_name)
        existing_teacher = db.session.execute(stmt).scalar_one_or_none()

        if existing_teacher:
            print(f"** Row {index + 2}: Group teacher profile for {group_teacher_name} already exists")
        else:
            teacher_profile = Profile(name=str(group_teacher_name))
            db.session.add(teacher_profile)
            print(f"** Row {index + 2}: Group Teacher {group_teacher_name}: added new record")

        try:
            db.session.commit()
        
        except IntegrityError:
            db.session.rollback()
            print(f"**** Commit Failed: Group Teacher profile for {group_teacher_name} already exists")
            
        except Exception as e:
            db.session.rollback()
            print(e)

    # Then, find all accompanists in the various accompanist columns
    # and create a list of accompanist column name tuples for the next step
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

    # In one set of name_*, phone_*, email_* accompanist columns, 
    # iterate through and find all unique combinations of values
    accompanists = []
    for index, row in input_df.iterrows():
        for name_col, phone_col, email_col in accompanist_columns:
            
            name = row[name_col]
            if pd.notna(name):
                name = str(name).strip()
                phone = row[phone_col]
                if pd.notna(phone):
                    phone = str(int(phone))
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

    # # Where the same accompanist has a different email or phone number
    # # in a different row in the spreadsheet, print a warning and 
    # # keep the current value
    #
    # # I am keeping this code in case I need it to build a "preview"
    # # step for analyzing errors before touching the database
    #
    # aggregated_data = []
    #
    # for row in accompanists:
    #     name = row['name']
    #     phone = row['phone']
    #     email = row['email']
    #     index = row['index']
    #
    #     if name not in aggregated_data:
    #         aggregated_data[name] = {'email': email, 'phone': phone, 'index': index}
    #     else:
    #         # Check for different email
    #         if aggregated_data[name]['email'] and email:
    #             if aggregated_data[name]['email'] != email:
    #                 print(f"** Info: Row {index +2}: Different email for {name}: '{email}'! Keeping the first one: {aggregated_data[name]['email']}")
    #         elif not aggregated_data[name]['email'] and email:
    #             aggregated_data[name]['email'] = email
    #
    #         # Check for different phone
    #         if aggregated_data[name]['phone'] and phone:
    #             if aggregated_data[name]['phone'] != phone:
    #                 print(f"** Info: Row {index +2}: Different phone for {name}: '{phone}'!. Keeping the first one: {aggregated_data[name]['phone']}")
    #         elif not aggregated_data[name]['phone'] and phone:
    #             aggregated_data[name]['phone'] = phone


    # accompanists are often also teachers, check if their name was already
    # entered as a teacher. If so, add email and phone if available
    for accompanist in accompanists:
        name = accompanist['name']
        phone = accompanist['phone']
        email = accompanist['email']
        index = accompanist['index']

        stmt = select(Profile).where(Profile.name == name)
        existing_accompanist = db.session.execute(stmt).scalar_one_or_none()

        if existing_accompanist:
            if pd.notna(existing_accompanist.phone) and pd.notna(existing_accompanist.email):
                print(
                    f"** Row {index +2}: Accompanist '{name}': "
                    f"already exists and has email and phone"
                )
                if pd.notna(phone) and (existing_accompanist.phone != phone):
                    print(
                        f"**** Row {index +2}: Accompanist '{name}': "
                        f"found a different phone number '{phone}'. "
                        f"Keeping original phone number '{existing_accompanist.phone}'"
                    )
                if pd.notna(email) and (existing_accompanist.email != email):
                    print(
                        f"**** Row {index +2}: Accompanist '{name}': "
                        f"found a different email '{email}'. "
                        f"Keeping original email '{existing_accompanist.email}'"
                    )
            if pd.isna(existing_accompanist.phone) and pd.notna(phone):
                existing_accompanist.phone = phone
                print(
                    f"** Row {index +2}: Accompanist {name}: "
                    f"add phone number to existing record"
                )
            if pd.isna(existing_accompanist.email) and pd.notna(email):
                existing_accompanist.email = email
                print(
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
            print(f"** Row {index +2}: Added accompanist '{name}', phone: '{phone}', email: '{email}'")
         
        try:
            db.session.commit()
            
        except IntegrityError:
            db.session.rollback()
            print(f"** Commit error: Row {index +2}: Accompanist profile for {name} {phone} {email} already exists")
            
        except Exception as e:
            db.session.rollback()
            print(e)

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
                    phone = str(int(participant.phone))
                else:
                    if pd.notna(participant.group_phone):
                        phone = str(int(participant.group_phone))
                    else:
                        phone = None

                # Continue to check for existing and add following profile items:
                # group_address
                # group_city
                # group_postal_code
                # group_province

                new_group = Profile(
                    group_name=group_name,
                    email=email,
                    phone=phone,
                    # group_address
                    # group_city
                    # group_postal_code
                    # group_province
                )
                db.session.add(new_group)
                print(f"** Row {index +2}: Group {group_name} {phone} {email}: added new record")

            else:
                print(f"** Row {index +2}: Group {group_name} {phone} {email}: already exists")

                # TODO: add code to fix email and phone numbers and other details, if in
                # spreadsheet row but not database row

            try:
                db.session.commit()
            
            except IntegrityError:
                db.session.rollback()
                print(f"**** Row {index +2}: Commit failed: Group {group_name} {phone} {email} already exists")
                
            except Exception as e:
                db.session.rollback()
                print(e)

        # Some participant first_name or last_name fields may be blank
        # Also, some have extra spaces before or after the first_name or last_name
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

                # Continue to check for existing and add following profile items:
                # date_of_birth,
                # gender,
                # address,
                # city,
                # postal_code,
                # province,

                new_participant = Profile(
                    name=full_name,
                    email=email,
                    phone=phone,
                    # date_of_birth,
                    # gender,
                    # address,
                    # city,
                    # postal_code,
                    # province,
                )
                db.session.add(new_participant)
                print(f"** Row {index +2}: Participant {full_name} {phone} {email}: added new record")
            else:
                print(f"** Row {index +2}: Participant {full_name} {email}: already exists")
                # But, add in details if the duplicate has more details than the existing
                if not existing_participant.phone:
                    if pd.notna(participant.phone):
                        phone = str(int(participant.phone))
                    else:
                        phone = None
                    if phone:
                        existing_participant.phone = phone
                        print(f"** Row {index +2}: Participant {full_name} {phone} {email}: added phone number")
                if not existing_participant.email:
                    if pd.notna(participant.email):
                        email = str(participant.email).lower()
                    else:
                        email = None
                    if email:
                        existing_participant.email = email
                        print(f"** Row {index +2}: Participant {full_name} {phone} {email}: added email")

            try:
                db.session.commit()
            
            except IntegrityError:
                db.session.rollback()
                print(f"**** Commit Failed 2: Row {index +2}: Participant {full_name} {email} already exists")
                
            except Exception as e:
                db.session.rollback()
                print(e)

        else:
            print(f"Spreadsheet error: Row {index +2}: invalid entry in 'group or individual' column: '{participant.type}'")


    # also consider case where accompanist, who is also participant, might 
    # have one email address for their accompanist role and another email 
    # for their participant role. Same for teachers

    # find schools and add an entry for them


def related_profiles(input_df):
    
    # Assign students to teachers 
    students_per_teacher = []
    students_and_teachers = input_df[['teacher', 'first_name', 'last_name']].dropna(how='all').drop_duplicates()

    for index, row in students_and_teachers.iterrows():
        if pd.notna(row.teacher):

            teacher_name = str(row.teacher).strip()
            student_first_name = row.first_name
            student_last_name = row.last_name

            if pd.isna(student_first_name):
                student_full_name = str(student_last_name).strip()
            elif pd.isna(student_last_name):
                student_full_name = str(student_first_name).strip()
            else:
                student_full_name = str(student_first_name).strip() + ' ' + str(student_last_name).strip()

            # now we have one instance of teacher_name and student_full_name
            stmt = select(Profile).where(Profile.name == teacher_name)
            teacher = db.session.execute(stmt).scalar_one_or_none()
            stmt = select(Profile).where(Profile.name == student_full_name)
            student = db.session.execute(stmt).scalar_one_or_none()

            if student in teacher.students:
                print(f"** Row {index +2}: Student {student_full_name} already associated with Teacher {teacher_name}")
            else:
                teacher.students.append(student)
                print(f"** Row {index +2}: Added Student {student_full_name} to Teacher {teacher_name}")

        try:
            db.session.commit()
            
        except IntegrityError:
                db.session.rollback()
                print(f"**** Commit Failed:Row {index +2}: Student {student_full_name} already associated with Teacher {teacher_name}")
                
        except Exception as e:
            db.session.rollback()
            print(e)

    # NOTE: accompanist relationship is in the entries, not directly to the student
    
    # Assign groups to teachers
    groups_and_teachers = input_df[['group_name', 'group_teacher']].dropna().drop_duplicates()

    for index, row in groups_and_teachers.iterrows():
        
        group_teacher_name = str(row.group_teacher).strip()

        stmt = select(Profile).where(Profile.name == group_teacher_name)
        teacher = db.session.execute(stmt).scalar_one_or_none()

        group_name = str(row.group_name).strip()
        stmt = select(Profile).where(Profile.group_name == group_name)
        group = db.session.execute(stmt).scalar_one_or_none()

        if group in teacher.group:
            print(f"**Row {index +2}: Group {group_name} already associated with Teacher {group_teacher_name}")
        else:
            teacher.group.append(group)
            print(f"** Row {index +2}: Added Group {group_name} to Teacher {group_teacher_name}")

        try:
            db.session.commit()
            
        except IntegrityError:
                db.session.rollback()
                print(f"**** Commit Failed: Row {index +2}: Group {group_name} already associated with Teacher {group_teacher_name}")
                
        except Exception as e:
            db.session.rollback()
            print(e)


def classes(input_df):

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

    for index, row in input_df.iterrows():
        for class_num_col, class_suf_col in class_columns:
            number = row[class_num_col]
            suffix = row[class_suf_col]

            if pd.notna(number) & pd.isna(suffix):
                if isinstance(number, (int, float)):
                    number=str(int(number))
                else:
                    number=number.strip()
                suffix = None
                good_number = True
            elif pd.notna(number) & pd.notna(suffix):
                if isinstance(number, (int, float)):
                    number=str(int(number))
                else:
                    number=number.strip()
                suffix = str(suffix).strip()
                good_number = True
            elif pd.isna(number) & pd.notna(suffix):
                print(f"**** Row {index+2}: Error: Class number missing")
                good_number = False
            elif pd.isna(number) & pd.isna(suffix):
                good_number = False
            else:
                pass

            if good_number:
                # Get last number in column name
                parts = class_num_col.rsplit('_', 1)
                if len(parts) > 1:
                    col_num = str(parts[-1]) 
                else:
                    col_num = str(class_num_col)
                
                type = class_column_type[col_num]
                repertoire_columns = class_repertoire_columns[col_num]
                
                # TEST CODE
                #print(input_df.columns.tolist())

                test_pieces = []

                for columns in repertoire_columns:
                    # TEST CODE
                    #print(columns)
                    title_col = columns['title']
                    duration_col = columns['duration']
                    composer_col = columns['composer']

                    title = row[title_col]
                    duration = row[duration_col]
                    composer = row[composer_col]

                    # TEST CODE
                    # print(index, "   ", title_col, "   ", title)
                    # print(index, "   ", duration_col, "   ", duration)
                    # print(index, "   ", composer_col, "   ", composer)

                    if pd.notna(title) and pd.notna(composer):

                        title = str(title).strip()
                        if pd.notna(duration):
                            duration = int(duration)
                        else:
                            duration = None
                        composer = str(composer)

                        test_pieces.append(
                            {
                                'title': title,
                                'duration': duration,
                                'composer': composer
                            }
                        )

                        title = None
                        composer = None

                classes.append({'number': number, 'suffix': suffix, 'type': type, 'test_pieces': test_pieces, 'index': index})


    
    # Now we have a list of class entries but probably many duplicate class/suffixes
   
    for row in classes:
        number = row['number']
        suffix = row['suffix']
        index = row['index']
        type = row['type']
        test_pieces = row['test_pieces']

        # TEST CODE
        # print('TEST_PIECES FROM LIST', test_pieces)

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
            print(f"** Row {index+2}: Class {number}{print_suffix}, type: {type}, already exists")

            if pd.notna(festival_class.class_type):
                if festival_class.class_type != type:
                    print(f"**** Row {index+2}: Class {number}{print_suffix} may be recorded as wrong type.\n  ** It was previously recorded as type: {festival_class.class_type} and has been found again as type: {type}\n  ** Currently-recorded type will remain unchanged")
                    type = festival_class.class_type
                    
            existing_pieces = {(piece.title, piece.composer) for piece in festival_class.test_pieces}
            
            for test_piece in test_pieces:
                title = test_piece['title']
                duration = test_piece['duration']
                composer = test_piece['composer']

                # TEST CODE
                # print('TP TITLE FROM LIST: ', title)
                # print('TP COMPOSER FROM LIST: ', composer)

                if (title, composer) in existing_pieces:
                    # TEST CODE
                    # print('EXISTING TEST PIECE')
                    
                    # Existing piece matches
                    continue
                else:
                    new_piece = Repertoire(
                        title=title,
                        duration=duration,
                        composer=composer,
                        # description
                    )
                    festival_class.test_pieces.append(new_piece)
                    print(f"** Row {index+2}: Added test piece '{title}' by '{composer}' to class '{number}{print_suffix}'")

        else:
            new_festival_class = FestivalClass(
                number=number,
                suffix=suffix,
                # description,
                class_type=type,
                # fee,
                # discipline,
                # adjudication_time,
                # move_time,
            )
            print(f"** Row {index+2}: Class {number}{print_suffix}, type: {type},  added")

            for x in test_pieces:

                title = x['title']
                duration = x['duration']
                composer = x['composer']

                if pd.notna(title) and pd.notna(composer):
                    new_piece = Repertoire(
                        title=title,
                        duration=duration,
                        composer=composer,
                        # description
                    )
                    new_festival_class.test_pieces.append(new_piece)
                    print(f"** Row {index+2}: Added test piece '{title}' by '{composer}' to class '{number}{print_suffix}'")

            db.session.add(new_festival_class)
            
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                print(f"**** Row {index+2}: Commit failed: Class {number}{print_suffix} already exists")
            except Exception as e:
                db.session.rollback()
                print(e)


def schools(input_df):
    # Create dataframe containing unique school names

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

    # Populate schools database table
    for school_name in school_names:
        name = school_name['name']
        index = school_name['index']

        stmt = select(School).where(
            School.name == name,
        )
        existing_school = db.session.execute(stmt).scalar_one_or_none()

        if existing_school:
            print(f"** Row {index+2}: School '{name}' already exists **")
        else:
            new_school = School(name=name)

            db.session.add(new_school)
            print(f"** Row {index+2}: School {name} added")
    
            try:
                db.session.commit()
                
            except IntegrityError:
                    db.session.rollback()
                    print(f"**** Row {index+2}: Commit error: School '{school_name}' already exists **")
                    
            except Exception as e:
                db.session.rollback()
                print(e)

    # Associate students with schools
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

            # Some participant first_name or last_name fields may be blank
            # Also, some have extra spaces before or after the first_name or last_name
            
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
                print(f"** Row {index+2}: Student '{student_full_name}' already associated with School: '{school_name}'")
            else:
                school.students_or_groups.append(student)
                print(f"** Row {index+2}: Added Student '{student_full_name}' to School: '{school_name}'")
            
            if teacher in school.teachers:
                print(f"** Row {index+2}: Teacher '{teacher_name}' already associated with School: '{school_name}'")
            else:
                school.teachers.append(teacher)
                print(f"** Row {index+2}: Added teacher '{teacher_name}' to School: '{school_name}'")
            
        try:
            db.session.commit()
            
        except IntegrityError:
                db.session.rollback()
                print(f"**** Row {index+2}: Commit failed: Student or Teacher already associated with School: '{school_name}'")
                
        except Exception as e:
            db.session.rollback()
            print(e)

    # Associate groups and group teachers with schools
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
                print(f"** Row {index+2}: Group {group_name} already associated with School {group_school}")
            else:
                school.students_or_groups.append(group)
                print(f"** Row {index+2}: Added Group {group_name} to School {group_school}")

            if teacher in school.teachers:
                print(f"** Row {index+2}: Group Teacher {group_teacher} already associated with School {group_school}")
            else:
                school.teachers.append(teacher)
                print(f"** Row {index+2}: Added Group Teacher {group_teacher} to School {group_school}")

            try:
                db.session.commit()
                
            except IntegrityError:
                    db.session.rollback()
                    print(f"**** Row {index+2}: Commit Failed: Group or Group Teacher already associated with School {group_school}")
                    
            except Exception as e:
                db.session.rollback()
                print(e)

    # Associate teachers with schools



def repertoire(input_df):
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
                    print(f"**** Row: {index+2}: Repertoire has missing title")
                    title = None

                if pd.notna(duration):
                    if isinstance(duration, (int, float)):
                        duration=int(duration)
                    else:
                        print(f"**** Row: {index+2}: Repertoire has invalid duration: '{duration}'")
                        duration = None
                else:
                    print(f"**** Row: {index+2}: Repertoire has invalid duration: '{duration}'")
                    duration = None

                if pd.notna(composer):
                    if isinstance(composer, (int, float)):
                        print(f"**** Row: {index+2}: Repertoire has invalid composer: '{composer}'")
                        composer = None
                    else:
                        composer = str(composer).strip()      
                else:
                    print(f"**** Row: {index+2}: Repertoire has invalid composer: '{composer}'")
                    composer = None
            
                repertoire_pieces.append({'title': title, 'duration': duration, 'composer': composer, 'index': index})

    # List 'repertoire_pieces' contains all repertoire items, 
    # many of which are duplicates
    

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
            print(f"** Row: {index+2}: Repertore {title} by {composer} already exists **")
            if existing_repertoire.duration != duration:
                print(f"   **** Row: {index+2}: Current duration was {existing_repertoire.duration} minutes long, duplicate entry was {duration} minutes long")
        else:
            new_repertoire = Repertoire(
                title=title,
                duration=duration,
                composer=composer,
                # description
            )

            db.session.add(new_repertoire)
            print(f"** Row: {index+2}: Repertore {title} by {composer} duration {duration} minutes added")

            try:
                db.session.commit()

            except IntegrityError:
                    db.session.rollback()
                    print(f"**** Row: {index+2}: Commit Failed: Repertore {title} by {composer} already exists **")

            except Exception as e:
                db.session.rollback()
                print(e)





def entries(input_df):
    """
    Entries are usually associated with one name but sometimes the same 
    person makes two entries. In the case of the second entry, it looks
    like they are adding a class or repertoire.
    e-mail address is not always belonging to participant because often
    teachers or parents create the entry on their behalf
    """

    pass

    # for index, row in input_df.iterrows():

    #     # group or individual entry?
    #     group_or_individual = str(row.type).strip().lower()
    #     if group_or_individual == "group participant":
            
    #         pass
    #     else:
    #         pass


    #     # create full name and get student profile
    #     participant_first_name = row.first_name
    #     participant_last_name = row.last_name
    #     participant

    #     if pd.isna(student_first_name):
    #         student_full_name = str(student_last_name).strip()
    #     elif pd.isna(student_last_name):
    #         student_full_name = str(student_first_name).strip()
    #     else:
    #         student_full_name = str(student_first_name).strip() + ' ' + str(student_last_name).strip()

    #     stmt = select(Profile).where(Profile.name == student_full_name)
    #     student = db.session.execute(stmt).scalar_one_or_none()
    





def convert_to_db(sheet_data):
    df = names_to_df(sheet_data)
    all_profiles(df)
    related_profiles(df)
    repertoire(df)
    classes(df)
    schools(df)
    entries(df)

