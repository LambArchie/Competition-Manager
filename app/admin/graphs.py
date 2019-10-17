"""
Controls graph pages
"""
from json import dumps
from bleach import clean
from flask import render_template
from flask_login import login_required
from app.database.models import User, Competition, Category, Review
from app.admin import bp
from app.admin.routes import check_permissions

def clean_text(text):
    """Removes all HTML tags"""
    return clean(text, strip=True)

@bp.route('/graphs/')
@login_required
def graphs():
    """Visual representation of reviews, categories, competitions and users"""
    check_permissions()
    users = User.query.all()
    competitions = Competition.query.all()
    categories = Category.query.all()
    reviews = Review.query.all()
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
    for _, review in enumerate(reviews):
        nodes.append(review.name)
        for _, review_cat in enumerate(review.categories):
            edges.append([review_cat.name, review.name])
        temp = User.query.filter_by(id=review.user_id).first().username
        edges.append([review.name, temp])
    combined['nodes'] = nodes
    combined['edges'] = edges
    nodes = clean_text(dumps(combined, ensure_ascii=False))
    return render_template('admin/graphs.html', title="Admin", json=nodes)
