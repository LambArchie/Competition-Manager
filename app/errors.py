"""
Controls general errors which may occur
"""
from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    """404 Page Missing handling"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 Server Error handling"""
    db.session.rollback()
    return render_template('errors/500.html'), 500
