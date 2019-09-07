"""
Controls general errors which may occur
"""
from flask import render_template, request
from app import db
from app.errors import bp
from app.api_v1.errors import error_response as api_error_response

def wants_json_response():
    """Checks if JSON or HTML should be returned"""
    return request.accept_mimetypes['application/json'] >= \
        request.accept_mimetypes['text/html']

@bp.app_errorhandler(403)
def forbidden(error):
    """403 Forbidden handling"""
    if wants_json_response():
        return api_error_response(403)
    return render_template('errors/403.html'), 403

@bp.app_errorhandler(404)
def not_found_error(error):
    """404 Page Missing handling"""
    if wants_json_response():
        return api_error_response(404)
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    """500 Server Error handling"""
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return render_template('errors/500.html'), 500
