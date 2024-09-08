# mfo/template_functions.py

import flask
from markupsafe import Markup

bp = flask.Blueprint(
    'jinja_functions',
    __name__,
    )

@bp.app_template_global()
def update_sort(column, sort_by, sort_order):
    if column in sort_by:
        # Move the existing column to the end of the list
        sort_by.remove(column)
        sort_by.append(column)
    else:
        # Or, add the new column to the end of the list
        sort_by.append(column)
    return sort_by

@bp.app_template_global()
def update_order(column, sort_by, sort_order):
    if column in sort_by:
        # If column altready exists in sort_by list,
        # find its corresponding sort_order value,
        # reverse it, and move it to the end of the list
        index = sort_by.index(column)
        order = sort_order.pop(index)
        if order == 'asc':
            sort_order.append('desc')
        else:
            sort_order.append('asc')
    else:
        # Or, add the sort_order value for the new column 
        # to the end of the list
        sort_order.append('asc')
    return sort_order

# Add helper functions to Jinja2 environment
# app.jinja_env.globals.update(update_sort=update_sort)
# app.jinja_env.globals.update(update_order=update_order)

@bp.app_template_global()
def format_time(seconds, show_seconds=True):
    if seconds is None or seconds == 0:
        return ""
    
    if show_seconds:
        minutes, remaining_seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        display_hours = f"<span class='ms-1 me-1'>{hours:2d}</span>h" if hours else ""
        display_minutes = f"<span class='ms-1 me-1'>{minutes:2d}</span>min" if seconds > 59 else ""
        display_seconds = f"<span class='ms-1 me-1'>{remaining_seconds:2d}</span>s"

        if remaining_seconds:
            return Markup(f"{display_hours}{display_minutes}{display_seconds}")
        else:
            return Markup(f"{display_hours}{display_minutes}")
    else:
        rounded_minutes = round(seconds / 60)
        hours, minutes = divmod(rounded_minutes, 60)

        display_hours = f"<span class='ms-1 me-1'>{hours:2d}</span>h" if hours else ""
        display_minutes = f"<span class='ms-1 me-1'>{minutes:2d}</span>min"

        return Markup(f"{display_hours}{display_minutes}")
