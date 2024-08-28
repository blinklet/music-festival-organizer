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

    existing_classes = []
    
    try:
        # find all rows in combined_df that have the same number
        grouped_df = combined_df.groupby('number')
        for number, group in grouped_df:
            # get list of classes with the same number from the database
            stmt = sa.select(FestivalClass).where(FestivalClass.number == number)
            db_classes = db.session.execute(stmt).scalars().all()
            # if there are no classes with the same number in the database, add all the rows in the group
            if not db_classes:
                for index, row in group.iterrows():
                    
                    suffix, class_type, discipline = infer_attributes(row)

                    festival_class = FestivalClass(
                    number=row.number, 
                    suffix=suffix, 
                    name=row.description, 
                    class_type=class_type,
                    discipline=discipline,
                    fee=row.fee)
                    db.session.add(festival_class)
                    existing_classes.append((row.number, suffix))
                    
            else:
                # Update existing classes in the database with information from the dataframe
                for db_class in db_classes:
                    for index, row in group.iterrows():
                        suffix, class_type, discipline = infer_attributes(row)
                        if (db_class.number, db_class.suffix) == (row.number, suffix):
                            db_class.name = row.description
                            db_class.class_type = class_type
                            db_class.discipline = discipline
                            db_class.fee = row.fee
                            db.session.add(db_class)
                            existing_classes.append((row.number, suffix))
                            break
                
                # Add new classes from the dataframe to the database
                for index, row in group.iterrows():
                    suffix, class_type, discipline = infer_attributes(row)
                    if (row.number, suffix) not in existing_classes:
                        festival_class = FestivalClass(
                            number=row.number, 
                            suffix=suffix, 
                            name=row.description, 
                            class_type=class_type,
                            discipline=discipline,
                            fee=row.fee)
                        db.session.add(festival_class)
                        existing_classes.append((row.number, suffix))

                # Add class from the database that are not in the dataframe, 
                # using the fields from the first row in the dataframe group
                for db_class in db_classes:
                    row = group.iloc[0]
                    if (db_class.number, db_class.suffix) not in existing_classes:
                        db_class.name = row.description
                        db_class.class_type = class_type
                        db_class.discipline = discipline
                        db_class.fee = row.fee
                        db.session.add(db_class)
                        existing_classes.append((row.number, suffix))

        flask.flash("Syllabus added to database.", "success")
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flask.flash(f"Error adding Syllabus to database: {e}. Database not updated.", "danger")
        # issues.append(f"**** Error adding Syllabus to database: {e}")

def infer_attributes(row):
    """
    Fill in "class_type" and "discipline" by inferring information from the 
    class number (which seems to correspond with discipline) and keywords 
    in the class description like "Solo" and "Trio".
    """

    if row.suffix == "":
        suffix = None
    else:
        suffix = row.suffix

    class_number = int(row['number'])
    class_description = row['description']

    # Infer discipline based on class number
    if 200 <= class_number <= 706:
        discipline = "Vocal Ensemble"
    elif 1000 <= class_number <= 1999:
        discipline = "Vocal"
    elif 2000 <= class_number <= 2899:
        discipline = "Piano"
    elif 2900 <= class_number <= 2999:
        discipline = "Organ"
    elif 3000 <= class_number <= 3999:
        discipline = "Strings"
    elif 4000 <= class_number <= 4099:
        discipline = "Strings"  # Guitar
    elif 4100 <= class_number <= 4299:
        discipline = "Recorder"
    elif 4300 <= class_number <= 4399:
        discipline = "Strings" # Ukulele
    elif 4400 <= class_number <= 4999:
        discipline = "Strings"  # Harp
    elif 5000 <= class_number <= 5999:
        discipline = "Woodwinds"
    elif 6000 <= class_number <= 6999:
        discipline = "Brass"
    elif 7000 <= class_number <= 7999:
        discipline = "Percussion"
    elif 8000 <= class_number <= 8999:
        discipline = "Instrumental"
    elif 9000 <= class_number <= 9999:
        discipline = "Musical Theatre"
    else:
        discipline = None

    # Infer class type based on keywords in class description
    keywords = class_description.lower().split()
    if "solo" in keywords:
        class_type = "Solo"
    elif "recital" in keywords:
        class_type = "Recital"
    elif "duet" in keywords:
        class_type = "Duet"
    elif "trio" in keywords:
        class_type = "Trio"
    elif "quartet" in keywords:
        class_type = "Quartet"
    elif "quintet" in keywords:
        class_type = "Quintet"
    elif "composition" in keywords:
        class_type = "Composition"
    elif any(keyword in keywords for keyword in ["ensemble", "band", "orchestra", "consort", "group"]):
        class_type = "Ensemble"
    else:
        class_type = "Solo"

    return (suffix, class_type, discipline)



def add_to_db(pdf_file):
    """Add the contents of the pdf file to the database."""
    succeeded, combined_df = to_table(pdf_file)
    if succeeded:
        load_database(combined_df)
