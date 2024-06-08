import flask

from mfo.database.base import db
import mfo.database.utilities
import flask_security

from mfo.account.forms.edit_profile import ProfileEdit

bp = flask.Blueprint(
    'account',
    __name__,
    static_folder='static',
    template_folder='templates',
    url_prefix='/account',
    )

@bp.route('/')
@flask_security.auth_required()
def index():
    user = flask_security.current_user
    profile = mfo.database.utilities.find_primary_profile(user)
    return flask.render_template('/account/index.html', user=user, profile=profile)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@flask_security.auth_required()
def edit_profile():
    user = flask_security.current_user
    profile = mfo.database.utilities.find_primary_profile(user)
    form = ProfileEdit(obj=profile)

    if form.validate_on_submit():
        profile.name = form.name.data
        profile.birthdate = form.birthdate.data
        profile.address = form.address.data
        profile.city = form.city.data
        profile.province = form.province.data
        profile.postal_code = form.postal_code.data
        profile.phone = form.phone.data
        profile.school = form.school.data
        profile.teacher = form.teacher.data
        profile.comments = form.comments.data
        profile.national_festival = form.national_festival.data
        db.session.commit()
        return flask.redirect(flask.url_for('account.index'))

    return flask.render_template('/account/edit_profile.html', form=form)
