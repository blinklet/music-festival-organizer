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
from mfo.database.models import Profile

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


@bp.get('/teachers')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def teachers_get():
    """
    Get teachers data from database and display it in a bootstrap-styled table
    """
    # Get teachers data from database
    #if "Teacher" in [role.name for role in existing_teacher.roles]:

    # Get all teachers from the database. Select rows where role = teacher
    stmt = select(Profile).where(Profile.roles.any(name='Teacher'))
    result = db.session.execute(stmt)
    teachers = result.scalars().all()

    # Render the teachers template with the teachers data
    return flask.render_template('admin/profile_report.html', report_name='Teachers', profiles=teachers)


@bp.get('/accompanists')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def accompanists_get():
    """
    Get accompanists data from database and display it in a bootstrap-styled table
    """
    stmt = select(Profile).where(Profile.roles.any(name='Accompanist'))
    result = db.session.execute(stmt)
    accompanists = result.scalars().all()

    # Render the teachers template with the teachers data
    return flask.render_template('admin/profile_report.html', report_name='Accompanists', profiles=accompanists)

@bp.get('/participants')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def participants_get():
    stmt = select(Profile).where(Profile.roles.any(name='Participant'))
    result = db.session.execute(stmt)
    participants = result.scalars().all()
    return flask.render_template('admin/profile_report.html', report_name='Participants', profiles=participants)

@bp.get('/groups')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def groups_get():
    stmt = select(Profile).where(Profile.roles.any(name='Group'))
    result = db.session.execute(stmt)
    groups = result.scalars().all()
    return flask.render_template('admin/profile_report.html', report_name='Groups', profiles=groups)