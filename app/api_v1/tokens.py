"""
Manages API Tokens
"""
from flask import jsonify, g
from app import db
from app.api_v1 import bp
from app.api_v1.auth import basic_auth, token_auth

@bp.route('/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    """Get token for current user"""
    token = g.current_user.get_token()
    db.session.commit()
    return jsonify({'token': token})

@bp.route('/tokens', methods=['DELETE'])
@token_auth.login_required
def revoke_token():
    """Revokes token for current user"""
    g.current_user.revoke_token()
    db.session.commit()
    return '', 204
