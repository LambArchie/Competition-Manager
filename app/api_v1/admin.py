"""
Admin API Routes
"""
from distutils.util import strtobool
from flask import jsonify, request
from app import db
from app.api_v1 import bp
from app.api_v1.auth import token_auth, permission_required
from app.api_v1.errors import bad_request, error_response
from app.database.models import User

def get_users():
    """Returns all users details in json"""
    users = [user.to_json() for user in User.query.all()]
    return jsonify(users)

@bp.route('/admin/users', methods=['GET'])
@token_auth.login_required
@permission_required('admin')
def token_get_users():
    """Dummy function, calls other function"""
    return get_users()

@bp.route('/admin/users/create', methods=['POST'])
@token_auth.login_required
@permission_required('admin')
def create_user():
    """Allows creating a user"""
    data = request.get_json() or {}
    if (('username' not in data) or ('email' not in data) or ('name' not in data)
            or ('organisation' not in data) or ('password' not in data)
            or ('admin' not in data) or ('reviewer' not in data)):
        return bad_request('must include username, email, name, organisation, password and admin fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    try:
        data['admin'] = bool(strtobool(data['admin']))
    except ValueError:
        return bad_request('admin is not boolean')
    try:
        data['reviewer'] = bool(strtobool(data['reviewer']))
    except ValueError:
        return bad_request('reviewer is not boolean')
    user = User()
    user.from_json(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_json())
    response.status_code = 201
    return response

@bp.route('/admin/users/<int:user_id>', methods=['GET'])
@token_auth.login_required
def get_user_admin(user_id):
    """Returns user from id"""
    user = User.query.filter_by(id=user_id).first()
    if user is not None:
        return jsonify(user.to_json())
    return error_response(404, "user id doesn't exist")

@bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@token_auth.login_required
@permission_required('admin')
def edit_user(user_id):
    """Changes user details"""
    user = User.query.filter_by(id=user_id).first()
    if user is not None:
        data = request.get_json() or {}
        if 'username' in data and data['username'] != user.username \
          and User.query.filter_by(username=data['username']).first():
            return bad_request('please use a different username')
        if 'email' in data and data['email'] != user.email \
          and User.query.filter_by(email=data['email']).first():
            return bad_request('please use a different email')
        user.from_json(data, new_user=False)
        db.session.commit()
        return jsonify(user.to_json())
    return error_response(404, "user id doesn't exist")

@bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@token_auth.login_required
@permission_required('admin')
def delete_user(user_id):
    """Deletes selected user"""
    user = User.query.filter_by(id=user_id).first()
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        return '', 200
    return error_response(404, "user id doesn't exist")
