from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, HiddenField, IntegerField, SelectField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, InputRequired, Length, Optional

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
    number = StringField('Number', validators=[DataRequired(), Length(max=10)])
    suffix = StringField('Suffix', validators=[Optional(), Length(max=5)])
    class_type_choices = class_types
    class_type = SelectField('Class Type', choices=class_type_choices, validators=[Optional()])
    name = StringField('Name', validators=[Optional(), Length(max=60)])
    discipline_choices = disciplines
    discipline = SelectField('Discipline', choices=discipline_choices, validators=[Optional()])
    fee = IntegerField('Fee', validators=[DataRequired()])
    adjudication_mins = IntegerField('Adjudication Minutes', validators=[InputRequired()])
    adjudication_secs = IntegerField('Adjudication Seconds', validators=[InputRequired()])
    move_mins = IntegerField('Move Minutes', validators=[InputRequired()])
    move_secs = IntegerField('Move Seconds', validators=[InputRequired()])
    submit = SubmitField('Update')
    
class EditRepertoireForm(FlaskForm):
    id = HiddenField('ID')
    title = StringField('Title', validators=[DataRequired(), Length(max=60)])
    composer = StringField('Composer', validators=[DataRequired(), Length(max=60)])
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
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter password..."})
    submit = SubmitField('Delete Data')