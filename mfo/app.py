import flask


from mfo.admin import admin
from mfo.home import home
from mfo.account import account

app = flask.Flask(__name__)
app.config.from_pyfile('config.py', silent=True)

#app.config['EXPLAIN_TEMPLATE_LOADING'] = True

app.register_blueprint(home.bp)
app.register_blueprint(account.bp)
app.register_blueprint(admin.bp)


if __name__ == "__main__":
    app.run()