"""
Admin API Routes
"""
from distutils.util import strtobool
from flask import jsonify, g, abort, request
from app import db
from app.api_v1 import bp
from app.api_v1.auth import token_auth
from app.api_v1.errors import bad_request, error_response
from app.models import User

def get_users():
    """Returns all users details in json"""
    if (g.current_user.admin is False) or (g.current_user.admin is None):
        error_response(403, "not admin user")
    users = [user.to_json() for user in User.query.all()]
    return jsonify(users)

@bp.route('/admin/users', methods=['GET'])
@token_auth.login_required
def token_get_users():
    """Dummy function, calls other function"""
    return get_users()

@bp.route('/admin/users', methods=['POST'])
@token_auth.login_required
def create_user():
    """Allows creating a user"""
    data = request.get_json() or {}
    if ('username' not in data) or ('email' not in data) or ('password' not in data) or ('admin' not in data):
        return bad_request('must include username, email, password and admin fields')
    if g.current_user.admin is False:
        return error_response(403, "not admin user")
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    try:
        data['admin'] = bool(strtobool(data['admin']))
    except ValueError:
        return bad_request('admin is not boolean')
    user = User()
    user.from_json(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_json())
    response.status_code = 201
    return response