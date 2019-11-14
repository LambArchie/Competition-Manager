"""
Controls users admin pages
"""
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from app import db
from app.database.models import User
from app.admin import bp
from app.admin.routes import check_permissions
from app.api_v1.admin import get_users
from app.auth.forms import RegistrationForm, ChangePasswordForm
from app.user.forms import EditProfileForm

@bp.route('/users/')
@login_required
def user_management():
    """Displays users in a table"""
    check_permissions()
    return render_template('admin/userTable.html', title="User Management")

@bp.route('/users/get') #Don't change, hardcoded in js
@login_required
def api_users():
    """Dummy function, calls other function"""
    check_permissions()
    return get_users()

@bp.route('/users/user/<username>/edit', methods=['GET', 'POST']) #Don't change, hardcoded in js
@login_required
def user_edit(username):
    """Allows admin to edit user information"""
    check_permissions()
    user = User.query.filter_by(username=username).first_or_404()
    form = EditProfileForm(user.username, user.email)
    if form.validate_on_submit():
        user.name = form.name.data
        user.organisation = form.organisation.data
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash('Updated successfully')
        return redirect(url_for('admin.user_management'))
    elif request.method == 'GET':
        form.name.data = user.name
        form.organisation.data = user.organisation
        form.username.data = user.username
        form.email.data = user.email
    return render_template('admin/edit_profile.html', title='Edit Profile', form=form, username=username)

@bp.route('/users/user/<username>/pwreset', methods=['GET', 'POST'])
@login_required
def user_pwreset(username):
    """Allows admin to reset password"""
    check_permissions()
    user = User.query.filter_by(username=username).first_or_404()
    form = ChangePasswordForm()
    del form.currentpassword
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.revoke_token()
        db.session.commit()
        flash('Password reset successfully')
        return redirect(url_for('admin.user_management'))
    return render_template('auth/change_password.html', title='Reset Password', form=form)

@bp.route('/users/register', methods=['GET', 'POST'])
@login_required
def register():
    """Registration page"""
    check_permissions()
    form = RegistrationForm()
    del form.recaptcha
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    name=form.name.data,
                    organisation=form.organisation.data,
                    admin=bool(form.admin.data),
                    reviewer=bool(form.reviewer.data)
                    )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User registed successfully')
        return redirect(url_for('admin.admin'))
    return render_template('auth/register.html', title='Register', form=form)
