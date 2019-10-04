"""
Controls which pages load and what is shown on each
"""
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db
from app.database.models import User
from app.admin import bp
from app.api_v1.admin import get_users
from app.auth.forms import RegistrationForm

@bp.route('/')
@login_required
def admin():
    """Shows default admin page if got permissions"""
    if (current_user.admin is False) or (current_user.admin is None):
        return render_template('errors/403.html')
    return render_template('admin/admin.html', title="Users")

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def admin_register():
    """Registration page"""
    if (current_user.admin is False) or (current_user.admin is None):
        return render_template('errors/403.html'), 403
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
def admin_users():
    """Dummy function, calls other function"""
    return get_users()
