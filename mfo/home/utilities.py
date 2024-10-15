# mfo/home/utilities.py
 
import flask

def get_identity_attributes():
    identity_attributes = flask.current_app.config.get(
        'SECURITY_USER_IDENTITY_ATTRIBUTES', 
        []
    )
    if identity_attributes:
        # list comprehension copied from 
        # https://github.com/pallets-eco/flask-security/blob/main/flask_security/utils.py
        return [[*f][0] for f in identity_attributes]
    return []




