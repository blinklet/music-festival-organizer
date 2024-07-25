# mfo/admin/services/data_services.py

from werkzeug.exceptions import Forbidden
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select
import pandas as pd

from mfo.database.base import db
from mfo.database.models import Profile, FestivalClass


def get_profiles(profile_type, sort_by=None):
    if sort_by == 'name':
        stmt = select(Profile).where(Profile.roles.any(name=profile_type)).order_by(Profile.name, Profile.email)
    elif sort_by == 'email':
        stmt = select(Profile).where(Profile.roles.any(name=profile_type)).order_by(Profile.email, Profile.name)
    else:
        stmt = select(Profile).where(Profile.roles.any(name=profile_type))
    return db.session.execute(stmt).scalars().all()


def get_class_list(classes, sort_by=None):
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
            fee = _class.fee
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

        if sort_by == 'number_suffix':
            class_list = sorted(
                class_list, 
                key=lambda x: (
                    x[sort_by] is not None, 
                    x[sort_by] or ''
                    )
                )
        elif sort_by is not None:
            class_list = sorted(
                class_list, 
                key=lambda x: (
                    x[sort_by] is not None, # Move None values to the start
                    x[sort_by] or '', # Use empty string as fallback for None values
                    x['number_suffix'] or '' # Add a secondary sort key to ensure consistent ordering
                    )
                )
        else:
            pass

    return class_list


def get_repertoire_list(repertoire, sort_by=None):
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

        if sort_by == 'title':
            repertoire_list = sorted(
                repertoire_list, 
                key=lambda x: (
                    x[sort_by] is not None, 
                    x[sort_by] or ''
                    )
                )
        elif sort_by is not None:
            repertoire_list = sorted(
                repertoire_list, 
                key=lambda x: (
                    x[sort_by] is not None, # Move None values to the start
                    x[sort_by] or '', # Use empty string as fallback for None values
                    x['title'] or '' # Add a secondary sort key to ensure consistent ordering
                    )
                )
        else:
            pass

    return repertoire_list