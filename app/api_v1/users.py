"""
Users API Routes
"""
from flask import jsonify
from app.api_v1 import bp
from app.api_v1.auth import token_auth
from app.api_v1.errors import error_response
from app.database.models import User

@bp.route('/users/<int:user_id>', methods=['GET'])
@token_auth.login_required
def get_user(user_id):
    """Returns user from id"""
    user = User.query.filter_by(id=user_id).first()
    if user is not None:
        return jsonify(user.to_json(admin=False))
    return error_response(404, "user id doesn't exist")
