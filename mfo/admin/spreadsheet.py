# mfo/admin/spreadsheet.py

# Functions and Classes that support reading data from 
# spreadsheets and importing it into the SQL database

import pandas as pd
import io

import mfo.admin.spreadsheet_columns
import mfo.utilities

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

def users_primary_profiles(sheet_data):
    for teacher in sheet_data.teacher:
        print(teacher)
    

    # find accompanists and make a profile for them
    # find schools and add an entry for them

    pass

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
    # print(df[['email', 'first_name', 'last_name', 'date_of_birth']].head())

