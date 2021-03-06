"""
Controls which pages load and what is shown on each
"""
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app, g, abort
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.database.models import User
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm
from app.auth.setup import check_setup

@bp.before_app_request
def before_request():
    """Code which is run before every request"""
    g.current_user = current_user
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    else:
        g.current_user.admin = False

@bp.after_app_request
def after_request(response):
    """Code which is run just before sending the request to the client"""
    response.headers["X-Frame-Options"] = "deny"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    """Logout page"""
    logout_user()
    return redirect(url_for('home.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if current_app.config['DISABLE_PUBLIC_REGISTRATION']:
        abort(403)
    elif current_user.is_authenticated:
        return redirect(url_for('home.index'))
    if check_setup():
        flash('Please complete initial setup first', 'info')
        return redirect(url_for('auth.initial_setup'))
    form = RegistrationForm()
    del form.admin  # Hides option to make user admin
    del form.reviewer  # Hides option to make user admin
    if current_app.config['CAPTCHA_ENABLED'] is False:
        del form.recaptcha
    if form.validate_on_submit():
        user = User(name=form.name.data,
                    organisation=form.organisation.data,
                    username=form.username.data,
                    email=form.email.data,
                    admin=False,
                    reviewer=False)
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
            flash('Wrong current password', 'error')
        elif form.password.data == form.currentpassword.data:
            flash('Same as existing password', 'info')
        else:
            user.set_password(form.password.data)
            user.revoke_token()
            db.session.commit()
            flash('Your password has been changed successfully.')
            return redirect(url_for('user.user_profile', username=current_user.username))
    return render_template('auth/change_password.html', title='Change Password', form=form)
