"""
Initialises Home
"""
from flask import Blueprint

bp = Blueprint('home', __name__, template_folder='templates', static_folder='files')

from app.home import routes
