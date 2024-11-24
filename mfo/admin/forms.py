# mfo/admin/forms.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from flask import current_app
from wtforms import ValidationError, StringField, SubmitField, BooleanField, HiddenField, IntegerField, DecimalField, SelectField, TextAreaField, PasswordField
from wtforms.validators import StopValidation, InputRequired, Length, Optional, NumberRange

from mfo.database.models import Discipline, PerformanceType, Level
from mfo.database.base import db
from sqlalchemy import select

def get_choices(table_class, column_name, none_option=False):
    """
    Get a list of choices for a select field from a database table column.
    :param table_class: SQLAlchemy table class
    :param column_name: Name of the column to get choices from
    :param none_option: Include a None option at the beginning of the list
    :return: List of choices
    """
    with current_app.app_context():
        column = getattr(table_class, column_name)
        results = db.session.execute(select(column)).scalars().all()
        choices_list = [(result, result) for result in results]
        if none_option:
            choices_list.insert(0, ('', 'None'))
        return choices_list

def validate_decimal_places(form, field):
    if field.data is not None:
        str_value = str(field.data)
        if '.' in str_value:
            decimal_places = str_value.split('.')[1]
            if len(decimal_places) > 2:
                message = 'Please enter a valid amount'
                raise ValidationError(message)


class UploadSyllabusForm(FlaskForm):
    file = FileField('Upload Syllabus File', [FileRequired()])
    submit = SubmitField('Upload')

class UploadRegistrationsForm(FlaskForm):
    file = FileField('Upload Entries File', [FileRequired()])
    submit = SubmitField('Upload')

class ConfirmForm(FlaskForm):
    confirm = SubmitField('Confirm')
    cancel = SubmitField('Cancel')
    
class EditClassBasicInfoForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(EditClassBasicInfoForm, self).__init__(*args, **kwargs)
        self.discipline.choices = get_choices(Discipline, 'name', none_option=True)
        self.class_type.choices = get_choices(PerformanceType, 'name')
        self.level.choices = get_choices(Level, 'name', none_option=True)

    number = StringField('Number', validators=[InputRequired(), Length(max=10)])
    suffix = StringField('Suffix', validators=[Optional(), Length(max=5)])
    class_type = SelectField('Class Type', validators=[Optional()])
    name = StringField('Name', validators=[Optional(), Length(max=60)])
    discipline = SelectField('Discipline', validators=[Optional()])
    level = SelectField('Level', validators=[Optional()])
    fee = DecimalField(
        'Fee', 
        validators=[
            InputRequired(), 
            NumberRange(min=0, message='Fee must be a positive amount'),
            validate_decimal_places
        ]
    )
    adjudication_mins = IntegerField('Adjudication Minutes', validators=[InputRequired()])
    adjudication_secs = IntegerField('Adjudication Seconds', validators=[InputRequired()])
    move_mins = IntegerField('Move Minutes', validators=[InputRequired()])
    move_secs = IntegerField('Move Seconds', validators=[InputRequired()])
    submit = SubmitField('Update')


class EditRepertoireForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super(EditRepertoireForm, self).__init__(*args, **kwargs)
        self.discipline.choices = get_choices(Discipline, 'name', none_option=True)
        self.type.choices = get_choices(PerformanceType, 'name', none_option=True)
        self.level.choices = get_choices(Level, 'name', none_option=True)

    id = HiddenField('ID')
    title = StringField('Title', validators=[InputRequired(), Length(max=60)])
    composer = StringField('Composer', validators=[InputRequired(), Length(max=60)])
    discipline = SelectField('Discipline', validators=[Optional()])
    type = SelectField('Type', validators=[Optional()])
    level = SelectField('Level', validators=[Optional()])
    duration_mins = IntegerField('Minutes', validators=[InputRequired()])
    duration_secs = IntegerField('Seconds', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[Optional()], render_kw={"rows": 5, "placeholder": "Enter description here..."})
    submit = SubmitField('Update')


class ConfirmFestivalDataDelete(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired()], render_kw={"placeholder": "Enter password..."})
    submit = SubmitField('Delete Data')


# these name of each label must the strings in the admin_services.sort_list() function
order_choices = [
    ("asc", "Ascending"),
    ("desc", "Descending"),
]

page_choices = [
    ("10", "10"),
    ("20", "20"),
    ("50", "50"),
    ("100000", "All"),
]

class ReportSortForm(FlaskForm):
    field_choices = []

    reset = SubmitField('Reset')
    submit = SubmitField('Sort')
    page_rows = SelectField('Displayed rows:', choices=page_choices, validators=[InputRequired()])

    sort1 = SelectField('Sort by:', choices=field_choices, validators=[Optional()])
    order1 = SelectField('Order:', choices=order_choices, validators=[Optional()])
    sort2 = SelectField('Sort by:', choices=field_choices, validators=[Optional()])
    order2 = SelectField('Order:', choices=order_choices, validators=[Optional()])
    sort3 = SelectField('Sort by:', choices=field_choices, validators=[Optional()])
    order3 = SelectField('Order:', choices=order_choices, validators=[Optional()])
    hide_zero_entries = BooleanField('Hide rows with zero entries', validators=[Optional()])


class ClassSortForm(ReportSortForm):
    def __init__(self):
        super(ClassSortForm, self).__init__()

        field_choices = [
            ("none", ""),
            ("number_suffix", "Class Number"),
            ("name", "Name"),
            ("discipline", "Discipline"),
            ("class_type", "Type"),
            ("level", "Level"),
            ("number_of_entries", "Entries"),
            ("total_fees", "Total fees"),
            ("total_time", "Total time"),
        ]

        self.sort1.choices = field_choices
        self.sort2.choices = field_choices
        self.sort3.choices = field_choices


class RepertoireSortForm(ReportSortForm):
    def __init__(self):
        super(RepertoireSortForm, self).__init__()

        field_choices = [
            ("none", ""),
            ("title", "Title"),
            ("composer", "Composer"),
            ("level", "Level"),
            ("type", "Type"),
            ("discipline", "Discipline"),
            ("duration", "Duration"),
            ("number_of_entries", "Entries"),
        ]

        self.sort1.choices = field_choices
        self.sort2.choices = field_choices
        self.sort3.choices = field_choices


class ParticipantSortForm(ReportSortForm):
    def __init__(self, role):
        super(ParticipantSortForm, self).__init__()

        field_choices = [
            ("none", ""),
            ("name", "Name"),
            ("email", "E-mail"),
            ("phone", "Phone"),
            ("address", "Address"),
            ("city", "City"),
            ("school", "School"),
        ]
        
        if role == "Group":
            field_choices[1] = ("group_name", "Group")
        elif role == "Participant":
            pass
        elif role == "Teacher" or role == "Accompanist":
            field_choices[6] = ("postal_code", "Postal Code")
        else:
            raise ValueError("Invalid participant type in ParticipantSortForm")

        self.sort1.choices = field_choices
        self.sort2.choices = field_choices
        self.sort3.choices = field_choices


