"""
API Routes
"""
from flask import jsonify, g, abort
from app import db
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from app.models import User

@bp.route('/v1/admin/users', methods=['GET'])
@token_auth.login_required
def token_get_users():
    """Dummy function, calls other function"""
    return get_users()

def get_users():
    """Returns all users details in json"""
    if (g.current_user.admin is False) or (g.current_user.admin is None):
        abort(403)
    users = [user.to_json() for user in User.query.all()]
    return jsonify(users)

@bp.route('/v1/admin/users', methods=['POST'])
@token_auth.login_required
def create_user():
    """TODO"""
    pass
