# mfo/admin/services/data_services.py

from werkzeug.exceptions import Forbidden
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select
import pandas as pd
from collections.abc import Sequence, Mapping

from mfo.database.base import db
from mfo.database.models import Profile, FestivalClass

def sort_key(x, column):
        """
        Retrieves the value associated with the specified key from a dictionary.
        If the key is not found, it returns None.
        """
        # Depending on which function calls the sort_list() function, 
        # I have to sort different lists that contain different types
        # of objects.
        # For example, a Profile object is not subscriptable, while
        # a dictionary is subscriptable.  
        # I need to check if the object is subscriptable
        # and if it is not, I need to get its key value differently.
        try:
            value = x[column]
        except (TypeError, KeyError, IndexError):
            value = getattr(x, column, None)
        # print(f"Sorting by {column}, value: {value}")  # Debug print
        return (value is not None, value)


def sort_list(list_to_sort, sort_by, sort_order):
    if sort_by is not None:
        for column, order in zip(sort_by, sort_order):
            if order == 'asc':
                list_to_sort = sorted(
                    list_to_sort, 
                    key=lambda x: sort_key(x, column)
                    )
            elif order == 'desc':
                list_to_sort = sorted(list_to_sort, 
                    key=lambda x: sort_key(x, column), 
                    reverse=True
                    )
            else:
                raise ValueError(f"Invalid sort order: {order}")

    return list_to_sort
    
    
            

def get_profiles(profile_type, sort_by=None, sort_order=None):
    stmt = select(Profile).where(Profile.roles.any(name=profile_type))
    profiles_list = db.session.execute(stmt).scalars().all()
    return sort_list(profiles_list, sort_by, sort_order)


def get_class_list(classes, sort_by=None, sort_order=None):
    class_list = list()
    for _class in classes:
        id = _class.id
        number = _class.number
        suffix = _class.suffix

        if pd.notna(number) & pd.isna(suffix):
            if isinstance(number, (int, float)):
                number_suffix = str(int(number)).zfill(4)
            else:
                number_suffix = number.strip()
        elif pd.notna(number) & pd.notna(suffix):
            if isinstance(number, (int, float)):
                number=str(int(number)).zfill(4)
            else:
                number=number.strip()
            suffix = str(suffix).strip()
            number_suffix = f"{number}{suffix}"
        
        name = _class.name
        type = _class.class_type
        if _class.fee:
            fee = int(_class.fee)
        else:
            fee = 0
        discipline = _class.discipline
        if _class.adjudication_time:
            adjudication_time = _class.adjudication_time
        else:
            adjudication_time = 0
        if _class.move_time:
            move_time = _class.move_time
        else:
            move_time = 0

        if _class.entries:
            number_of_entries = len(_class.entries)
            total_adjudication_time = adjudication_time * number_of_entries
            total_move_time = move_time * number_of_entries
            total_repertoire_time = sum([sum([repertoire.duration for repertoire in entry.repertoire]) for entry in _class.entries])
            total_time = total_adjudication_time + total_move_time + total_repertoire_time
            total_fees = fee * number_of_entries
        else:
            number_of_entries = 0
            total_adjudication_time = 0
            total_move_time = 0
            total_repertoire_time = 0
            total_fees = 0
            total_time = 0
        
        class_dict = {
            "id": id,
            "number_suffix": number_suffix,
            "number": number,
            "suffix": suffix,
            "name": name,
            "type": type,
            "fee": fee,
            "discipline": discipline,
            "adjudication_time": adjudication_time,
            "move_time": move_time,
            "number_of_entries": number_of_entries,
            "total_adjudication_time": total_adjudication_time,
            "total_move_time": total_move_time,
            "total_repertoire_time": total_repertoire_time,
            "total_fees": total_fees,
            "total_time": total_time
        }
        class_list.append(class_dict)

    return sort_list(class_list, sort_by, sort_order)


def get_repertoire_list(repertoire, sort_by=None, sort_order=None):
    repertoire_list = list()
    for piece in repertoire:

        if piece.used_in_entries:
            number_of_entries = len(piece.used_in_entries)
        else:
            number_of_entries = 0

        if piece.festival_classes:
            number_of_classes = len(piece.festival_classes)
        else:                
            number_of_classes = 0

        pieces_dict = {
            "id": piece.id,
            "title": piece.title,
            "composer": piece.composer,
            "discipline": piece.discipline,
            "type": piece.type,
            "level": piece.level,
            "duration": piece.duration,
            "entries": number_of_entries,
            "classes": number_of_classes
        }

        repertoire_list.append(pieces_dict)

    return sort_list(repertoire_list, sort_by, sort_order)