# mfo/template_functions.py

import flask
from markupsafe import Markup
import inspect

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

    # This function is used as a Jinja2 template filter, but it can also be called
    # directly from Python code. When called from Jinja2, the function will return
    # a Markup object that can be safely rendered in an HTML template. When called
    # from Python code, the function will return a string.
    stack = inspect.stack()
    called_from_jinja = any('jinja2' in frame.filename for frame in stack)

    if seconds is None or seconds == 0:
        return ""
    
    if show_seconds:
        minutes, remaining_seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if called_from_jinja:
            display_hours = f"<span class='ms-1 me-1'>{hours:2d}</span>h" if hours else ""
            display_minutes = f"<span class='ms-1 me-1'>{minutes:2d}</span>min" if seconds > 59 else ""
            display_seconds = f"<span class='ms-1 me-1'>{remaining_seconds:2d}</span>s"
        else:
            display_hours = f"{hours:2d} h " if hours else ""
            display_minutes = f"{minutes:2d} min " if seconds > 59 else ""
            display_seconds = f"{remaining_seconds:2d} s"

        if remaining_seconds:
            return Markup(f"{display_hours}{display_minutes}{display_seconds}")
        else:
            return Markup(f"{display_hours}{display_minutes}")
    else:
        rounded_minutes = round(seconds / 60)
        hours, minutes = divmod(rounded_minutes, 60)

        if called_from_jinja:
            display_hours = f"<span class='ms-1 me-1'>{hours:2d}</span>h" if hours else ""
            display_minutes = f"<span class='ms-1 me-1'>{minutes:2d}</span>min"
        else:
            display_hours = f"{hours:2d} h " if hours else ""
            display_minutes = f"{minutes:2d} min"

        return Markup(f"{display_hours}{display_minutes}")
