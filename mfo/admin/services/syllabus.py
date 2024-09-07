import pandas as pd
import flask
import tabula
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import io

from mfo.database.base import db
from mfo.database.models import FestivalClass
from mfo.admin.services.admin_services import infer_attributes
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

    existing_classes = []
    
    try:
        # find all rows in combined_df that have the same number
        grouped_df = combined_df.groupby('number')
        for number, group in grouped_df:
            # get list of classes with the same number from the database
            stmt = sa.select(FestivalClass).where(FestivalClass.number == number)
            db_classes = db.session.execute(stmt).scalars().all()
            # if there are no classes with the same number in the database, 
            # add all the rows in the group
            if not db_classes:
                for index, row in group.iterrows():
                    suffix, class_type, discipline = infer_attributes(row)
                    if (row.number, suffix) not in existing_classes:
                        festival_class = FestivalClass(
                            number=row.number, 
                            suffix=suffix, 
                            name=row.description, 
                            class_type=class_type,
                            discipline=discipline,
                            fee=row.fee,
                            adjudication_time = flask.current_app.config["DEFAULT_ADJUDICATION_TIME"][discipline][class_type],
                            move_time = flask.current_app.config["DEFAULT_MOVE_TIME"][discipline][class_type],
                            )

                        db.session.add(festival_class)
                    existing_classes.append((row.number, suffix))
                    
            else:
                # If at least one class with the same number exists in the database,
                # update existing classes in the database with information from the dataframe
                for db_class in db_classes:
                    for index, row in group.iterrows():
                        suffix, class_type, discipline = infer_attributes(row)
                        if (row.number, suffix) not in existing_classes:
                            if (db_class.number, db_class.suffix) == (row.number, suffix):
                                db_class.name = row.description
                                db_class.class_type = class_type
                                db_class.discipline = discipline
                                db_class.fee = row.fee

                                # overwrite adjudication_time and move_time with defaults, if none exist
                                if pd.isna(db_class.adjudication_time):
                                    db_class.adjudication_time = flask.current_app.config["DEFAULT_ADJUDICATION_TIME"][discipline][class_type]
                                
                                if pd.isna(db_class.move_time):
                                    db_class.move_time = flask.current_app.config["DEFAULT_MOVE_TIME"][discipline][class_type]

                                db.session.add(db_class)
                                existing_classes.append((row.number, suffix))

                # Update classes from the database that are not in the dataframe group, 
                # using the fields from the first row in the dataframe group
                for db_class in db_classes:
                    row = group.iloc[0]
                    suffix, class_type, discipline = infer_attributes(row)
                    if (db_class.number, db_class.suffix) not in existing_classes:
                        db_class.name = row.description
                        db_class.class_type = class_type
                        db_class.discipline = discipline
                        db_class.fee = row.fee

                        if pd.isna(db_class.adjudication_time):
                            db_class.adjudication_time = flask.current_app.config["DEFAULT_ADJUDICATION_TIME"][discipline][class_type]
                                
                        if pd.isna(db_class.move_time):
                            db_class.move_time = flask.current_app.config["DEFAULT_MOVE_TIME"][discipline][class_type]

                        db.session.add(db_class)
                        existing_classes.append((row.number, suffix))

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
