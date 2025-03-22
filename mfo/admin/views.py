# mfo/admin/views.py

import flask
import flask_security
import mfo.admin.forms
from werkzeug.exceptions import Forbidden
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select, desc, asc
from sqlalchemy.sql import exists, func, text
from sqlalchemy.orm import selectinload, joinedload, aliased
from datetime import datetime
import pandas as pd
import os
import json
import io
from werkzeug.security import check_password_hash

from mfo.database.base import db
import mfo.admin.services.spreadsheet as spreadsheet
import mfo.admin.services.syllabus as syllabus
from mfo.database.models import School, Entry, Profile, FestivalClass, Repertoire, profiles_roles, entry_repertoire, participants_entries
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

    role = flask.request.args.get('role', None)
    report_name = flask.request.args.get('report_name', None)
    form = forms.ParticipantSortForm(role)

    sort_by = flask.request.args.getlist('sort_by')
    sort_order = flask.request.args.getlist('sort_order')
    page = int(flask.request.args.get('page', 1))
    per_page = int(flask.request.args.get('per_page', 10))
    hide_zero_entries = flask.request.args.get(
        'hide_zero_entries', 
        'false'
    ).lower() == 'true'

    if sort_by:
        sort_criteria = zip(sort_by, sort_order)
        for i, (sort_field, order_field) in enumerate(sort_criteria, start=1):
            setattr(getattr(form, f'sort{i}'), 'data', sort_field)
            setattr(getattr(form, f'order{i}'), 'data', order_field)
    else:
        if role == 'Group':
            form.sort1.data = 'group_name'
            sort_by = ['group_name']
        else:
            form.sort1.data = 'name'
            sort_by = ['name']

        form.order1.data = 'asc'
        sort_order = ['asc']

    form.page_rows.data = str(per_page) if per_page else '10'
    form.hide_zero_entries.data = hide_zero_entries
    # I don't do anything with hide_zero_entries yet, but I might in the future

    
    # Define aliases for Profile
    student_profile = aliased(Profile)
    teacher_profile = aliased(Profile)

    # Define subqueries for num_entries
    if role == 'Teacher':
        students_subquery = (
            select(
                teacher_profile.id.label("teacher_id"), 
                student_profile.id.label("student_id")
            ).outerjoin(
                student_profile, 
                teacher_profile.students
            ).group_by(
                teacher_profile.id, 
                student_profile.id
            )
        ).subquery()

        entries_subquery = (
            select(
                students_subquery.c.teacher_id.label("profile_id"),
                func.count(Entry.id).label('number_of_entries')
            ).outerjoin(
                student_profile, 
                student_profile.id == students_subquery.c.student_id
            ).outerjoin(
                Entry, 
                student_profile.participates_in_entries
            ).group_by(
                students_subquery.c.teacher_id
            )
        ).subquery()
        
    elif role == 'Accompanist':
        entries_subquery = (
            select(
                Profile.id.label("profile_id"), 
                func.count(Entry.id).label('number_of_entries')
            ).outerjoin(
                Entry, 
                Profile.accompanies_entries
            ).group_by(
                Profile.id
            )
        ).subquery()

    elif role == 'Participant' or role == 'Group':
        entries_subquery = (
            select(
                Profile.id.label("profile_id"),
                func.count(Entry.id).label("number_of_entries")
            ).outerjoin(
                Entry, 
                Profile.participates_in_entries
            ).group_by(
                Profile.id
            )
        ).subquery()

    else:
        raise ValueError(f"Invalid role found in profile_report_get() function: {role}")

    stmt = (
        select(
            Profile.id.label("id"),
            Profile.name.label("name"),
            Profile.group_name,
            Profile.email,
            Profile.phone,
            Profile.address,
            Profile.city,
            Profile.province,
            Profile.postal_code,
            School.name.label("attends_school"),
            entries_subquery.c.number_of_entries
        ).outerjoin(
            entries_subquery,
            Profile.id == entries_subquery.c.profile_id
        ).outerjoin(School, Profile.attends_school
        ).filter(Profile.roles.any(name=role))
    )

    if hide_zero_entries:
        stmt = stmt.filter(func.coalesce(entries_subquery.c.number_of_entries, 0) > 0)

    if sort_by and sort_order:
        for column, order in zip(sort_by, sort_order):
            if column == 'school':
                if order == 'asc':
                    stmt = stmt.order_by(asc(text('schools.name')))
                elif order == 'desc':
                    stmt = stmt.order_by(desc(text('schools.name')))
            else:
                if order == 'asc':
                    stmt = stmt.order_by(asc(column))
                elif order == 'desc':
                    stmt = stmt.order_by(desc(column))

    stmt = stmt.limit(per_page).offset((page - 1) * per_page)

    profiles = db.session.execute(stmt).all()

    stmt2 = select(
        func.count(Profile.id)
    ).filter(Profile.roles.any(name=role))

    if hide_zero_entries:
        if role == 'Teacher':
            stmt2 = stmt2.filter(
                teacher_profile.students.any(
                    student_profile.participates_in_entries.any()
                )
            )   
        elif role == 'Accompanist':
            stmt2 = stmt2.filter(Profile.accompanies_entries.any())
        elif role == 'Participant' or role == 'Group':
            stmt2 = stmt2.filter(Profile.participates_in_entries.any())

    total_profiles = db.session.execute(stmt2).scalar()

    return flask.render_template(
        'admin/profile_report.html', 
        form=form,
        report_name=report_name, 
        role=role, 
        profiles=profiles, 
        sort_by=sort_by, 
        sort_order=sort_order,
        page=page,
        per_page=per_page,
        total_profiles=total_profiles,
        )


@bp.post('/report')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def profile_report_post():
    role = flask.request.args.get('role', None)
    report_name = flask.request.args.get('report_name', None)
    form = forms.ParticipantSortForm(role)

    if form.validate_on_submit():
        if form.reset.data:
            return flask.redirect(flask.url_for('admin.profile_report_get', report_name=report_name, role=role))
        else:
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
            hide_zero_entries = form.hide_zero_entries.data

            return flask.redirect(
                flask.url_for(
                    'admin.profile_report_get', 
                    report_name=report_name,
                    role=role,
                    sort_by=sort_by, 
                    sort_order=sort_order, 
                    page=page, 
                    per_page=per_page,
                    hide_zero_entries=hide_zero_entries
                )
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
    hide_zero_entries = flask.request.args.get(
        'hide_zero_entries', 
        'false'
    ).lower() == 'true'

    # fill in form fields with sort_by and sort_order values
    if sort_by:
        sort_criteria = zip(sort_by, sort_order)
        for i, (sort_field, order_field) in enumerate(sort_criteria, start=1):
            setattr(getattr(form, f'sort{i}'), 'data', sort_field)
            setattr(getattr(form, f'order{i}'), 'data', order_field)
    else:
        form.sort1.data = 'number_suffix'
        form.order1.data = 'asc'
        sort_by = ['number_suffix']
        sort_order = ['asc']

    form.page_rows.data = str(per_page) if per_page else '10'
    form.hide_zero_entries.data = hide_zero_entries

    class_entries = (
        select(
            Entry.class_id,
            func.count(Entry.id).label('number_of_entries')
        )
        .group_by(Entry.class_id)
    ).subquery()

    class_repertoire = (
        select(
            FestivalClass.id,
            func.sum(Repertoire.duration).label('total_duration')
        )
        .join(FestivalClass.entries)
        .join(Entry.repertoire)
        .group_by(FestivalClass.id)
    ).subquery()

    class_numbers = (
        select(
            FestivalClass.id,
            func.concat(FestivalClass.number, FestivalClass.suffix).label('number_suffix')
        )
        .group_by(FestivalClass.id)
    ).subquery()

    stmt = (
        select(
            FestivalClass.id.label('id'),
            class_numbers.c.number_suffix,
            FestivalClass.name.label('name'),
            FestivalClass.discipline.label('discipline'),
            FestivalClass.class_type.label('class_type'),
            FestivalClass.level.label('level'),
            func.coalesce(class_entries.c.number_of_entries, 0).label('number_of_entries'),
            (FestivalClass.fee * func.coalesce(class_entries.c.number_of_entries, 0)).label('total_fees'),
            (func.coalesce(class_repertoire.c.total_duration, 0) +
                (FestivalClass.adjudication_time * func.coalesce(class_entries.c.number_of_entries, 0)) +
                (FestivalClass.move_time * func.coalesce(class_entries.c.number_of_entries, 0))
            ).label('total_time')
        )
        .outerjoin(class_entries, FestivalClass.id == class_entries.c.class_id)
        .outerjoin(class_repertoire, FestivalClass.id == class_repertoire.c.id)
        .outerjoin(class_numbers, FestivalClass.id == class_numbers.c.id)
    )

    if hide_zero_entries:
        stmt = stmt.filter(func.coalesce(class_entries.c.number_of_entries, 0) > 0)

    if sort_by and sort_order:
        for column, order in zip(sort_by, sort_order):
            if order == 'asc':
                stmt = stmt.order_by(asc(column))
            elif order == 'desc':
                stmt = stmt.order_by(desc(column))

    stmt = stmt.limit(per_page).offset((page - 1) * per_page)

    _classes = db.session.execute(stmt).all()
    
    stmt2 = select(func.count(FestivalClass.id))
    if hide_zero_entries:
        stmt2 = stmt2.filter(FestivalClass.entries.any())
    total_classes = db.session.execute(stmt2).scalar()
    
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
            hide_zero_entries = form.hide_zero_entries.data
            # Display table with new sort_by and sort_order values
            return flask.redirect(
                flask.url_for(
                    'admin.classes_get', 
                    sort_by=sort_by, 
                    sort_order=sort_order, 
                    page=page, 
                    per_page=per_page,
                    hide_zero_entries=hide_zero_entries
                )
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

        # if I want to use form.populate_obj(_class), 
        # I need to consistently make sure that the values
        # in empty database fields are set to whatever the form instance
        # places in an empty field. So, instead of using the form.populate_obj()
        # method, I will manually set the values of the database fields
        # in the for loop below, which enters "None" in empty fields
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
    form = forms.RepertoireSortForm()

    page = int(flask.request.args.get('page', 1))
    per_page = int(flask.request.args.get('per_page', 10))
    sort_by = flask.request.args.getlist('sort_by')
    sort_order = flask.request.args.getlist('sort_order')
    hide_zero_entries = flask.request.args.get(
        'hide_zero_entries', 
        'false'
    ).lower() == 'true'

    if sort_by:
        sort_criteria = zip(sort_by, sort_order)
        for i, (sort_field, order_field) in enumerate(sort_criteria, start=1):
            setattr(getattr(form, f'sort{i}'), 'data', sort_field)
            setattr(getattr(form, f'order{i}'), 'data', order_field)
    else:
        form.sort1.data = 'title'
        form.order1.data = 'asc'
        sort_by = ['title']
        sort_order = ['asc']

    form.page_rows.data = str(per_page) if per_page else '10'
    form.hide_zero_entries.data = hide_zero_entries

    entries_count = (
        select(
            Repertoire.id,
            func.count(Entry.id).label('number_of_entries')
        )
        .join(Repertoire.used_in_entries)
        .group_by(Repertoire.id)
    ).subquery()

    classes_count = (
        select(
            Repertoire.id,
            func.count(FestivalClass.id).label('number_of_classes')
        )
        .join(Repertoire.festival_classes)
        .group_by(Repertoire.id)
    ).subquery()

    stmt = (
        select(
            Repertoire.id.label('id'),
            Repertoire.title.label('title'),
            Repertoire.composer.label('composer'),
            Repertoire.level.label('level'),
            Repertoire.type.label('type'),
            Repertoire.discipline.label('discipline'),
            Repertoire.duration.label('duration'),
            entries_count.c.number_of_entries,
            classes_count.c.number_of_classes
        )
        .join(entries_count, Repertoire.id == entries_count.c.id)
        .join(classes_count, Repertoire.id == classes_count.c.id)
    )

    if hide_zero_entries:
        stmt = stmt.where(func.coalesce(entries_count.c.number_of_entries, 0) > 0)

    if sort_by and sort_order:
        for column, order in zip(sort_by, sort_order):
            if order == 'asc':
                stmt = stmt.order_by(asc(column))
            elif order == 'desc':
                stmt = stmt.order_by(desc(column))

    stmt = stmt.limit(per_page).offset((page - 1) * per_page)

    repertoire = db.session.execute(stmt).all()
    
    stmt2 = select(func.count(Repertoire.id))
    if hide_zero_entries:
        stmt2 = stmt2.where(Repertoire.used_in_entries.any())
    total_repertoire = db.session.execute(stmt2).scalar()
          
    return flask.render_template(
        'admin/repertoire_report.html', 
        form=form,
        repertoire=repertoire,
        total_repertoire=total_repertoire, 
        sort_by=sort_by, 
        sort_order=sort_order,
        page=page,
        per_page=per_page,
        )


@bp.post('/report/repertoire')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def repertoire_post():
    form = forms.RepertoireSortForm()
    if form.validate_on_submit():
        if form.reset.data:
            return flask.redirect(flask.url_for('admin.repertoire_get'))
        else:
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
            hide_zero_entries = form.hide_zero_entries.data
            return flask.redirect(
                flask.url_for('admin.repertoire_get', 
                    sort_by=sort_by, 
                    sort_order=sort_order, 
                    page=page, 
                    per_page=per_page,
                    hide_zero_entries=hide_zero_entries
                )
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
        # places in an empty field. So, instead of using the form.populate_obj()
        # method, I will manually set the values of the database fields
        # in the for loop below, which enters "None" in empty fields
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
                        do_not_delete = [
                            'user', 
                            'role', 
                            'profile', 
                            'roles_users', 
                            'profiles_roles',
                            'disciplines',
                            'performance_types',
                            'levels',
                            'default_times',
                            'default_fees',
                            ]
                        
                        if table.name not in do_not_delete:
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


@bp.get('/profile_info')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def profile_info_get():
    profile_id = flask.request.args.get('id', None)

    profile_alias = aliased(Profile)
    teacher_alias = aliased(Profile)

    role_names = (
        select(
            Profile.id,
            func.string_agg(Role.name.label('role_name'), ', ').label('roles')
        ).join(Profile.roles
        ).group_by(Profile.id)
    ).subquery()

    teacher_names = (
        select(
            profile_alias.id,
            func.string_agg(teacher_alias.name.label('teacher_name'), '; ').label('teacher')
        ).outerjoin(teacher_alias, profile_alias.teachers
        ).group_by(profile_alias.id)
    ).subquery()

    stmt = (
        select(
            Profile.id,
            Profile.name.label("name"),
            Profile.group_name,
            Profile.email,
            Profile.phone,
            Profile.address,
            Profile.city,
            Profile.province,
            Profile.postal_code,
            Profile.birthdate,
            Profile.comments,
            Profile.national_festival,
            School.name.label("attends_school"),
            teacher_names.c.teacher,
            role_names.c.roles
        ).outerjoin(Profile.attends_school
        ).outerjoin(teacher_names, Profile.id == teacher_names.c.id
        ).outerjoin(role_names, Profile.id == role_names.c.id
        ).filter(Profile.id == profile_id)
    )

    profile = db.session.execute(stmt).first()

    return flask.render_template('/admin/profile_info.html', profile=profile)


@bp.get('/edit_profile_info')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def edit_profile_info_get():
    profile_id = int(flask.request.args.get('id', None))
    
    stmt = select(Profile).options(
        selectinload(Profile.roles),
        selectinload(Profile.teachers),
        joinedload(Profile.attends_school)
    ).filter_by(id=profile_id)

    profile = db.session.execute(stmt).scalar_one_or_none()

    profile.rolenames = [role.name for role in profile.roles]

    print(profile.rolenames)

    if "Group" not in profile.rolenames:
        form = forms.ProfileIndivualEditForm(obj=profile)
        if profile.birthdate:
            print()
            print(type(profile.birthdate))
            print(profile.birthdate)
            print(profile.birthdate.strftime('%m/%d/%Y'))
            print()
            form.birthdate.data = profile.birthdate
    else:
        form = forms.ProfileGroupEditForm(obj=profile)

    form.attends_school.data = (
        profile.attends_school.name 
        if profile.attends_school 
        else None
    )
    form.teacher.data = '; '.join(
        [teacher.name for teacher in profile.teachers]
    )

    return flask.render_template('/admin/profile_info_edit.html', form=form, profile=profile)


@bp.post('/edit_profile_info')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def edit_profile_info_post():
    profile_id = int(flask.request.args.get('id', None))
    stmt = select(Profile).options(
        selectinload(Profile.roles),
        selectinload(Profile.teachers),
        joinedload(Profile.attends_school)
    ).filter_by(id=profile_id)

    profile = db.session.execute(stmt).scalar_one_or_none()
    
    if not profile:
        flask.flash("Profile not found.", 'danger')
        return flask.redirect(flask.url_for('admin.profile_info_get', id=profile_id))
    
    profile.rolenames = [role.name for role in profile.roles]

    if "Group" in profile.rolenames:
        form = forms.ProfileGroupEditForm()
    else:
        form = forms.ProfileIndivualEditForm()

    if form.cancel.data:
        return flask.redirect(flask.url_for('admin.profile_info_get', id=profile_id))
    
    if form.validate_on_submit():
        # I can't just use form.populate_obj(profile) because the form has fields that are not in the database
        # I need to manually set the values of the database fields
        if "Group" in profile.rolenames:
            profile.group_name = form.group_name.data
        else:
            profile.name = form.name.data
            profile.birthdate = form.birthdate.data if form.birthdate.data else None
        profile.address = form.address.data if form.address.data else None
        profile.city = form.city.data if form.city.data else None
        profile.province = form.province.data if form.province.data else None
        profile.postal_code = form.postal_code.data if form.postal_code.data else None
        profile.phone = form.phone.data if form.phone.data else None
        profile.email = form.email.data if form.email.data else None
        profile.comments = form.comments.data if form.comments.data else None
        profile.national_festival = form.national_festival.data if form.national_festival.data else None

        # Update the school
        school_name = form.attends_school.data
        if school_name:
            stmt = select(School).filter_by(name=school_name)
            school = db.session.execute(stmt).scalar_one_or_none()
            if school:
                profile.attends_school = school
            else:
                flask.flash(f"School {school_name} not found in the database.")  
        else:
            profile.attends_school = None

        # Update the teachers
        teacher_names = form.teacher.data.split(';')
        teachers = []
        for teacher_name in teacher_names:
            teacher = Profile.query.filter_by(name=teacher_name).one_or_none()
            if teacher:
                teachers.append(teacher)
        profile.teachers = teachers

        # Update the roles for individuals
        if "Group" not in profile.rolenames:
            roles = []
            for role_name in form.rolenames.data:
                role = db.session.execute(
                    select(Role).filter_by(name=role_name)
                ).scalar_one_or_none()
                if role:
                    roles.append(role)
            profile.roles = roles

        db.session.commit()
        return flask.redirect(flask.url_for('admin.profile_info_get', id=profile_id))
    
    print(form.errors)
    return flask.render_template('/admin/profile_info_edit.html', form=form, profile=profile)


@bp.post('/edit_group_info')
@flask_security.auth_required()
@flask_security.roles_required('Admin')
def edit_group_info_post():
    profile_id = int(flask.request.args.get('id', None))
    stmt = select(Profile).filter_by(id=profile_id)
    profile = db.session.execute(stmt).scalar_one_or_none()
    form = forms.ProfileGroupEditForm()

    return("group post")