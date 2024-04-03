import flask


app = flask.Flask(__name__)
#app.config.from_pyfile('config.py', silent=True)

from mfo3.account import account
app.register_blueprint(account.bp)

from mfo3.home import home
app.register_blueprint(home.bp)

if __name__ == "__main__":
    app.run()