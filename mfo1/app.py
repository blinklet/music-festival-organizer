import flask


app = flask.Flask(__name__)
app.config.from_pyfile('config.py')

@app.route('/')
def index():
    return flask.render_template('/layout.html')

if __name__ == "__main__":
    app.run()