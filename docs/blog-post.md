title: User authentication in a Flask web app
slug: flask-authentication-web-app
summary: Build a basic web app that can store accounts for different users, using helpful Flask plugins
date: 2024-04-01
modified: 2024-04-01
category: Flask
status: Draft

<!--
A bit of extra CSS code to centre all images in the post
-->
<style>
img
{
    display:block; 
    float:none; 
    margin-left:auto;
    margin-right:auto;
}
</style>

# Project structure

Based on what I learned in my [previous](https://learningwithcode.com/flask-web-app-tutorial) [projects](https://learningwithcode.com/python-packaging-modern), and also incorporating some new patterns I learned from the [Flask Web App course](https://training.talkpython.fm/courses/details/building-data-driven-web-applications-in-python-with-flask-sqlalchemy-and-bootstrap) from [TalkPython Training](https://training.talkpython.fm/), I organized my Flask project in the following way:

```text
project
├── mfo
|   ├── .env
│   ├── app.py
│   ├── bin
│   ├── models
│   ├── static
│   |   ├── css
│   |   └── img
│   ├── templates
│   |   ├── account
│   |   ├── home
|   |   └── shared
|   └── views
├── tests
├── docs
├── requirements.txt
└── venv
```

Below, I made some notes about the files and folders in the project.

#### *.env*

The *dotenv* file is excluded from source control because it will contain keys and passwords that I do not want published on GitHub. 

I documented the information required in the file, using fake data, in the *docs/dotenv.example* file.

#### *app.py*

The Flask app is run from the *app.py* file. I am following the standard convention for Flask apps in this case.

#### *bin*

The *bin* folder contains programs that help the developer and administrator manage the back end of the site. Usually these files will not be accessible from the web app and must be run from the command line.

I will create an *import_data.py* program that reads data from an excel file that contains the results from a Google form and writes the data into an SQL database.

#### *models*

Following a new pattern I learned in teh TalkPython Web App course, I will store SQLAlchemy models in different files. I currently plan to define the *users* and *roles* tables in *users.py* and the association table that maps users to roles in the *association.py* file.

#### *static*

The *static* folder will contain CSS and image files needed to refine the look of the web app

#### *templates*

Following a new patterns I also learned in teh Web App course, I will organize Jinja2 template files into folders named after each route in the Flask program. Each folder will contain at least an *index.html* file and may contain other files if the program needs to change the web page.

#### *views*

The *views* folder contains the logic associated with each Flask route. Following another new pattern, I am organizing route handlers, or views, in different files. Each view file is associated with a corresponding template folder. 

This requires the use of [Flask Blueprints](https://flask.palletsprojects.com/en/3.0.x/blueprints/), which might be overkill at this point, but which will be helpful later when this program increases in scope.

# Install requirements

```
# mfo/requirements.txt

flask
```

Create virtual environment. Go to the top-level *project* folder.

```text
(venv) $ python3 -m venv venv
(venv) $ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

Enter the following "hello world" text into the *mfo/app.py* file.

```python
import flask

app = flask.Flask(__name__)


@app.route('/<color>')
def index(color):
    return 'Hello world'


if __name__ == "__main__":
    app.run()
```

Run the app from the top-level prohect folder:

```text
(venv) $ python -m mfo.app
```

or,

```text
(venv) $ export FLASK_APP=mfo.app
(venv) $ flask run
```




























```text
project
├── pyproject.toml
├── mfo
|   ├── .env
|   ├── __init__.py
│   ├── app.py
│   ├── bin
│   │   └── import_data.py
│   ├── models
│   |   ├── association.py
│   |   └── users.py
│   ├── static
│   |   ├── css
│   |   └── img
│   ├── templates
│   |   ├── account
│   |   │   ├── index.html
│   |   │   ├── login.html
|   |   |   └── register.html
│   |   ├── home
│   |   |   ├── index.html
|   |   |   └── about.html
|   |   └── shared
|   |       └── _layout.html
|   └── views
│       ├── account_views.py
│       └── home_views.py
├── tests
├── docs
|   └── dotenv.example
├── requirements.txt
└── venv
```