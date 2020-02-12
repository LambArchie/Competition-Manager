"""
Initialises API
"""
from flask import Blueprint

bp = Blueprint('api_v1', __name__)

from app.api_v1 import admin, competition, tokens, users
