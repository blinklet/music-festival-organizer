from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SubmitField, HiddenField, IntegerField
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
    class_type = StringField('Type', validators=[Optional(), Length(max=20)])
    name = StringField('Name', validators=[Optional(), Length(max=60)])
    discipline = StringField('Discipline', validators=[Optional(), Length(max=30)])
    fee = IntegerField('Fee', validators=[DataRequired()])
    submit = SubmitField('Update')