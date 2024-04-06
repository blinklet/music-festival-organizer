# app.py

import flask

app = flask.Flask(__name__)
app.config.from_pyfile('config.py')

# Register blueprints
import mfo2.account.views
import mfo2.admin.views
import mfo2.home.views
app.register_blueprint(mfo2.account.views.bp)
app.register_blueprint(mfo2.admin.views.bp)
app.register_blueprint(mfo2.home.views.bp)

if __name__ == "__main__":
    app.run()