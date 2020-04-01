"""
Manages API Auth
"""
from functools import wraps
from sqlalchemy.sql import text
from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app import db
from app.database.models import User
from app.api_v1.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password):
    """Basic HTTP Auth checking"""
    query = text("SELECT * FROM user WHERE username = :username LIMIT 1 OFFSET 0")
    user = db.session.query(User).from_statement(query).params(username=username).first()
    if user is None:
        return False
    g.current_user = user
    return user.check_password(password)

@basic_auth.error_handler
def basic_auth_error():
    """Error if unauthorized"""
    return error_response(401)

@token_auth.verify_token
def verify_token(token):
    """Checks token"""
    g.current_user = User.check_token(token) if token else None
    return g.current_user is not None

@token_auth.error_handler
def token_auth_error():
    """Error if unauthorized"""
    return error_response(401)

def permission_required(permission):
    """Checks if user has the correct permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if permission == 'admin':
                if not g.current_user.admin:
                    return error_response(403, "missing permission {}".format(permission))
            elif permission == 'reviewer':
                if not g.current_user.reviewer:
                    return error_response(403, "missing permission {}".format(permission))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
