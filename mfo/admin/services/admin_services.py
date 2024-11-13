# mfo/admin/services/admin_services.py

from sqlalchemy import select
import pandas as pd

from mfo.database.base import db
from mfo.database.models import Profile
from mfo.config import TEST_LEVEL_MAP

level_map = pd.read_json(TEST_LEVEL_MAP, orient='records')

def infer_discipline(class_number):
    """ Infer discipline based on class number """
    if 200 <= class_number <= 706:
        return "Vocal" # Ensemble
    elif 1000 <= class_number <= 1999:
        return "Vocal"
    elif 2000 <= class_number <= 2899:
        return "Piano"
    elif 2900 <= class_number <= 2999:
        return "Organ"
    elif 3000 <= class_number <= 3999:
        return "Strings"
    elif 4000 <= class_number <= 4099:
        return "Strings"  # Guitar
    elif 4100 <= class_number <= 4299:
        return "Recorder"
    elif 4300 <= class_number <= 4399:
        return "Strings" # Ukulele
    elif 4400 <= class_number <= 4999:
        return "Strings"  # Harp
    elif 5000 <= class_number <= 5999:
        return "Woodwinds"
    elif 6000 <= class_number <= 6999:
        return "Brass"
    elif 7000 <= class_number <= 7999:
        return "Percussion"
    elif 8000 <= class_number <= 8999:
        return "Instrumental"
    elif 9000 <= class_number <= 9999:
        return "Musical Theatre"
    else:
        return None
    

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
    discipline = infer_discipline(class_number)

    # Infer class type based on keywords in class description
    keywords = class_description.lower().split()
    if any(keyword in keywords for keyword in [
        "solo", "solos", "concerto", "concertos", "sonata", "sonatas"
        ]):
        class_type = "Solo"
    elif any(keyword in keywords for keyword in ["recital", "recitals"]):
        class_type = "Recital"
    elif any(keyword in keywords for keyword in ["duet", "duets"]):
        class_type = "Duet"
    elif any(keyword in keywords for keyword in ["trio", "trios"]):
        class_type = "Trio"
    elif any(keyword in keywords for keyword in ["quartet", "quartets"]):
        class_type = "Quartet"
    elif any(keyword in keywords for keyword in ["quintet", "quintets"]):
        class_type = "Quintet"
    elif any(keyword in keywords for keyword in ["composition", "compositions"]):
        class_type = "Composition"
    elif any(keyword in keywords for keyword in [
        "choir", "chorus", "ensemble", "band", 
        "orchestra", "consort", "group", "ensembles",
        "groups"
        ]):
        class_type = "Ensemble"
    else:
        class_type = "Solo"

    # Infer level based on class description and levels_map
    level = None
    for index, row in level_map.iterrows():
        key = row['text'].lower()
        desc = class_description.lower()
        if key in desc:
            level = row['level']
            break

    if level is None:
        level = "none"

    return (suffix, class_type, discipline, level)