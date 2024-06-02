# mfo/admin/spreadsheet.py

# Functions and Classes that support reading data from 
# spreadsheets and importing it into the SQL database

import pandas as pd
import io
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import flask

import mfo.admin.spreadsheet_columns
import mfo.utilities
from mfo.database.base import db
from mfo.database.profiles import Profile

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
        teacher_profile = Profile(first_name=str(first_name), last_name=str(last_name))
        
        results = []

        try:
            db.session.add(teacher_profile)
            db.session.commit()
        
        except IntegrityError:
            db.session.rollback()
            print(f"** Teacher profile for {first_name} {last_name} already exists")
            
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
        phone = str(aggregated_data[accompanist]['phone'])
        email = str(aggregated_data[accompanist]['email'])

        stmt = select(Profile).where(
            Profile.first_name == str(first_name), 
            Profile.last_name == str(last_name)
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
            print(f"** Accompanist profile for {first_name} {last_name} already exists")
            
        except Exception as e:
            db.session.rollback()
            print(e)


    # find schools and add an entry for them


def secondary_profiles(sheet_data):
    pass

def entries(sheet_data):
    pass

def classes(sheet_data):
    pass

def schools(sheet_data):
    pass

def repertoire(sheet_data):
    pass





def convert_to_db(sheet_data):
    df = names_to_df(sheet_data)
    all_profiles(df)
    # print(df[['email', 'first_name', 'last_name', 'date_of_birth']].head())

