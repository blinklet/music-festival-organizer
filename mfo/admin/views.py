# mfo/admin/views.py

import flask
import flask_security
import mfo.admin.forms
from werkzeug.exceptions import Forbidden
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select, desc
import pandas as pd
import os
import json
import io
from werkzeug.security import check_password_hash

from mfo.database.base import db
import mfo.admin.services.spreadsheet as spreadsheet
from mfo.database.models import Profile, FestivalClass, Repertoire
from mfo.database.users import User, Role
import mfo.admin.services.admin_services as admin_services
import mfo.admin.forms as forms

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
    # # clear any flashes that may have been set
    # if '_flashes' in flask.session:
    #     flask.session['_flashes'].clear()
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
            return flask.redirect(flask.url_for('admin.upload_fail_get'))
        
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
        return flask.render_template('admin/list_issues.html', issues=issues, form=form)
    else:
        flask.flash("No issues found. Click Confirm to add spreadsheet data to MFO", 'success')
        issues = []
        return flask.render_template('admin/list_issues.html', issues=issues, form=form)
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
    file_name = flask.request.form.get('filename', 'issues.txt')

    output = io.BytesIO()
    
    issues_json = flask.session.get('issues', None)
    issues = json.loads(issues_json)

    for issue in issues:
        output.write((issue + "\n").encode('utf-8'))

    output.seek(0)

    return flask.send_file(output, mimetype='text/plain', as_attachment=True, download_name=file_name)


@bp.errorhandler(Forbidden)
def handle_forbidden(e):
    return flask.render_template('forbidden.html', role="Admin")


@bp.get('/report')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def profile_report_get():
    sort_by = flask.request.args.getlist('sort_by')
    sort_order = flask.request.args.getlist('sort_order')

    role = flask.request.args.get('role', None)
    report_name = flask.request.args.get('report_name', None)

    profiles = admin_services.get_profiles(role, sort_by, sort_order)

    return flask.render_template(
        'admin/profile_report.html', 
        report_name=report_name, 
        role=role, 
        profiles=profiles, 
        sort_by=sort_by, 
        sort_order=sort_order,
        )

@bp.get('/report/classes')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def classes_get():
    sort_by = flask.request.args.getlist('sort_by')
    sort_order = flask.request.args.getlist('sort_order')

    stmt = select(FestivalClass)
    _classes = db.session.execute(stmt).scalars().all()
    class_list = admin_services.get_class_list(_classes, sort_by, sort_order)

    return flask.render_template(
        'admin/class_report.html', 
        classes=class_list, 
        sort_by=sort_by, 
        sort_order=sort_order
        )



@bp.get('/info/class')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def class_info_get():
    id = flask.request.args.get('id', None)
    stmt = select(FestivalClass).where(FestivalClass.id == id)
    _class = db.session.execute(stmt).scalar()
    return flask.render_template('admin/class_info.html', _class=_class)

@bp.get('/edit/class_info')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def edit_class_info_get():
    id = flask.request.args.get('id', None)
    stmt = select(FestivalClass).where(FestivalClass.id == id)
    _class = db.session.execute(stmt).scalar()
    form = forms.EditClassBasicInfoForm(obj=_class)
    return flask.render_template('admin/class_edit_info.html', form=form, _class=_class)

@bp.post('/edit/class_info')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def edit_class_info_post():
    id = flask.request.args.get('id', None)
    stmt = select(FestivalClass).where(FestivalClass.id == id)
    _class = db.session.execute(stmt).scalar()
    form = forms.EditClassBasicInfoForm()
    if form.validate_on_submit():
        # if I want to use form.populate_obj(_class), 
        # I need to consistently make sure that the values
        # in empty database fields are set to whatever the form instance
        # places in an empty field. The work below, enters 
        # "None" in empty fields
        for fieldName, field in form._fields.items():
            # Check if the field is blank
            if field.data == '' or field.data is None:
                # Set the corresponding attribute in the database to None
                setattr(_class, fieldName, None)
            else:
                # If the field is not blank, let populate_obj handle it normally
                setattr(_class, fieldName, field.data)

        db.session.commit()

        return flask.redirect(
            flask.url_for('admin.class_info_get', id=id)
            )
    
    return flask.render_template(
        'admin/class_edit_info.html', 
        form=form, 
        _class=_class
        )

@bp.get('/report/repertoire')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def repertoire_get():
    sort_by = flask.request.args.getlist('sort_by')
    sort_order = flask.request.args.getlist('sort_order')
    stmt = select(Repertoire)
    repertoire = db.session.execute(stmt).scalars().all()

    repertoire_list = admin_services.get_repertoire_list(
        repertoire, 
        sort_by,
        sort_order,
        )
    
    return flask.render_template(
        'admin/repertoire_report.html', 
        repertoire=repertoire_list, 
        sort_by=sort_by, 
        sort_order=sort_order
        )

@bp.get('/info/repertoire')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def repertoire_info_get():
    id = flask.request.args.get('id', None)
    stmt = select(Repertoire).where(Repertoire.id == id)
    repertoire = db.session.execute(stmt).scalar()
    return flask.render_template('admin/repertoire_info.html', repertoire=repertoire)

@bp.get('/edit/repertoire')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def repertoire_edit_get():
    id = flask.request.args.get('id', None)
    stmt = select(Repertoire).where(Repertoire.id == id)
    repertoire = db.session.execute(stmt).scalar()
    form = forms.EditRepertoireForm(obj=repertoire)
    return flask.render_template('admin/repertoire_edit.html', form=form, repertoire=repertoire)

@bp.post('/edit/repertoire')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def repertoire_edit_post():
    id = flask.request.args.get('id', None)
    stmt = select(Repertoire).where(Repertoire.id == id)
    repertoire = db.session.execute(stmt).scalar()
    form = forms.EditRepertoireForm()
    if form.validate_on_submit():
        # if I want to use form.populate_obj(_class), 
        # I need to consistently make sure that the values
        # in empty database fields are set to whatever the form instance
        # places in an empty field. The work below, enters 
        # "None" in empty fields
        for fieldName, field in form._fields.items():
            # Check if the field is blank
            if field.data == '' or field.data is None:
                # Set the corresponding attribute in the database to None
                setattr(repertoire, fieldName, None)
            else:
                # If the field is not blank, let populate_obj handle it normally
                setattr(repertoire, fieldName, field.data)
        db.session.commit()
        return flask.redirect(flask.url_for('admin.repertoire_info_get', id=id))
    return flask.render_template('admin/repertoire_edit.html', form=form, repertoire=repertoire)

@bp.get('/delete/festival_data')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def delete_festival_data_get():
    form = forms.ConfirmFestivalDataDelete()
    return flask.render_template('admin/delete_festival_data.html', form=form)

@bp.post('/delete/festival_data')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def delete_festival_data_post():
    form = forms.ConfirmFestivalDataDelete()
    if form.validate_on_submit():
        if flask_security.utils.verify_and_update_password(form.password.data, flask_security.current_user):
            try:          
                # Get list of users
                users = db.session.scalars(select(User)).all()
                roles = db.session.scalars(select(Role)).all()
                
                # Remove profile associations
                for user in users:
                    if hasattr(user, 'profiles'):
                        for profile in user.profiles:
                            db.session.delete(profile)
                            # clear primary_profile foreign key
                            user.primary_profile_id = None

                for role in roles:
                    if hasattr(role, 'profiles'):
                        for profile in role.profiles:
                            db.session.delete(profile)
                
                # Delete profile records
                profile_table = db.metadata.tables.get('profile')
                if profile_table is not None:
                    db.session.execute(profile_table.delete())
                
                # Clear all data except User and Role data
                meta = db.metadata
                for table in reversed(meta.sorted_tables):
                    if table.name not in ['user', 'role', 'profile', 'roles_users']:
                        db.session.execute(table.delete())

                # Add back in a blank primary profile for each user
                for user in users:
                    primary_profile = Profile()
                    primary_profile.email = user.email
                    user, primary_profile = mfo.database.utilities.set_primary_profile(user, primary_profile)
                    for role in user.roles:
                        primary_profile.roles.append(role)
                    primary_profile.users.append(user)
                    db.session.add(primary_profile)
                
                db.session.commit()
                flask.flash('Festival data has been deleted.', 'success')
            except Exception as e:
                db.session.rollback()
                flask.flash(f'An error occurred: {str(e)}', 'danger')
            
            return flask.redirect(flask.url_for('admin.index_get'))
        else:
            flask.flash('Invalid password.', 'danger')
    return flask.render_template('admin/delete_festival_data.html', form=form)