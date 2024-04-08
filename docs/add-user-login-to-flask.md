Using Flass-Security-Too basic setup


First, add database config information to *config.py* and, if needed, *.env*

```python
# mfo/config.py

import os
import dotenv

app_dir = os.path.abspath(os.path.dirname(__file__))
project_dir, _unused = os.path.split(app_dir)

print(project_dir)

dotenv.load_dotenv()

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
ENVIRONMENT = os.environ.get("FLASK_ENVIRONMENT")
DEBUG = os.environ.get("FLASK_DEBUG")
EXPLAIN_TEMPLATE_LOADING = os.environ.get("FLASK_EXPLAIN_TEMPLATE_LOADING")

SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")\
     or 'sqlite:///' + os.path.join(project_dir, 'app.db')
SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO")
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")


```

Since I want the database to be stored in the project directory, outside the application directory where *config.py* resides, I need to define the path to the project directory as shown above.


```python
# mfo/.env

FLASK_APP = app
FLASK_SECRET_KEY = abcd

FLASK_ENVIRONMENT = development
FLASK_DEBUG = True
FLASK_EXPLAIN_TEMPLATE_LOADING = True

SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

Since I did not specify the SQLALCHEMY_DATABASE_URI environment variable, my program will use a default development database named *app.py*, stored in the project folder.

## database

Create a database folder and a *setup.py* file

```python
# mfo/database/setup.py
 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
```

# models

Then create a file containing user models

```python
# mfo/database/models/users.py


```

## app.py

Add `from mfo.database import db` and `db.base.init_app(app)` to the app file to configure flask-sqlalchemy using the Flask app configuration established in the *config.py* file. The add the`db.create_all()` statement to build the database tables, if they do not yet exist

```python
# mfo/app.py

import flask

from mfo.database.setup import db

from mfo.admin import admin
from mfo.home import home
from mfo.account import account


app = flask.Flask(__name__)
app.config.from_pyfile('config.py', silent=True)

# Configure Flask extensions
db.init_app(app)

# Register blueprints
app.register_blueprint(home.bp)
app.register_blueprint(account.bp)
app.register_blueprint(admin.bp)


if __name__ == "__main__":
    app.run()
```

