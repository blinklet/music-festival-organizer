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
from mfo.database.models import Profile, FestivalClass

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

    # First, find teachers and make a profile for each
    for teacher in input_df.teacher.dropna().drop_duplicates():
        first_name, last_name = mfo.utilities.parse_full_name(teacher)
        stmt = select(Profile).where(
            Profile.first_name == first_name, 
            Profile.last_name == last_name,
        )
        existing_teacher = db.session.execute(stmt).scalar_one_or_none()

        if existing_teacher:
            print(f"** Teacher profile for {first_name} {last_name} already exists")
        else:
            teacher_profile = Profile(first_name=str(first_name), last_name=str(last_name))
            db.session.add(teacher_profile)

        try:
            db.session.commit()
        
        except IntegrityError:
            db.session.rollback()
            print(f"** Commit failed: Teacher profile for {first_name} {last_name} already exists")
            
        except Exception as e:
            db.session.rollback()
            print(e)

    # Then, find all accompanists in the various accompanist columns
    # and make a profile for each
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

    # In one set of name_*, phone_*, email_* columns, iterate through and find
    # all unique combinations
    accompanists = []
    for index, row in input_df.iterrows():
        for name_col, phone_col, email_col in accompanist_columns:
            name = row[name_col]
            if pd.notna(name):
                phone = row[phone_col]
                if pd.notna(phone):
                    phone = str(int(phone))
                else:
                    phone = None
                email = row[email_col]
                if pd.notna(email):
                    email = str(email)
                else:
                    email = None
                accompanists.append({'name': name, 'phone': phone, 'email': email})
            else:
                pass

    aggregated_data = {}

    for row in accompanists:
        name = row['name']
        phone = row['phone']
        email = row['email']
        
        if name not in aggregated_data:
            aggregated_data[name] = {'email': email, 'phone': phone}
        else:
            # Check for different email
            if aggregated_data[name]['email'] and email and aggregated_data[name]['email'] != email:
                print(f"Warning: Different email for {name}: '{email}'! Keeping the first one: {aggregated_data[name]['email']}")
            elif not aggregated_data[name]['email'] and email:
                aggregated_data[name]['email'] = email
            
            # Check for different phone
            if aggregated_data[name]['phone'] and phone and aggregated_data[name]['phone'] != phone:
                print(f"Warning: Different phone for {name}: '{phone}'!. Keeping the first one: {aggregated_data[name]['phone']}")
            elif not aggregated_data[name]['phone'] and phone:
                aggregated_data[name]['phone'] = phone

    # accompanists are often also teachers, check if their name was already
    # entered as a teacher. If so, add email and phone if available
    for accompanist in aggregated_data.keys():
        first_name, last_name = mfo.utilities.parse_full_name(accompanist)
        phone = aggregated_data[accompanist]['phone']
        email = aggregated_data[accompanist]['email']

        stmt = select(Profile).where(
            Profile.first_name == first_name, 
            Profile.last_name == last_name,
        )
        existing_accompanist = db.session.execute(stmt).scalar_one_or_none()

        if existing_accompanist:
            if existing_accompanist.phone and existing_accompanist.email:
                print(f"** Accompanist {first_name} {last_name}: already exists and has email and phone")
            if not existing_accompanist.phone and phone:
                existing_accompanist.phone = phone
                print(f"** Accompanist {first_name} {last_name}: add phone number to existing record")
            if not existing_accompanist.email and email:
                existing_accompanist.email = email
                print(f"** Accompanist {first_name} {last_name}: add email to existing record")
        else:
            new_accompanist = Profile(
                first_name=str(first_name), 
                last_name=str(last_name),
                phone=phone,
                email=email,
            )
            db.session.add(new_accompanist)
            print(f"** Accompanist {first_name} {last_name} {phone} {email}: added new record")
         
        try:
            db.session.commit()
            
        except IntegrityError:
            db.session.rollback()
            print(f"** Accompanist profile for {first_name} {last_name} {phone} {email} already exists")
            
        except Exception as e:
            db.session.rollback()
            print(e)

    # Now, add groups details
    #     'group_name_15',
    #     'group_address_15',
    #     'group_city_15',
    #     'group_postal_code_15',
    #     'group_province_15',
    #     'group_phone_15',
    #     'group_school_15',
    for index, participant in input_df.iterrows():
        if participant.type == "Group participant":
            group_name = participant.group_name_15
            email = participant.email
            stmt = select(Profile).where(
                Profile.group_name == group_name,
            )
            existing_group = db.session.execute(stmt).scalar_one_or_none()
            if not existing_group:
                if pd.notna(participant.phone):
                    phone = str(int(participant.phone))
                else:
                    if pd.notna(participant.group_phone_15):
                        phone = str(int(participant.group_phone_15))
                    else:
                        phone = None

                new_group = Profile(
                    group_name=group_name,
                    email=email,
                    phone=phone
                )
                db.session.add(new_group)
                print(f"** Group {group_name} {phone} {email}: added new record")

            else:
                print(f"** Group {group_name} {phone} {email}: already exists")
                # TODO: add code to fix email and phone numbers and other datils, if in
                # spreadsheet row but not database row

            try:
                db.session.commit()
            
            except IntegrityError:
                db.session.rollback()
                print(f"** Commit failed: Group {group_name} {phone} {email} already exists")
                
            except Exception as e:
                db.session.rollback()
                print(e)

        elif participant.type == "Individual participant (Solo, Recital, Duet, Trio,  Quartet, or Quintet Class)":
            first_name = participant.first_name
            last_name = participant.last_name
            email = participant.email
            
            stmt = select(Profile).where(
                Profile.first_name == first_name,
                Profile.last_name == last_name,
            )

            existing_participant = db.session.execute(stmt).scalar_one_or_none()
            if not existing_participant:
                if pd.notna(participant.phone):
                    phone = str(int(participant.phone))
                else:
                    phone = None
                new_participant = Profile(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone
                )
                db.session.add(new_participant)
                print(f"** Participant {first_name} {last_name} {phone} {email}: added new record")
            else:
                print(f"** Participant {first_name} {last_name} {email}: already exists")
                # But, add in details if the duplicate has more details than the existing
                if not existing_participant.phone:
                    if pd.notna(participant.phone):
                        phone = str(int(participant.phone))
                    else:
                        phone = None
                    if phone:
                        existing_participant.phone = phone
                        print(f"** Participant {first_name} {last_name} {phone} {email}: added phone number")
                if not existing_participant.email:
                    if pd.notna(participant.email):
                        email = participant.email
                    else:
                        email = None
                    if email:
                        existing_participant.email = email
                        print(f"** Participant {first_name} {last_name} {phone} {email}: added email")

            try:
                db.session.commit()
            
            except IntegrityError:
                db.session.rollback()
                print(f"** Commit failed 2: Participant {first_name} {last_name} {email} already exists")
                
            except Exception as e:
                db.session.rollback()
                print(e)

        else:
            print(f"Spreadsheet error: invalid entry in 'group or individual' column: '{participant.type}'")


    # also consider case where accompanist, who is also participant, might 
    # have one email address for their accompanist role and another email 
    # for their participant role. Same for teachers

    # find schools and add an entry for them


def related_profiles(input_df):
    
    # Assign students to teachers 

    # Combine student first name and last name into a list of tuples
    input_df['student_tuple'] = list(zip(input_df['first_name'], input_df['last_name']))
    # Group by teacher and aggregate the student tuples into a list
    students_per_teacher = input_df.groupby('teacher')['student_tuple'].apply(lambda x: list(x.dropna())).reset_index()
    # rename 'student_tuple' column to 'students', because it will contain a list of student tuples
    students_per_teacher.columns = ['teacher_name', 'students']
    # Filter out teachers with no students
    students_per_teacher = students_per_teacher[students_per_teacher['students'].map(len) > 0]

    for index, row in students_per_teacher.iterrows():
        # get teacher name
        teacher_first_name, teacher_last_name = mfo.utilities.parse_full_name(row.teacher_name)
        stmt = select(Profile).where(
            Profile.first_name == teacher_first_name,
            Profile.last_name == teacher_last_name,
        )
        teacher = db.session.execute(stmt).scalar_one_or_none()

        for student_first_name, student_last_name in row.students:
            stmt = select(Profile).where(
                Profile.first_name == student_first_name,
                Profile.last_name == student_last_name,
            )
            student = db.session.execute(stmt).scalar_one_or_none()
            if student in teacher.students:
                print(f"** Student {student_first_name} {student_last_name} already associated with Teacher {teacher_first_name}, {teacher_last_name}")
            else:
                teacher.students.append(student)
                print(f"** Added Student {student_first_name} {student_last_name} to Teacher {teacher_first_name}, {teacher_last_name}")

        try:
            db.session.commit()
            
        except IntegrityError:
                db.session.rollback()
                print(f"** Commit failed: Student {student_first_name} {student_last_name} already associated with Teacher {teacher_first_name}, {teacher_last_name}")
                
        except Exception as e:
            db.session.rollback()
            print(e)

    # # Find all accompanists in the various accompanist columns
    # accompanist_name_columns = [
    #     col for col in input_df.columns if col.startswith('accompanist_name_')
    #     ]

    # accompanists_df = input_df[accompanist_name_columns]
    # accompanists = accompanists_df.values.flatten()
    # accompanists = accompanists[~pd.isna(accompanists)]
    # accompanists = pd.unique(accompanists)

    # # for each accompanist, find associated students
    # for accompanist_name in accompanists:
    #     accompanist_first_name, accompanist_last_name = mfo.utilities.parse_full_name(accompanist_name)
    #     print(accompanist_first_name, accompanist_last_name)

    




def classes(input_df):
    """
    Parse through dataframe, find all class-related columns.
    Class columns have format like below, and there could be many
    'class_number_x',
    'class_suffix_x'

    After you get the column names, parse through all column pairs and 
    generate a list of tuples that identify each unique class number/suffix
    """
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

    class_pairs = set()
    
    for num_col, suf_col in class_columns:
        for num, suf in zip(input_df[num_col], input_df[suf_col]):
            if not pd.isna(num) and not pd.isna(suf):
                class_pairs.add((str(int(num)), suf))
    
    for class_number, class_suffix in list(class_pairs):
        stmt = select(FestivalClass).where(
            FestivalClass.number == class_number,
            FestivalClass.suffix == class_suffix,
        )
        festival_class = db.session.execute(stmt).scalar_one_or_none()

        if festival_class:
            print(F"Class {class_number}{class_suffix} already exists")
        else:
            new_festival_class = FestivalClass(
                number=class_number,
                suffix=class_suffix,
                # description
                # class_type
                # fee
                # discipline
                # adjudication_time
                # move_time
                # test_pieces
            )

            db.session.add(new_festival_class)
            print(f"** Class {class_number}{class_suffix} added")
    
            try:
                db.session.commit()
                
            except IntegrityError:
                    db.session.rollback()
                    print(f"** Commit failed: Class {class_number}{class_suffix} already exists")
                    
            except Exception as e:
                db.session.rollback()
                print(e)



    

def schools(sheet_data):
    pass

def repertoire(sheet_data):
    pass


def entries(sheet_data):
    pass


def convert_to_db(sheet_data):
    df = names_to_df(sheet_data)
    all_profiles(df)
    related_profiles(df)
    classes(df)
    # print(df[['email', 'first_name', 'last_name', 'date_of_birth']].head())

