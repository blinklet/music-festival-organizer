# mfo/home/forms.py

from flask_security.forms import LoginForm
from wtforms import StringField
from wtforms.validators import DataRequired

class ExtendedLoginForm(LoginForm):
    festival = StringField('Festival', validators=[DataRequired()])
    season = StringField('Season', validators=[DataRequired()])