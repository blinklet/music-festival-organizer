title: Use blueprints to organize a Flask application
slug: flask-blueprints-python
summary: I am starting a large Flask project so I need to define the project structure. I discovered that there are many different opinions about how a large Flask project should be organized. After some consideration and testing, I decided on the structure I describe in this post.
date: 2024-04-01
modified: 2024-04-01
category: Flask
status: Draft

# Look into Flask-AppBuilder extension


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

I am starting a large Flask project so I needed to define the project structure. I discovered that there are many different opinions about how a large Flask project should be organized. After some consideration and testing, I decided on the structure I describe in this post.

# Project structure

To get started, I need a home page, and account page, and an admin page. I decided that each page will have its own blueprint and each blueprint will be fuly self-contained with its own resource files.

The high-level folder structure looks like below. In the application's root folder, I have the main flask app, *app.py*, a config file *config.py*, a [*dotenv* file](https://learningwithcode.com/use-environment-variables-python), and the standard Flask resource folders, *static* and *templates*. Then, I have three blueprint folders named *account*, *admin*, and *home*.  

```text
mfo
├── account
│   ├── account.py
│   ├── static
│   └── templates
|
├── admin
│   ├── admin.py
│   ├── static
│   └── templates
|
├── home
│   ├── home.py
│   ├── static
│   └── templates
|
├── static
├── templates
│
├── app.py
├── config.py
└── .env
```

## Why not create packages?

The Flask documentation [recommends implementing large applications as packages](https://flask.palletsprojects.com/en/3.0.x/patterns/packages/). I may do that later but, for now, I will implement the application as a set of modules because I think it makes it easier to undersatnd the structure of the project.

If I implemented the application as packages, I would add an *\_\_init\_\_.py* in the application directory and in each blueprint directory. Then I would move the logic in the app file and in each blueprint view file into the *\_\_init\_\_.py*. I would have to change some of the import statements in the app's *\_\_init\_\_.py* file now that I am importing packages instead of modules. See the [Flask tutorial](https://flask.palletsprojects.com/en/3.0.x/tutorial/layout/) for an example of implementing a Flask app as a package.

## Why this structure?

I wanted to create a structure that followed the generally-accepted practices of Flask app organization. So I am using the [blueprint structure recommended in the Flask documentation](https://flask.palletsprojects.com/en/3.0.x/blueprints/)

# Building the base files

Most Flask sites need a base template that defines the common look of the web site. Blueprint templates will extend the base template to create specific web pages.
















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





















Based on what I learned in my [previous](https://learningwithcode.com/flask-web-app-tutorial) [projects](https://learningwithcode.com/python-packaging-modern), and also incorporating some new patterns I learned from the [Flask Web App course](https://training.talkpython.fm/courses/details/building-data-driven-web-applications-in-python-with-flask-sqlalchemy-and-bootstrap) from [TalkPython Training](https://training.talkpython.fm/), 





```text
mfo
├── account
│   ├── account.py
│   ├── static
│   │   └── account
│   │       ├── css
│   │       │   └── styles.css
│   │       └── img
│   └── templates
│       └── account
│           ├── index.html
│           ├── login.html
│           └── register.html
├── admin
│   ├── admin.py
│   ├── static
│   │   └── admin
│   │       └── css
│   └── templates
│       └── admin
│           └── index.html
├── home
│   ├── home.py
│   ├── static
│   │   └── home
│   │       └── css
│   └── templates
│       └── home
│           └── index.html
├── static
│   ├── css
│   │   └── shared_styles.css
│   └── img
│
├── templates
│   └── shared_layout.html
│
├── app.py
├── config.py
└── .env
```