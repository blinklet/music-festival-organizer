from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, HiddenField, IntegerField, SelectField
from wtforms.validators import DataRequired, InputRequired, Length, Optional

class UploadForm(FlaskForm):
    file = FileField('Spreadsheet File', [InputRequired()])
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
    