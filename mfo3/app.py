import flask


app = flask.Flask(__name__)

app.config.from_pyfile('config.py', silent=True)

from mfo2.views import greetings
app.register_blueprint(greetings.bp)


if __name__ == "__main__":
    app.run()