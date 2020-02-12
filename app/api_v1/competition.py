"""
Competition API Routes
"""
from flask import jsonify
from app.api_v1 import bp
from app.api_v1.auth import token_auth
from app.api_v1.errors import error_response
from app.database.models import Competition, Category, Submission, SubmissionUploads

@bp.route('/competition', methods=['GET'])
@token_auth.login_required
def get_competitions():
    """Returns all competitions running and their id"""
    competitions = [competition.to_json() for competition in Competition.query.all()]
    return jsonify(competitions)

@bp.route('/competition/<int:comp_id>', methods=['GET'])
@token_auth.login_required
def get_competition_detail(comp_id):
    """Retrives information about the competition and the categories in it"""
    json = [Competition.query.filter_by(id=comp_id).first_or_404().to_json()]
    categories = [category.to_json() for category in Category.query.filter_by(comp_id=comp_id).all()]
    json.append(categories)
    return jsonify(json)

@bp.route('/competition/<int:comp_id>/<int:cat_id>', methods=['GET'])
@token_auth.login_required
def get_category_detail(comp_id, cat_id):
    """Retrives information about the category and the reviews in it"""
    json = [Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).first_or_404().to_json()]
    submissions = Submission.query.filter_by(comp_id=comp_id).all()
    cat_submissions = []
    for _, submission in enumerate(submissions):
        for j in range(len(submission.categories)):
            if submission.categories[j].id == cat_id:
                cat_submissions.append(submission.to_json(detail=False))
    json.append(cat_submissions)
    return jsonify(json)

@bp.route('/competition/<int:comp_id>/<int:cat_id>/<int:sub_id>', methods=['GET'])
@token_auth.login_required
def get_submission_detail(comp_id, cat_id, sub_id):
    """Retrives information about the review and category"""
    json = [Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).first_or_404().to_json()]
    submission = Submission.query.filter_by(id=sub_id).filter_by(comp_id=comp_id).first_or_404()
    if not submission.check_category(cat_id):
        return error_response(404, 'submission is not in this category')
    json.append(submission.to_json())
    return jsonify(json)

@bp.route('/competition/<int:comp_id>/<int:cat_id>/<int:sub_id>/uploads', methods=['GET'])
@token_auth.login_required
def get_submission_upload_detail(comp_id, cat_id, sub_id):
    """Retrives information about uploads for this submission"""
    uploads = SubmissionUploads.query.filter_by(submission_id=sub_id).first()
    if uploads is None:
        return jsonify([]) # Returns nothing
    json = [uploads.to_json()]
    submission = Submission.query.filter_by(id=sub_id).filter_by(comp_id=comp_id).first_or_404()
    if not submission.check_category(cat_id):
        return error_response(404, 'submission is not in this category')
    return jsonify(json)
