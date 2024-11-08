# mfo/admin/forms.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import ValidationError, StringField, SubmitField, HiddenField, IntegerField, DecimalField, SelectField, TextAreaField, PasswordField
from wtforms.validators import StopValidation, InputRequired, Length, Optional, NumberRange


class_types = [
        ('', 'None'),
        ('Solo', 'Solo'),
        ('Duet', 'Duet'),
        ('Trio', 'Trio'),
        ('Quartet', 'Quartet'),
        ('Quintet', 'Quintet'),
        ('Recital', 'Recital'),
        ('Ensemble', 'Ensemble'),
    ]

disciplines = [
        ('', 'None'),
        ('Vocal', 'Vocal'),
        ('Piano', 'Piano'),
        ('Organ', 'Organ'),
        ('Strings', 'Strings'),
        ('Recorder', 'Recorder'),
        ('Woodwinds', 'Woodwinds'),
        ('Brass', 'Brass'),
        ('Percussion', 'Percussion'),
        ('Instrumental', 'Instrumental'),
        ('Musical Theatre', 'Musical Theatre'),
    ]
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
    number = StringField('Number', validators=[InputRequired(), Length(max=10)])
    suffix = StringField('Suffix', validators=[Optional(), Length(max=5)])
    class_type_choices = class_types
    class_type = SelectField('Class Type', choices=class_type_choices, validators=[Optional()])
    name = StringField('Name', validators=[Optional(), Length(max=60)])
    discipline_choices = disciplines
    discipline = SelectField('Discipline', choices=discipline_choices, validators=[Optional()])
    
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
    id = HiddenField('ID')
    title = StringField('Title', validators=[InputRequired(), Length(max=60)])
    composer = StringField('Composer', validators=[InputRequired(), Length(max=60)])
    discipline_choices = disciplines
    discipline = SelectField('Discipline', choices=discipline_choices, validators=[Optional()])
    type_choices = class_types
    type = SelectField('Type', choices=type_choices, validators=[Optional()])
    level = StringField('Level', validators=[Optional(), Length(max=60)])
    duration_mins = IntegerField('Minutes', validators=[InputRequired()])
    duration_secs = IntegerField('Seconds', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[Optional()], render_kw={"rows": 5, "placeholder": "Enter description here..."})
    submit = SubmitField('Update')


class ConfirmFestivalDataDelete(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired()], render_kw={"placeholder": "Enter password..."})
    submit = SubmitField('Delete Data')


class ClassSortForm(FlaskForm):
    # these name of each label must match the key in the _classes dictionary
    field_choices = [
        ("none", ""),
        ("number_suffix", "Class Number"),
        ("name", "Name"),
        ("discipline", "Discipline"),
        ("class_type", "Type"),
        ("number_of_entries", "Entries"),
        ("total_fees", "Total fees"),
        ("total_time", "Total time"),
    ]

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

    reset = SubmitField('Reset')
    submit = SubmitField('Sort')
    page_rows = SelectField('Displayed rows:', choices=page_choices, validators=[InputRequired()])

    sort1 = SelectField('Sort by:', choices=field_choices, validators=[Optional()])
    order1 = SelectField('Order:', choices=order_choices, validators=[Optional()])
    sort2 = SelectField('Sort by:', choices=field_choices, validators=[Optional()])
    order2 = SelectField('Order:', choices=order_choices, validators=[Optional()])
    sort3 = SelectField('Sort by:', choices=field_choices, validators=[Optional()])
    order3 = SelectField('Order:', choices=order_choices, validators=[Optional()])
