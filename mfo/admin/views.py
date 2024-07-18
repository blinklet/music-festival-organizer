# mfo/admin/views.py

import flask
import flask_security
import mfo.admin.forms
from werkzeug.exceptions import Forbidden
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select
import pandas as pd
import os
import json
import io

from mfo.database.base import db
import mfo.admin.services.spreadsheet as spreadsheet
from mfo.database.models import Profile, FestivalClass
import mfo.admin.services.admin_services as admin_services

bp = flask.Blueprint(
    'admin',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/admin',
    )


@bp.get('/upload_fail')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def upload_fail_get():
    form = mfo.admin.forms.UploadForm()
    return flask.render_template('admin/index.html', form=form)


@bp.get('/')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def index_get():
    if '_flashes' in flask.session:
        flask.session['_flashes'].clear()
    form = mfo.admin.forms.UploadForm()
    return flask.render_template('admin/index.html', form=form)


@bp.post('/')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def index_post():
    form = mfo.admin.forms.UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        df, succeeded, message = spreadsheet.read_sheet(file)

        if not succeeded:
            flask.flash(message, 'danger')
            # Get out of the innerHTML so that the redirect works
            # https://htmx.org/docs/#redirect
            # (This is different than the confirm_post() function because the form in the 
            # confirm_form.html template is not submitted with htmx; it is a normal POST request)
            response = flask.jsonify("")
            response.headers['HX-Redirect'] = flask.url_for('admin.upload_fail_get')
            return response
        
        flask.flash(message, 'success')

        df = spreadsheet.names_to_df(df)
        issues, info = spreadsheet.gather_issues(df)
        

        if issues:
            flask.session['dataframe'] = df.to_json()
            flask.session['issues'] = json.dumps(issues)
            db.session.rollback()
        
        return flask.redirect(flask.url_for('admin.confirm_get'))

    
@bp.get('/confirm')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def confirm_get():
    form = mfo.admin.forms.ConfirmForm()
    issues_json = flask.session.get('issues', None)
    if issues_json:
        issues = json.loads(issues_json)
        flask.flash("Issues found. Review issues", 'warning')
        return flask.render_template('admin/partials/list_issues.html', issues=issues, form=form)
    else:
        flask.flash("No issues found. Click Confirm to add spreadsheet data to MFO", 'success')
        issues = []
        return flask.render_template('admin/partials/list_issues.html', issues=issues, form=form)
    # Note that the form in the confirm_form.html template included in the 
    # partials/list_issues.html template is not submitted with htmx; it is a normal POST request
    # so when the form is submitted, the confirm_post() function is called with a normal POST request
    # so the redirect reloads the entire page.


@bp.post('/confirm')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def confirm_post():
    form = mfo.admin.forms.ConfirmForm()
    if form.validate_on_submit():
        flask.session.pop('issues', None)
        if form.confirm.data:
            df = pd.read_json(flask.session.get('dataframe'))
            flask.session.pop('dataframe', None)
            issues, info = spreadsheet.gather_issues(df)
            spreadsheet.commit_to_db()
            flask.flash("Changes were committed to the database.", 'success')
            return flask.redirect(flask.url_for('admin.index_get'))
        elif form.cancel.data:
            flask.flash("Upload cancelled by user. Database unchanged.", 'warning')
        else:
            flask.flash("Unexpected error! Changes were not committed to the database.", 'danger')
    
    return flask.redirect(flask.url_for('admin.upload_fail_get'))


@bp.post('/generate_text_file')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def generate_text_file():
    # Get the file name from the form data
    file_name = flask.request.form.get('filename', 'issues.txt')  # Default to 'issues.txt' if not provided

    # Create an in-memory binary file
    output = io.BytesIO()
    
    # Example issues list, typically this would be dynamic
    issues_json = flask.session.get('issues', None)
    issues = json.loads(issues_json)

    # Write each issue to the output, appending a newline to each one
    for issue in issues:
        output.write((issue + "\n").encode('utf-8'))
    
    # Set the cursor to the beginning of the file
    output.seek(0)
    
    # Save the file content and file name in the session
    flask.session['file_content'] = output.getvalue()
    flask.session['file_name'] = file_name

    # Return a JSON response with the download URL
    return flask.jsonify({'redirect': flask.url_for('admin.download_file')})

@bp.route('/download_file')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def download_file():
    # Retrieve file content and file name from session
    file_content = flask.session.get('file_content', None)
    file_name = flask.session.get('file_name', 'issues.txt')

    if not file_content:
        return '<p class="error">No file to download</p>'

    output = io.BytesIO(file_content)
    output.seek(0)
    return flask.send_file(output, mimetype='text/plain', as_attachment=True, download_name=file_name)


@bp.errorhandler(Forbidden)
def handle_forbidden(e):
    return flask.render_template('forbidden.html', role="Admin")


@bp.get('/report')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def profile_report_get():
    sort_by = flask.request.args.get('sort_by', None)
    role = flask.request.args.get('role', None)
    report_name = flask.request.args.get('report_name', None)

    profiles = admin_services.get_profiles(role, sort_by)

    print(f'#### {report_name} ####')
    print(f'#### {role} ####')

    return flask.render_template(
        'admin/profile_report.html', 
        report_name=report_name, 
        role=role, 
        profiles=profiles, 
        sort_by=sort_by
        )

@bp.get('/report/classes')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def classes_get():
    class_list = list()
    stmt = select(FestivalClass)
    _classes = db.session.execute(stmt).scalars().all()
    for _class in _classes:

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
        
        description = _class.description
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
            "number_suffix": number_suffix,
            "number": number,
            "suffix": suffix,
            "description": description,
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

    return flask.render_template('admin/class_report.html', report_name='Classes', classes=class_list)

