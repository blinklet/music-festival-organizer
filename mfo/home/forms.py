# mfo/home/forms.py

from sqlalchemy import select
from flask_security.forms import LoginForm
from wtforms import SelectField
from wtforms.validators import DataRequired

from mfo.database.base import db
from mfo.database.models import Festival

class ExtendedLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stmt = select(Festival)
        festivals = db.session.execute(stmt).scalars().all()
        self.festival.choices = [(festival.name, festival.name) for festival in festivals]
    
    def validate(self, extra_validators=None):
        # Put code here if you want to do stuff before login attempt

        if not self.is_submitted():
            return False

        response = super(ExtendedLoginForm, self).validate(extra_validators=extra_validators)

        # Put code here if you want to do stuff after login attempt

        return response

    festival = SelectField('Festival', validators=[DataRequired()])

