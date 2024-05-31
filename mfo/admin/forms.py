from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField

class UploadForm(FlaskForm):
    file = FileField('Spreadsheet')
    submit = SubmitField('Upload')