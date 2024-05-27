import wtforms as fm
import phonenumbers
from flask_wtf import FlaskForm


class ProfileEdit(FlaskForm):

    first_name = fm.StringField('First Name', [fm.validators.InputRequired()])
    last_name = fm.StringField('Last Name', [fm.validators.InputRequired()])
    birthdate = fm.DateField('Birth Date')
    
    address = fm.StringField('Street Address')
    city = fm.StringField('City')
    province = fm.StringField('Province')
    postal_code = fm.StringField('Postal Code')

    phone = fm.StringField('Phone')
    school = fm.StringField('School')
    teacher = fm.StringField('Teacher')

    comments = fm.TextAreaField('Comments')
    national_festival  =  fm.BooleanField('Eligible for the National Festival')

    submit = fm.SubmitField('Save changes')

    # https://stackoverflow.com/questions/36251149/validating-us-phone-number-in-wtforms
    def validate_phone(form, field):
        if len(field.data) > 16:
            raise fm.ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise fm.ValidationError('Invalid phone number.')
        except:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise fm.ValidationError('Invalid phone number.')
