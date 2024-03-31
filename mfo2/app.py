import flask


app = flask.Flask(__name__)

app.config['SECRET_KEY']='dev'
app.config['DEBUG']=True
# A real config file overrides above configs
#app.config.from_pyfile('config.py', silent=True)

# Register blueprints
# could import the app object into each view file and the view file
# into the app module but that creates creates circular routes
# see https://flask.palletsprojects.com/en/3.0.x/patterns/packages/
#

from mfo2.views import greetings
app.register_blueprint(greetings.bp)

 
print(app.url_map)
print(app.config)

# This is to show how the irl_for uses the blueprint "name" to build URLs
from flask import url_for
app.config['SERVER_NAME'] = 'example.org'
with app.app_context():
    x = url_for('anyname.hello')
    print(x)

if __name__ == "__main__":
    app.run()

