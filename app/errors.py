"""
Controls general errors which may occur
"""
from flask import render_template, request
from app import app, db
from app.api.errors import error_response as api_error_response

def wants_json_response():
    """Checks if JSON or HTML should be returned"""
    return request.accept_mimetypes['application/json'] >= \
        request.accept_mimetypes['text/html']

@app.errorhandler(404)
def not_found_error(error):
    """404 Page Missing handling"""
    if wants_json_response():
        return api_error_response(404)
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 Server Error handling"""
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return render_template('errors/500.html'), 500
