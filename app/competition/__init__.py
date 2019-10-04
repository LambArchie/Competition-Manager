"""
Initialises Main Part
"""
from flask import Blueprint

bp = Blueprint('competition', __name__)

from app.competition import competition, category, review, files, forms
