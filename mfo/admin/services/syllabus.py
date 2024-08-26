import pandas as pd
import flask
import tabula
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import io

from mfo.database.base import db
from mfo.database.models import FestivalClass
import mfo.utilities


def verify_pdf(tables):
    """Verify that the tables extracted from the PDF file are in the expected format."""

    if not tables:
        flask.flash("No tables found in the PDF file. Database not updated.", "danger")
        print("PDF NO TABLES")
        return False
    
    for table in tables:
        if table.shape[1] != 4:
            flask.flash("PDF file table has wrong number of columns. Database not updated.", "danger")
            return False
        
    reference_columns = ['Unnamed: 0', 'Unnamed: 1', 'Class Based', 'Unnamed: 2']
    first_row_reference = ['Class Sec #','Description']

    if not all(table.columns == reference_columns):
        flask.flash("Wrong column headers in PDF file. Database not updated.", "danger")
        return False
    
    if not all(table.iloc[0, :2] == first_row_reference):
        flask.flash("Wrong column headers in PDF file. Database not updated.", "danger")
        return False

    return True
    



def to_table(pdf_file):
    """Convert the pdf file to a pandas dataframe."""

    tables = tabula.read_pdf(
            pdf_file,
            pages='all', 
            multiple_tables=True, 
            stream=True, 
            silent=True, 
            guess=True
            )
    
    if not verify_pdf(tables):
        return False, None

    combined_df = pd.DataFrame()

    for table in tables:
        
        # Drop the first 3 rows and reset the index
        df = table.drop(table.index[:2])  
        
        df.columns = ["number","description", "fee", "festival"]
        df["suffix"] = pd.Series(dtype="string")
        
        df.suffix = df.number.str[4:]
        df.number = df.number.str[0:4]
        
        df = df[["number", "suffix", "description", "fee"]]
        
        combined_df = pd.concat([combined_df, df], ignore_index=True)

        # Special case for the last page of the syllabus, drop rows where fee = "n/a"
        combined_df = combined_df[combined_df.fee != "n/a"]

    return True, combined_df


def load_database(combined_df):
    """
    Load the syllabus data into the database. Note that I do not 
    generate a list of issues here. I should probably do that.
    """
    # issues = mfo.utilities.CustomList()

    try:
        for index, row in combined_df.iterrows():

            # In dataframes converted from PDF, empty strings are not None, so we need to convert them
            if row.suffix == "":
                suffix = None
            else:
                suffix = row.suffix

            stmt = sa.select(FestivalClass).where(
                FestivalClass.number == row.number,
                FestivalClass.suffix == suffix,
            )
            festival_class = db.session.execute(stmt).scalar_one_or_none()

            if festival_class is None:
                festival_class = FestivalClass(number=row.number, suffix=suffix, name=row.description, fee=row.fee)
                db.session.add(festival_class)
            else:
                if festival_class.name == None:
                    # issues.append(f"**** Class {row['number']}{row['suffix']}: added description and fee from Syllabus")
                    festival_class.name = row.description
                    festival_class.fee = row.fee
                    db.session.add(festival_class)

        flask.flash("Syllabus added to database.", "success")
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flask.flash(f"Error adding Syllabus to database: {e}. Database not updated.", "danger")
        # issues.append(f"**** Error adding Syllabus to database: {e}")


def add_to_db(pdf_file):
    """Add the contents of the pdf file to the database."""
    succeeded, combined_df = to_table(pdf_file)
    if succeeded:
        load_database(combined_df)
