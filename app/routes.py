"""
Controls which pages load and what is shown on each
"""
from datetime import datetime
from flask import render_template, g
from flask_login import current_user, login_required
from app import app, db

@app.before_request
def before_request():
    """Code which is run before every request"""
    g.current_user = current_user
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    else:
        g.current_user.admin = False

@app.route('/')
@app.route('/index')
@login_required
def index():
    """Landing page"""
    return render_template('index.html', title='Home')
