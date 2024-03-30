import flask

bp = flask.Blueprint('anyname', __name__, url_prefix='/auth')
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

