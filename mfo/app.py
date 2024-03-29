import flask
import flask_wtf
import wtforms

app = flask.Flask(__name__)

app.config['SECRET_KEY'] = 'a temporary value'
csrf = flask_wtf.CSRFProtect(app)

class MyForm(flask_wtf.FlaskForm):
    color = wtforms.StringField(
        'Next color: ',
        validators=[wtforms.validators.DataRequired()]
        )
    submit = wtforms.SubmitField('Submit')


@app.route("/", methods=('GET','POST'))
def index():
    form = MyForm()

    if form.validate_on_submit():
        color = form.color.value
        print(f'################ {color}')
        return flask.redirect(flask.url_for('/', color=color))

    return flask.render_template(
        'home/index.html', 
        form=form, 
        )


@app.route("/<color>", methods=('GET','POST'))
def colors(color):
    form = MyForm()
    return flask.render_template("home/index.html", form=form, color=color)

if __name__ == "__main__":
    app.run()