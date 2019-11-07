"""
Controls graph pages
"""
from flask import render_template
from flask_login import login_required
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
    competitions = Competition.query.all()
    categories = Category.query.all()
    submissions = Submission.query.all()
    nodes = []
    edges = []
    combined = {}
    for _, competition in enumerate(competitions):
        nodes.append(competition.name)
    for _, category in enumerate(categories):
        nodes.append(category.name)
        temp = Competition.query.filter_by(id=category.comp_id).first().name
        edges.append([temp, category.name])
    for _, submission in enumerate(submissions):
        nodes.append(submission.name)
        for _, submission_cat in enumerate(submission.categories):
            edges.append([submission_cat.name, submission.name])
    combined['nodes'] = nodes
    combined['edges'] = edges
    return render_template('admin/graph.html', title="Graph without Users", json=combined)

@bp.route('/graphs/users')
@login_required
def graphs_users():
    """Visual representation of submissions, categories, competitions and users"""
    check_permissions()
    users = User.query.all()
    competitions = Competition.query.all()
    categories = Category.query.all()
    submissions = Submission.query.all()
    nodes = []
    edges = []
    combined = {}
    for _, user in enumerate(users):
        nodes.append(user.username)
    for _, competition in enumerate(competitions):
        nodes.append(competition.name)
    for _, category in enumerate(categories):
        nodes.append(category.name)
        temp = Competition.query.filter_by(id=category.comp_id).first().name
        edges.append([temp, category.name])
    for _, submission in enumerate(submissions):
        nodes.append(submission.name)
        for _, submission_cat in enumerate(submission.categories):
            edges.append([submission_cat.name, submission.name])
        temp = User.query.filter_by(id=submission.user_id).first().username
        edges.append([submission.name, temp])
    combined['nodes'] = nodes
    combined['edges'] = edges
    return render_template('admin/graph.html', title="Graph with Users", json=combined)
