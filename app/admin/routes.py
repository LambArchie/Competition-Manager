"""
Controls main admin pages
"""
from flask import render_template, abort
from flask_login import current_user, login_required
from app.admin import bp

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
