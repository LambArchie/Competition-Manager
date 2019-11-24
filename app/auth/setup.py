"""
Sets up the application on first launch
"""
from flask import render_template, flash, redirect, url_for, abort
import sqlalchemy
from app import db
from app.database.models import User
from app.auth import bp
from app.auth.forms import RegistrationForm

def check_setup():
    """Checks if setup has already been completed"""
    try:
        if User.query.count() == 0:
            return 1
    except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.ProgrammingError):
        print("Creating databases")
        db.create_all()
        db.session.commit()
        return 1
    return 0

@bp.route('/setup', methods=['GET', 'POST'])
def initial_setup():
    """Performs first time setup"""
    if check_setup():
        form = RegistrationForm()
        del form.admin  # Forces first user to be admin
        del form.reviewer  # Forces first user to be a reviewer
        del form.recaptcha
        if form.validate_on_submit():
            user = User(name=form.name.data,
                        organisation=form.organisation.data,
                        username=form.username.data,
                        email=form.email.data,
                        admin=True,
                        reviewer=True)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Admin user created successfully')
            return redirect(url_for('auth.login'))
        return render_template('auth/register.html', title='Setup - Create Admin', form=form)
    abort(403)
