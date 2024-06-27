from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, HiddenField
from wtforms.validators import DataRequired, InputRequired

class UploadForm(FlaskForm):
    file = FileField('Spreadsheet File', [InputRequired()])
    submit = SubmitField('Upload')

class ConfirmForm(FlaskForm):
    confirm = SubmitField('Confirm')
    cancel = SubmitField('Cancel')
    
