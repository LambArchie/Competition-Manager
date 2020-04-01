"""
Competition API Routes
"""
from sqlalchemy.sql import text
from flask import jsonify
from app import db
from app.api_v1 import bp
from app.api_v1.auth import token_auth
from app.api_v1.errors import error_response
from app.database.models import Competition, Category, Submission, SubmissionUploads

@bp.route('/competition', methods=['GET'])
@token_auth.login_required
def get_competitions():
    """Returns all competitions running and their id"""
    query = text("SELECT * FROM competition")
    competitions = [competition.to_json() for competition in db.session.query(Competition).from_statement(query).all()]
    return jsonify(competitions)

@bp.route('/competition/<int:comp_id>', methods=['GET'])
@token_auth.login_required
def get_competition_detail(comp_id):
    """Retrives information about the competition and the categories in it"""
    query = text("SELECT * FROM competition WHERE id = :id LIMIT 1 OFFSET 0")
    json = [db.session.query(Competition).from_statement(query).params(id=comp_id).first_or_404().to_json()]
    query = text("SELECT * FROM category WHERE comp_id = :comp_id")
    categories = [category.to_json() for category in db.session.query(Category).from_statement(query).params(comp_id=comp_id).all()]
    json.append(categories)
    return jsonify(json)

@bp.route('/competition/<int:comp_id>/<int:cat_id>', methods=['GET'])
@token_auth.login_required
def get_category_detail(comp_id, cat_id):
    """Retrives information about the category and the reviews in it"""
    query = text("SELECT * FROM category WHERE id = :id AND comp_id = :comp_id LIMIT 1 OFFSET 0")
    json = [db.session.query(Category).from_statement(query).params(id=cat_id, comp_id=comp_id).first_or_404().to_json()]
    query = text("SELECT * FROM submission WHERE comp_id = :comp_id")
    submissions = db.session.query(Submission).from_statement(query).params(comp_id=comp_id).all()
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
    query = text("SELECT * FROM submission WHERE id = :id AND comp_id = :comp_id LIMIT 1 OFFSET 0")
    submission = db.session.query(Submission).from_statement(query).params(id=sub_id, comp_id=comp_id).first_or_404()
    if not submission.check_category(cat_id):
        return error_response(404, 'submission is not in this category')
    query = text("SELECT * FROM category WHERE id = :id AND comp_id = :comp_id LIMIT 1 OFFSET 0")
    json = [db.session.query(Category).from_statement(query).params(id=comp_id, comp_id=comp_id).first_or_404().to_json()]
    json.append(submission.to_json())
    return jsonify(json)

@bp.route('/competition/<int:comp_id>/<int:cat_id>/<int:sub_id>/uploads', methods=['GET'])
@token_auth.login_required
def get_submission_upload_detail(comp_id, cat_id, sub_id):
    """Retrives information about uploads for this submission"""
    query = text("SELECT id FROM submission WHERE id = :id AND comp_id = :comp_id LIMIT 1 OFFSET 0")
    submission = db.session.query(Submission).from_statement(query).params(id=sub_id, comp_id=comp_id).first_or_404()
    if not submission.check_category(cat_id):
        return error_response(404, 'submission is not in this category')
    uploads = SubmissionUploads.query.filter_by(submission_id=sub_id).all()
    json = []
    for _, upload in enumerate(uploads):
        json.append(upload.to_json())
    return jsonify(json)
