# mfo/admin/views.py

import flask
import flask_security
import mfo.admin.forms
from werkzeug.exceptions import Forbidden
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select, desc, asc
from sqlalchemy.sql import exists, func
from sqlalchemy.orm import selectinload
import pandas as pd
import os
import json
import io
from werkzeug.security import check_password_hash

from mfo.database.base import db
import mfo.admin.services.spreadsheet as spreadsheet
import mfo.admin.services.syllabus as syllabus
from mfo.database.models import Entry, Profile, FestivalClass, Repertoire, profiles_roles, entry_repertoire
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

@bp.get ('/dashboard')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def dashboard():
    # need to add some data gathering here
    return flask.render_template('admin/dashboard.html')

@bp.get('/upload_syllabus')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def upload_syllabus_get():
    form = mfo.admin.forms.UploadSyllabusForm()
    return flask.render_template('admin/upload_syllabus.html', form=form)

@bp.post('/upload_syllabus')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def upload_syllabus_post():
    form = mfo.admin.forms.UploadSyllabusForm()
    if form.validate_on_submit():
        file = form.file.data
        if file.filename.endswith('.pdf'):
            syllabus.add_to_db(file)
            # I might make a different template for showing any issues or other ionformation related to a successful upload
            # For now, just redirect back to the Syllabus load page to show flask.flash messages, if they exist
            return flask.redirect(flask.url_for('admin.upload_registrations_get')) 
        else:
            flask.flash(
                f"Uploaded file is not a PDF file." +
                f"Please select the Syllabus PDF file",
                'danger'
                )
            return flask.redirect(flask.url_for('admin.upload_syllabus_get'))

@bp.get('/upload_registrations')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def upload_registrations_get():
    # # clear any flashes that may have been set
    # if '_flashes' in flask.session:
    #     flask.session['_flashes'].clear()
    # check if classes exist in the database
    stmt = select(FestivalClass)
    classes = db.session.execute(stmt).scalars().first()
    if not classes:
        flask.flash("No classes found in the database. Please upload a Syllabus file before uploading registration entries.", 'warning')
        return flask.redirect(flask.url_for('admin.upload_syllabus_get'))
    
    form = mfo.admin.forms.UploadRegistrationsForm()
    return flask.render_template('admin/upload_registrations.html', form=form)


@bp.post('/upload_registrations')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def upload_registrations_post():
    form = mfo.admin.forms.UploadRegistrationsForm()
    if form.validate_on_submit():
        file = form.file.data
        df, succeeded, message = spreadsheet.read_sheet(file)

        if not succeeded:
            flask.flash(message, 'danger')
            return flask.redirect(flask.url_for('admin.upload_registrations_get'))
        
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
            return flask.redirect(flask.url_for('admin.upload_registrations_get'))
        elif form.cancel.data:
            flask.flash("Upload cancelled by user. Database unchanged.", 'warning')
        else:
            flask.flash("Unexpected error! Changes were not committed to the database.", 'danger')
    
    return flask.redirect(flask.url_for('admin.upload_registrations_get'))


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
    form = forms.ClassSortForm()

    sort_by = flask.request.args.getlist('sort_by')
    sort_order = flask.request.args.getlist('sort_order')
    page = int(flask.request.args.get('page', 1))
    per_page = int(flask.request.args.get('per_page', 10))


    # fill in form fields with sort_by and sort_order values
    if sort_by:
        sort_criteria = zip(sort_by, sort_order)
        for i, (sort_field, order_field) in enumerate(sort_criteria, start=1):
            setattr(getattr(form, f'sort{i}'), 'data', sort_field)
            setattr(getattr(form, f'order{i}'), 'data', order_field)
    else:
        form.sort1.data = 'number_suffix'
        form.order1.data = 'asc'

    form.page_rows.data = str(per_page) if per_page else '10'


    class_entries = (
        select(
            Entry.class_id,
            func.count(Entry.id).label('number_of_entries')
        )
        .group_by(Entry.class_id)
    ).subquery()

    stmt = (
        select(
            FestivalClass.id.label('id'),
            func.concat(FestivalClass.number, FestivalClass.suffix).label('number_suffix'),
            FestivalClass.name.label('name'),
            FestivalClass.discipline.label('discipline'),
            FestivalClass.class_type.label('class_type'),
            class_entries.c.number_of_entries,
            (FestivalClass.fee * class_entries.c.number_of_entries).label('total_fees'),
            (func.sum(Repertoire.duration) +
                (FestivalClass.adjudication_time * class_entries.c.number_of_entries) +
                (FestivalClass.move_time * class_entries.c.number_of_entries)
            ).label('total_time')
        )
        .join(FestivalClass.entries)
        .join(Entry.repertoire)
        .join(class_entries, FestivalClass.id == class_entries.c.class_id)
        .group_by(
            FestivalClass.id,
            FestivalClass.number,
            FestivalClass.suffix,
            FestivalClass.name,
            FestivalClass.discipline,
            FestivalClass.class_type,
            FestivalClass.fee,
            FestivalClass.adjudication_time,
            FestivalClass.move_time,
            class_entries.c.number_of_entries,
        )
        .having(func.count(Entry.id) > 0)
    )

    if sort_by and sort_order:
        for column, order in zip(sort_by, sort_order):
            if order == 'asc':
                stmt = stmt.order_by(asc(column))
            elif order == 'desc':
                stmt = stmt.order_by(desc(column))


    stmt = stmt.limit(per_page).offset((page - 1) * per_page)

    _classes = db.session.execute(stmt).all()
    
    total_classes = db.session.execute(
        select(func.count(FestivalClass.id))
        .where(FestivalClass.entries.any())
    ).scalar()

    return flask.render_template(
        'admin/class_report.html', 
        sort_by=sort_by,
        sort_order=sort_order,
        classes=_classes, 
        form=form,
        page=page,
        per_page=per_page,
        total_classes=total_classes,
        )


@bp.post('/report/classes')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def classes_post():
    form = forms.ClassSortForm()
    if form.validate_on_submit():
        if form.reset.data:
            return flask.redirect(flask.url_for('admin.classes_get'))
        else:
            # Get sort_by and sort_order lists from the submitted form
            sort_by = []
            sort_order = []
            for i in range(1, 4):
                sort_field = getattr(form, f'sort{i}').data
                order_field = getattr(form, f'order{i}').data
                if sort_field != 'none': # 'none' is defined in the form's field_choice for no input
                    sort_by.append(sort_field)
                    sort_order.append(order_field)
            per_page = form.page_rows.data
            page = flask.request.args.get('page')
            # Display table with new sort_by and sort_order values
            return flask.redirect(flask.url_for('admin.classes_get', sort_by=sort_by, sort_order=sort_order, page=page, per_page=per_page))
    
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
    if pd.notna(_class.adjudication_time):
        adjudication_mins, adjudication_secs = divmod(_class.adjudication_time, 60)
    else:
        adjudication_mins, adjudication_secs = 0, 0
    form.adjudication_mins.data = adjudication_mins
    form.adjudication_secs.data = adjudication_secs
    if pd.notna(_class.move_time):
        move_mins, move_secs = divmod(_class.move_time, 60)
    else:
        move_mins, move_secs = 0, 0
    form.move_mins.data = move_mins
    form.move_secs.data = move_secs
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

        minutes = int(flask.request.form['adjudication_mins']) # form fields are strings
        seconds = int(flask.request.form['adjudication_secs'])
        total_seconds = minutes * 60 + seconds
        _class.adjudication_time = total_seconds

        minutes = int(flask.request.form['move_mins'])
        seconds = int(flask.request.form['move_secs'])
        total_seconds = minutes * 60 + seconds
        _class.move_time = total_seconds

        # If I want to use form.populate_obj(_class), I need
        # to consistently make sure that the values in empty database 
        # fields are set to whatever the form instance places in an 
        # empty field. The loop, below, enters "None" in empty fields.
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
    stmt = select(Repertoire).options(
        selectinload(Repertoire.festival_classes).load_only(FestivalClass.id),
        selectinload(Repertoire.used_in_entries).load_only(Entry.id)
    )

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

    duration_mins, duration_secs = divmod(repertoire.duration, 60)
    form.duration_mins.data = duration_mins
    form.duration_secs.data = duration_secs

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

        minutes = int(flask.request.form['duration_mins'])
        seconds = int(flask.request.form['duration_secs'])
        total_seconds = minutes * 60 + seconds
        repertoire.duration = total_seconds  # 'duration' matches with database field

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
                with db.session.no_autoflush:     
                    # Get list of users that have a primary profile configured
                    stmt = select(User.primary_profile_id).where(User.primary_profile_id.isnot(None))
                    primary_profile_ids = db.session.execute(stmt).scalars().all()

                    # Find profiles that are not primary profiles
                    stmt = select(Profile).where(Profile.id.notin_(primary_profile_ids))
                    profiles_to_delete = db.session.execute(stmt).scalars().all()

                    # Delete the profiles
                    for profile in profiles_to_delete:
                        db.session.execute(profiles_roles.delete().where(profiles_roles.c.profile_id == profile.id))
                        db.session.delete(profile)                                
               
                    # Clear all remaining data except tables already cleared
                    meta = db.metadata
                    for table in reversed(meta.sorted_tables):
                        if table.name not in ['user', 'role', 'profile', 'roles_users', 'profiles_roles']:
                            db.session.execute(table.delete())
                    
                    db.session.commit()
                    flask.flash('Festival data has been deleted.', 'success')

            except Exception as e:
                db.session.rollback()
                flask.flash(f'An error occurred: {str(e)}', 'danger')
            
            return flask.redirect(flask.url_for('admin.upload_syllabus_get'))
        else:
            flask.flash('Invalid password.', 'danger')

    return flask.render_template('admin/delete_festival_data.html', form=form)