import flask

bp = flask.Blueprint('anyname', __name__, url_prefix='/greetings')
# Blueprint name 'hello' is only to register the blueprint
# if you add ,url_prefix='/auth' to the function parameters
# all routes will start with "/auth" (note the last slash)
# and routes using the blueprint will add to that path
# so you would get /auth/hello in the following example

# name is used when referring to blueprint path 
# url_for uses the 'name' and outputs the url_prefix to build the path
# example: url_for(anyname.hello) generates /auth/hello

# a simple page that says hello
@bp.route('/hello')
def hello():
    return 'Hello, World!'

# Could also have separate templates and static folder
# to completely separate blueprint into an independent
# set of code that could be re-used by other apps
# https://realpython.com/flask-blueprint/

# Could organize blueprints as packages where the
# folder name is what's imported and the blueprint
# views are in __init__.py in the folder
# Then have the blueprint static and template folders in teh same
# blueprint folder
# https://flask.palletsprojects.com/en/3.0.x/blueprints/#blueprint-resources

# BUT, that's assuming we will want to reuse cide and
# what about using shared templates for common element??


