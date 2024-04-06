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

I am starting a large Flask project so I needed to define the project structure. I discovered that there are several different opinions about how a large Flask project should be organized. After some consideration and testing, I decided on the structure I describe in this post.

Also, I want to save readers the same aggravation I felt when troubleshooting some issues I found while developing the view functions and template files in this structure by clearly describing the rules Flask follows when searching for template files in blueprint folders, and by providing concrete examples.

# Project structure

To get started, I need a home page, and account page, and an admin page. I decided that each page will have its own blueprint and each blueprint will be fully self-contained with its own resource files.

The high-level folder structure looks like below. In the application's root folder, I have the main flask app, *app.py*, a config file *config.py*, a [*dotenv* file](https://learningwithcode.com/use-environment-variables-python), and the standard Flask resource folders, *static* and *templates*. Then, I have three blueprint folders named *account*, *admin*, and *home*.  

```text
mfo
├── account
│   ├── views.py
│   ├── static
│   └── templates
|
├── admin
│   ├── views.py
│   ├── static
│   └── templates
|
├── home
│   ├── views.py
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

The Flask documentation [recommends implementing large applications as packages](https://flask.palletsprojects.com/en/3.0.x/patterns/packages/). I may do that later but, for now, I will implement the application as a set of modules because I think that implementation makes it easier to understand the structure of the project. See the [official Flask tutorial](https://flask.palletsprojects.com/en/3.0.x/tutorial/layout/) for an example of implementing a Flask app as a package. 

Also, see my [previous post about packaging Python applications](https://learningwithcode.com/python-packaging-modern) if you need more information about packging.

## Why this structure?

After [learning the basics of Flask]([previous](https://learningwithcode.com/flask-web-app-tutorial)), I wanted to create a program structure that followed the generally-accepted practices of Flask application organization. So, I am using the [blueprint structure recommended in the Flask documentation](https://flask.palletsprojects.com/en/3.0.x/blueprints/). I prefer to keep all code related to each blueprint in the same blueprint folder.

There are some alternative application structures one could consider. These organize the blueprint view files all in one folder and have common *templates* and *static* folders for the entire application. See the [DigitalOcean Flask blueprint tutorial](https://www.digitalocean.com/community/tutorials/how-to-structure-a-large-flask-application-with-flask-blueprints-and-flask-sqlalchemy).

# Building the base files

I started building my application in the simplest way, by creating a Flask application file, a template file, and a CSS file. To support the application, I also created a configuration file.

The application structure was as shown below:

```text
mfo
├── static
│   └── css
│       └── styles.css
├── templates
│   └── index.html
├── app.py
├── config.py
└── .env
```

## The Flask application file

For now, the Flask application file, *app.py* just creates the Flask app object and configures it. The file is listed below:

```python
# app.py

import flask

app = flask.Flask(__name__)
app.config.from_pyfile('config.py')

@app.route('/')
def index():
    return flask.render_template('/index.html')

if __name__ == "__main__":
    app.run()
```

## The configuration files

The *config.py* file reads environment variables

```python
# config.py

import os
import dotenv

dotenv.load_dotenv()

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
ENVIRONMENT = os.environ.get("FLASK_ENVIRONMENT")
DEBUG = os.environ.get("FLASK_DEBUG")
EXPLAIN_TEMPLATE_LOADING = os.environ.get("FLASK_EXPLAIN_TEMPLATE_LOADING")
```

The *dotenv* file, *.env*,  is used to define the environment variables that will be exported to the *config.py* file. If environment variables are already set in the shell, they will be used instead of the variables in the *dotenv* file.

```python
# .env

FLASK_APP = app
FLASK_SECRET_KEY = abcd

FLASK_ENVIRONMENT = development
FLASK_DEBUG = True
FLASK_EXPLAIN_TEMPLATE_LOADING = True
```
## The template file

Most Flask sites need a base template that defines the common look of the web site. Blueprint templates will extend the base template to create specific web pages.

```html
<!-- templates/index.html -->

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Example Website{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/styles.css" />
    {% block additional_css %}{% endblock %}
</head>

<body>
    <div class="main_content">
        {% block main_content %}
        <h1>This is a simple example page</h1>
        {% endblock %}
    </div>
</body>
</html>
```


## The CSS file

```css
/*  static/css/styles.css  */

.main_content {
    padding: 20px;
}

h1 {
    font-weight: bold;
    color: rgb(255, 0, 0);
    font-size: 32px;
  }
```

## Testing the application

Go to the folder above the application folder and run the flask application

```text
$ cd ..
$ ls
mfo
$ flask --app mfo.app run
```

![](./images/basic-page-01.png)

```text
[2024-04-05 13:41:55,248] INFO in debughelpers: Locating template '/index.html':
    1: trying loader of application 'app'
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/mfo/templates
       -> found ('/home/brian/Projects/mfo/templates/index.html')
127.0.0.1 - - [05/Apr/2024 13:41:55] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [05/Apr/2024 13:41:55] "GET /static/css/styles.css HTTP/1.1" 200 -
```

# Creating a blueprint

Now I want to create a page for "accounts". It will eventually support account functions like logging into a user acount, displaying user information if the user is logged in, and registering new users. For now, it will just be a dummy page with two links to a "login" dummy page and a "register" dummy page. 

I will implement this new page as a blueprint, instead of adding more Flask routes to the *app.py* file.

In the application folder, I created a new folder named *account*. In that folder, I created a blueprint file containing the blueprint definition and the routes supported by the blueprint. I also created new subfolders named *template* and *static*, which will contain the template files and CSS files that support the "accounts" page.

The blueprint folder structure will look like below:

```text
mfo
├── account
│   ├── views.py
│   ├── static
│   │   └── css
│   │       └── styles.css
│   └── templates
│       └── account
│           ├── index.html
│           ├── login.html
│           └── register.html
...
```

I modified the main Flask application file, *app.py*, so it registered the new *account* blueprint. In addition, I changed the main template name to *shared_layout.html* because it will be a shared resource used by all the blueprint templates. It contains navigation links to the different site pages which are, at this point, the *home* page and the *account* page.

The remaining files in the application folder have the following structure, which is the same as the simple example I started with, except the template's file name is different:

```text
...
├── static
│   └── css
│       └── styles.css
├── templates
│   └── shared_layout.html
├── app.py
├── config.py
└── .env
```

## The blueprint file

```python
# account/views.py

import flask

bp = flask.Blueprint(
    'account',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/account',
    )

@bp.route('/')
def index():
    return flask.render_template('/account/index.html')

@bp.route('/login')
def login():
    return flask.render_template('/account/login.html')

@bp.route('/register')
def register():
    return flask.render_template('/account/register.html')
```

## Registering the blueprint

```python
# app.py

import flask

app = flask.Flask(__name__)
app.config.from_pyfile('config.py')

# Register blueprint
from mfo.account import account
app.register_blueprint(account.bp)

@app.route('/')
def index():
    return flask.render_template('/shared_layout.html')

if __name__ == "__main__":
    app.run()
```

## The blueprint static folder

I bundles a CSS file named *styles.css* with the *account* template to demonstrate how the blueprint finds its own bundled static files. The main application CSS file will color all *Heading1* tags black, along with other styles, but the CSS file in the *account* blueprint will change *Heading1* text to red. 

```css
/* account/static/css/styles.css */

h1 {
    color: rgb(255, 0, 0);
  }
```

Any template used by the *account* blueprint can add this additional CSS file and, in this example, the *login.html* template will add this CSS file. 

## The blueprint templates

I created templates for the three account pages: the main account page is *index.html*, the login page is *login.html*, and the registration page is *register.html*.

### The main account page template

```html
<!-- account/templates/account/index.html -->

{% extends "shared_layout.html" %}
{% block title %}User Information{% endblock %}

{% block main_content %}
    <div>
        <h1>Your user account</h1>

        <div>
            Welcome to your account!
        </div>
        <div>
            What do you want to do?
        </div>
        <div>
            <a href = "{{url_for('account.login')}}">Login</a>
            <a href = "{{url_for('account.register')}}">Register</a>
        </div>
    </div>
{% endblock %}

{% block additional_css %}{% endblock %}
```

### The login page template

The *login.html* template adds an additional CSS file, which will extend or overwrite the CSS from the Flask application's main CSS file. This demonstrates how the blueprint finds its own bundled static files.

```html
<!-- account/templates/account/login.html -->

{% extends "shared_layout.html" %}
{% block title %}Login to your account{% endblock %}

{% block main_content %}
    <div>
        <h1>Login form</h1>

        <div>
            Placeholder for a login form
        </div>
    </div>
{% endblock %}

{% block additional_css %}
    <link rel="stylesheet" href="{{ url_for('account.static', filename='css/styles.css') }}" >
{% endblock %}
```

### The registration page template

```html
<!-- account/templates/account/register.html -->

{% extends "shared_layout.html" %}
{% block title %}Register a new user{% endblock %}

{% block main_content %}
    <div class="form-container">
        <h1>Register form</h1>

        <div>
            Placeholder for a user registration form
        </div>
    </div>
{% endblock %}

{% block additional_css %}{% endblock %}
```

## The shared layout template

In the main application template, now named *shared_layout.html*, I added navigation links in a nav bar

```html
<!-- templates/shared_layout.html -->

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Music Festival Website{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/styles.css" />
    {% block additional_css %}{% endblock %}
</head>

<body>
    <nav>
        <a href="/">Home</a>
        <a href="{{ url_for('account.index') }}">Account</a>
    </nav>

    <div class="main_content">
        {% block main_content %}
        <h1>This is a simple example page</h1>
        {% endblock %}
    </div>
</body>
</html>
```

I also added some styles for the nav bar in the main CSS file, *static/css/styles.css*:

```css
/* static/css/styles.css */

.main_content {
    padding: 20px;
}

h1 {
    font-weight: bold;
    color: rgb(0, 0, 0);
    font-size: 32px;
  }

nav {
    background-color: rgb(15, 63, 196);
    padding: 10px;
    font-size: 15px;
    color: white;
}

nav > a {
    color: white;
    margin-right: 10px;
}
```

## testing the blueprint

Home page

![](./images/blueprint-pages-01.png)

```text
[2024-04-05 16:58:43,833] INFO in debughelpers: Locating template '/shared_layout.html':
    1: trying loader of application 'mfo.app'
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/templates
       -> found ('/home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/templates/shared_layout.html')
    2: trying loader of blueprint 'account' (mfo.account.views)
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/account/templates
       -> no match
127.0.0.1 - - [05/Apr/2024 16:58:43] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [05/Apr/2024 16:58:43] "GET /static/css/styles.css HTTP/1.1" 304 -
```

account page

![](./images/blueprint-pages-02.png)

```text
[2024-04-05 17:00:57,986] INFO in debughelpers: Locating template '/account/index.html':
    1: trying loader of application 'mfo.app'
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/templates
       -> no match
    2: trying loader of blueprint 'account' (mfo.account.views)
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/account/templates
       -> found ('/home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/account/templates/account/index.html')
[2024-04-05 17:00:57,988] INFO in debughelpers: Locating template 'shared_layout.html':
    1: trying loader of application 'mfo.app'
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/templates
       -> found ('/home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/templates/shared_layout.html')
    2: trying loader of blueprint 'account' (mfo.account.views)
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/account/templates
       -> no match
127.0.0.1 - - [05/Apr/2024 17:00:57] "GET /account/ HTTP/1.1" 200 -
127.0.0.1 - - [05/Apr/2024 17:00:58] "GET /static/css/styles.css HTTP/1.1" 304 -
```

login page

![](./images/blueprint-pages-03.png)

```text
[2024-04-05 17:02:11,243] INFO in debughelpers: Locating template '/account/login.html':
    1: trying loader of application 'mfo.app'
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/templates
       -> no match
    2: trying loader of blueprint 'account' (mfo.account.views)
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/account/templates
       -> found ('/home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/account/templates/account/login.html')
127.0.0.1 - - [05/Apr/2024 17:02:11] "GET /account/login HTTP/1.1" 200 -
127.0.0.1 - - [05/Apr/2024 17:02:11] "GET /static/css/styles.css HTTP/1.1" 304 -
127.0.0.1 - - [05/Apr/2024 17:02:11] "GET /account/static/css/styles.css HTTP/1.1" 304 -
```

# Creating more blueprints

This is where we could run into namespace issues for tempaltes

Add an *admin* blueprint for an admin page and move the route for the home page to a *home* blueprint. The structure of the addition folders is:

```text
...
├── admin
│   ├── views.py
│   ├── static
│   │   └── css
│   └── templates
│       └── admin
│           └── index.html
├── home
│   ├── views.py
│   ├── static
│   │   └── css
│   └── templates
│       └── home
│           └── index.html
...
```

## The *admin* view file

```python
# app.py

import flask

app = flask.Flask(__name__)
app.config.from_pyfile('config.py')

# Register blueprints
import mfo.account.views
import mfo.admin.views
import mfo.home.views
app.register_blueprint(mfo.account.views.bp)
app.register_blueprint(mfo.admin.views.bp)
app.register_blueprint(mfo.home.views.bp)

if __name__ == "__main__":
    app.run()
```

## The *admin* template

```html
<!-- admin/templates/admin/index.html -->

{% extends "shared_layout.html" %}
{% block title %}Admin page{% endblock %}

{% block main_content %}
    <div>
        <h1>Administration page</h1>

        <div>
            Placeholder for admin tools
        </div>
    </div>
{% endblock %}

{% block additional_css %}{% endblock %}
```

## The *home* view file

```python
# home/views.py

import flask

bp = flask.Blueprint(
    'home',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/',
    )

@bp.route('/')
def index():
    return flask.render_template('/home/index.html')
```

## The *home* template

```html
<!-- home/templates/home/index.html -->

{% extends "shared_layout.html" %}
{% block title %}Home page{% endblock %}

{% block main_content %}
    <div>
        <h1>Home page</h1>

        <div>
            Placeholder for website!
        </div>
    </div>
{% endblock %}

{% block additional_css %}{% endblock %}
```

## The updated *app.py* file

Removed the original "/" route because it is now in the *home* blueprint. Registered the *admin* and *home* blueprints

```python
# app.py

import flask

app = flask.Flask(__name__)
app.config.from_pyfile('config.py')

# Register blueprints
import mfo.account.views
import mfo.admin.views
import mfo.home.views
app.register_blueprint(mfo.account.views.bp)
app.register_blueprint(mfo.admin.views.bp)
app.register_blueprint(mfo.home.views.bp)

if __name__ == "__main__":
    app.run()
```

Now, the *app.py* file contains no routes or view functions. It simply configures the Flask app object with configuration variables and blueprints.

Currently, all program logic is in the blueprint folders. When I add a database or otehr common components, I may have to place program logic in other folders that are 

## Testing new pages

Admin page

![](./images/blueprint-pages-05.png)

```text
[2024-04-05 18:05:59,994] INFO in debughelpers: Locating template '/admin/index.html':
    1: trying loader of application 'mfo.app'
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/templates
       -> no match
    2: trying loader of blueprint 'account' (mfo.account.views)
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/account/templates
       -> no match
    3: trying loader of blueprint 'admin' (mfo.admin.views)
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/admin/templates
       -> found ('/home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/admin/templates/admin/index.html')
    4: trying loader of blueprint 'home' (mfo.home.views)
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/home/templates
       -> no match
[2024-04-05 18:06:00,000] INFO in debughelpers: Locating template 'shared_layout.html':
    1: trying loader of application 'mfo.app'
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/templates
       -> found ('/home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/templates/shared_layout.html')
    2: trying loader of blueprint 'account' (mfo.account.views)
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/account/templates
       -> no match
    3: trying loader of blueprint 'admin' (mfo.admin.views)
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/admin/templates
       -> no match
    4: trying loader of blueprint 'home' (mfo.home.views)
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/home/templates
       -> no match
127.0.0.1 - - [05/Apr/2024 18:06:00] "GET /admin/ HTTP/1.1" 200 -
127.0.0.1 - - [05/Apr/2024 18:06:00] "GET /static/css/styles.css HTTP/1.1" 304 -
```

Home page

![](./images/blueprint-pages-06.png)

```text
[2024-04-05 18:09:46,863] INFO in debughelpers: Locating template '/home/index.html':
    1: trying loader of application 'mfo.app'
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/templates
       -> no match
    2: trying loader of blueprint 'account' (mfo.account.views)
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/account/templates
       -> no match
    3: trying loader of blueprint 'admin' (mfo.admin.views)
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/admin/templates
       -> no match
    4: trying loader of blueprint 'home' (mfo.home.views)
       class: jinja2.loaders.FileSystemLoader
       encoding: 'utf-8'
       followlinks: False
       searchpath:
         - /home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/home/templates
       -> found ('/home/brian/Projects/Music Festival Program/music-festival-organizer/mfo/home/templates/home/index.html')
127.0.0.1 - - [05/Apr/2024 18:09:46] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [05/Apr/2024 18:09:46] "GET /static/css/styles.css HTTP/1.1" 304 -
```

# Templates in Flask blueprint folders

The flask blueprint enables you to specify the folder in which all your static files will be found and it only looks in that folder. It does not search for other static files in other namespaces.

But, templates work differently. The Flask developers wanted you to be able to "override" one template file with another of the same name if you wanted to.

This is why you need to use the naming convention we use with the seemingly unneccessary template folder structure. You need a unique string to identify the template if you are using generic filenames like *index.html*. So */account/index.html* is unique.

Setting the template folder in the blueprint definition to *templates/account* and then referencing the template with only the filename *index.html* will not work. Flask will look for *index.html* in every other blueprint's template folder and in the main application templates folder and will use the first on that was registered

https://realpython.com/flask-blueprint/#including-templates


















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



# Final app structure   

The final application structure is shown below. this supports navigating between blueprints and is a good base upon which to buid the rest of my application.

```text
mfo
├── account
│   ├── static
│   │   └── css
│   │       └── styles.css
│   ├── templates
│   │   └── account
│   │       ├── index.html
│   │       ├── login.html
│   │       └── register.html
│   └── views.py
|
├── admin
│   ├── static
│   │   └── css
│   ├── templates
│   │   └── admin
│   │       └── index.html
│   └── views.py
|
├── home
│   ├── static
│   │   └── css
│   ├── templates
│   │   └── home
│   │       └── index.html
│   └── views.py
|
├── app.py
├── config.py
├── .env
├── requirements.txt
├── static
│   └── css
│       └── styles.css
└── templates
    └── shared_layout.html
```



























and also incorporating some new patterns I learned from the [Flask Web App course](https://training.talkpython.fm/courses/details/building-data-driven-web-applications-in-python-with-flask-sqlalchemy-and-bootstrap) from [TalkPython Training](https://training.talkpython.fm/), 
