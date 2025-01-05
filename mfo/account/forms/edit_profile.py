# mfo/account/forms/edit_profile.py

import wtforms
import phonenumbers
import datetime
from flask_wtf import FlaskForm


def validate_at_least_one_role(form, field):
    if not field.data or len(field.data) == 0:
        raise wtforms.ValidationError("At least one role must be selected")
    
def validate_group_or_participant(form, field):
    if 'Group' in form.rolenames.data and 'Participant' in form.rolenames.data:
        raise wtforms.ValidationError("Profile can be a 'Group' or a 'participant', but not both")

class ProfileEdit(FlaskForm):

    def validate_birthday(form, field):
        # I used a the name "validate_birthday" instead of "validate_birthdate"
        # because the field is named "birthdate" in the form. This avoids a
        # doubled validation error message.
        
        if not field.data:
            # workaround for wtforms validation bug
            # https://stackoverflow.com/questions/37026390/dont-want-to-validate-a-datefield-in-wtforms-but-want-to-keep-the-date-format
            field.errors[:] = []

            if 'Participant' in form.rolenames.data:
                raise wtforms.ValidationError('Participants must enter their birthdate')
        else:
            if field.data > datetime.date.today():
                raise wtforms.ValidationError('Birthdate is in the future.')
            
    def validate_phone(form, field):
    # https://stackoverflow.com/questions/36251149/validating-us-phone-number-in-wtforms
        if field.data:
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

    name = wtforms.StringField(
        'Full Name', 
        [wtforms.validators.InputRequired()]
        )
    birthdate = wtforms.DateField('Birth Date',  validators=[validate_birthday])

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
    
    rolenames = wtforms.SelectMultipleField(
        'Roles',
        choices=[
            ('Participant', 'Participant'), 
            ('Teacher', 'Teacher'), 
            ('Guardian', 'Parent or Guardian'), 
            ('Accompanist', 'Accompanist'), 
            ('Adjudicator', 'Adjudicator'),
            ('Admin', 'Admin'),
            ],
        default=['Participant'],
        option_widget=wtforms.widgets.CheckboxInput(),
        widget=wtforms.widgets.ListWidget(prefix_label=False),
        validators=[validate_at_least_one_role]
    )
    submit = wtforms.SubmitField('Save changes')

    