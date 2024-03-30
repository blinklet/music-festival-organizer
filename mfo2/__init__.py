import os

import flask


def create_app():
    app = flask.Flask(__name__)

    app.config['SECRET_KEY']='dev'
    app.config['DEBUG']=True

    # A real config file overrides above configs
    app.config.from_pyfile('config.py', silent=True)
    
    from mfo2.views import hello
    app.register_blueprint(hello.bp)

    print(app.url_map)


    return app