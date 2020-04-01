"""
Controls graph pages
"""
from sqlalchemy.sql import text
from flask import render_template, jsonify
from flask_login import login_required
from app import db
from app.database.models import User, Competition, Category, Submission
from app.admin import bp
from app.admin.routes import check_permissions

@bp.route('/graphs/')
@login_required
def graphs():
    """Overview page for graphs"""
    check_permissions()
    return render_template('admin/graphs.html', title="Graphs")

@bp.route('/graphs/nousers')
@login_required
def graphs_nousers():
    """Visual representation of submissions, categories and competitions"""
    check_permissions()
    return render_template('admin/graph.html', title="Graph without Users")

@bp.route('/graphs/users')
@login_required
def graphs_users():
    """Visual representation of submissions, categories, competitions and users"""
    check_permissions()
    return render_template('admin/graph.html', title="Graph with Users")

@bp.route('/graphs/nousers/json')
@login_required
def json_nousers():
    """Gives JSON of submissions, categories and competitions with links"""
    check_permissions()
    competitions = db.session.query(Competition).from_statement(text("SELECT id, name FROM competition")).all()
    categories = db.session.query(Category).from_statement(text("SELECT id, name, comp_id FROM category")).all()
    submissions = db.session.query(Submission).from_statement(text("SELECT id, name FROM submission")).all()
    nodes = []
    edges = []
    combined = {}
    for _, competition in enumerate(competitions):
        nodes.append(competition.name)
    for _, category in enumerate(categories):
        nodes.append(category.name)
        temp = db.session.query(Competition).from_statement(text("SELECT id, name FROM competition WHERE id = :id LIMIT 1 OFFSET 0")).params(id=category.comp_id).first().name
        edges.append([temp, category.name])
    for _, submission in enumerate(submissions):
        nodes.append(submission.name)
        for _, submission_cat in enumerate(submission.categories):
            edges.append([submission_cat.name, submission.name])
    combined['nodes'] = nodes
    combined['edges'] = edges
    return jsonify(combined)

@bp.route('/graphs/users/json')
@login_required
def json_users():
    """Gives JSON of submissions, categories, competitions and users with links"""
    check_permissions()
    users = db.session.query(User).from_statement(text("SELECT id, username FROM user")).all()
    competitions = db.session.query(Competition).from_statement(text("SELECT id, name FROM competition")).all()
    categories = db.session.query(Category).from_statement(text("SELECT id, name, comp_id FROM category")).all()
    submissions = db.session.query(Submission).from_statement(text("SELECT id, name, user_id FROM submission")).all()
    nodes = []
    edges = []
    combined = {}
    for _, user in enumerate(users):
        nodes.append(user.username)
    for _, competition in enumerate(competitions):
        nodes.append(competition.name)
    for _, category in enumerate(categories):
        nodes.append(category.name)
        temp = db.session.query(Competition).from_statement(text("SELECT id, name FROM competition WHERE id = :id LIMIT 1 OFFSET 0")).params(id=category.comp_id).first().name
        edges.append([temp, category.name])
    for _, submission in enumerate(submissions):
        nodes.append(submission.name)
        for _, submission_cat in enumerate(submission.categories):
            edges.append([submission_cat.name, submission.name])
        temp = db.session.query(User).from_statement(text("SELECT id, username FROM user WHERE id = :id")).params(id=submission.user_id).first().username
        edges.append([submission.name, temp])
    combined['nodes'] = nodes
    combined['edges'] = edges
    return jsonify(combined)
