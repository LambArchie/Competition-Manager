"""
Controls which pages load and what is shown on each
"""

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.models import User
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    """Logout page"""
    logout_user()
    return redirect(url_for('index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if app.config['DISABLE_PUBLIC_REGISTRATION']:
        return render_template('errors/403.html')
    elif current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    del form.admin # Hides option to make user admin
    if app.config['CAPTCHA_ENABLED'] is False:
        del form.recaptcha
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, admin=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password form"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if not user.check_password(form.currentpassword.data):
            flash('Wrong current password')
        elif form.password.data == form.currentpassword.data:
            flash('Same as existing password')
        else:
            user.set_password(form.password.data)
            db.session.commit()
            flash('Your password has been changed successfully.')
            return redirect(url_for('user.user_profile', username=current_user.username))
    return render_template('auth/change_password.html', title='Change Password', form=form)
