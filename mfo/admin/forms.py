from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, HiddenField, IntegerField, SelectField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, InputRequired, Length, Optional

class UploadForm(FlaskForm):
    file = FileField('Spreadsheet File', [FileRequired()])
    submit = SubmitField('Upload')

class ConfirmForm(FlaskForm):
    confirm = SubmitField('Confirm')
    cancel = SubmitField('Cancel')
    
class EditClassBasicInfoForm(FlaskForm):
    number = StringField('Number', validators=[DataRequired(), Length(max=10)])
    suffix = StringField('Suffix', validators=[Optional(), Length(max=5)])
    class_type_choices = [
        ('', 'None'),
        ('Solo', 'Solo'),
        ('Duet', 'Duet'),
        ('Trio', 'Trio'),
        ('Quartet', 'Quartet'),
        ('Quintet', 'Quintet'),
        ('Recital', 'Recital'),
        ('Large Group', 'Large Group'),
    ]
    class_type = SelectField('Class Type', choices=class_type_choices, validators=[Optional()])
    name = StringField('Name', validators=[Optional(), Length(max=60)])
    discipline_choices = [
        ('', 'None'),
        ('Strings', 'Strings'),
        ('Piano', 'Piano'),
        ('Voice', 'Voice'),
        ('Winds', 'Winds'),
    ]
    discipline = SelectField('Discipline', choices=discipline_choices, validators=[Optional()])
    fee = IntegerField('Fee', validators=[DataRequired()])
    adjudication_time = IntegerField('Adjudication Time', validators=[Optional()])
    move_time = IntegerField('Move Time', validators=[Optional()])
    submit = SubmitField('Update')
    
class EditRepertoireForm(FlaskForm):
    id = HiddenField('ID')
    title = StringField('Title', validators=[DataRequired(), Length(max=60)])
    composer = StringField('Composer', validators=[DataRequired(), Length(max=60)])
    discipline_choices = [
        ('', 'None'),
        ('Strings', 'Strings'),
        ('Piano', 'Piano'),
        ('Voice', 'Voice'),
        ('Winds', 'Winds'),
    ]
    discipline = SelectField('Discipline', choices=discipline_choices, validators=[Optional()])
    type_choices = [
        ('', 'None'),
        ('Solo', 'Solo'),
        ('Duet', 'Duet'),
        ('Trio', 'Trio'),
        ('Quartet', 'Quartet'),
        ('Quintet', 'Quintet'),
        ('Recital', 'Recital'),
        ('Large Group', 'Large Group'),
    ]
    type = SelectField('Type', choices=type_choices, validators=[Optional()])
    level = StringField('Level', validators=[Optional(), Length(max=60)])
    duration = IntegerField('Duration', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()], render_kw={"rows": 10, "placeholder": "Enter description here..."})
    submit = SubmitField('Update')


class ConfirmFestivalDataDelete(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter password..."})
    submit = SubmitField('Delete Data')