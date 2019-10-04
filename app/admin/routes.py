"""
Controls which pages load and what is shown on each
"""
from flask import render_template, flash, redirect, url_for, abort
from flask_login import current_user, login_required
from app import db
from app.database.models import User
from app.admin import bp
from app.api_v1.admin import get_users
from app.auth.forms import RegistrationForm

def check_permissions():
    """Checks if can access admin resources"""
    if (current_user.admin is False) or (current_user.admin is None):
        abort(403)

@bp.route('/')
@login_required
def admin():
    """Shows default admin page if got permissions"""
    check_permissions()
    return render_template('admin/admin.html', title="Admin")

@bp.route('/users')
@login_required
def user_management():
    """Displays users in a table"""
    check_permissions()
    return render_template('admin/userTable.html', title="User Management")

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
                    admin=bool(form.admin.data),
                    reviewer=bool(form.reviewer.data)
                    )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User registed successfully')
        return redirect(url_for('admin.admin'))
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/users/get')
@login_required
def api_users():
    """Dummy function, calls other function"""
    return get_users()
