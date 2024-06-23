from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, HiddenField

class UploadForm(FlaskForm):
    file = FileField('Spreadsheet File')
    submit = SubmitField('Upload')

class ConfirmForm(FlaskForm):
    confirm = SubmitField('Confirm')
    cancel = SubmitField('Cancel')
    
