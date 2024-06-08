import wtforms
import phonenumbers
from flask_wtf import FlaskForm


class ProfileEdit(FlaskForm):

    name = wtforms.StringField(
        'Full Name', 
        [wtforms.validators.InputRequired()]
        )
    birthdate = wtforms.DateField('Birth Date')

    address = wtforms.StringField('Street Address')
    city = wtforms.StringField('City')
    province = wtforms.StringField('Province')
    postal_code = wtforms.StringField('Postal Code')

    phone = wtforms.StringField('Phone')
    school = wtforms.StringField('School')
    teacher = wtforms.StringField('Teacher')

    comments = wtforms.TextAreaField('Comments')
    national_festival  =  wtforms.BooleanField(
        'Eligible for the National Festival'
        )

    submit = wtforms.SubmitField('Save changes')

    # https://stackoverflow.com/questions/36251149/validating-us-phone-number-in-wtforms
    def validate_phone(form, field):
        if len(field.data) > 16:
            raise wtforms.ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise wtforms.ValidationError('Invalid phone number.')
        except:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise wtforms.ValidationError('Invalid phone number.')
