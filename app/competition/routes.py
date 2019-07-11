"""
Controls which pages load and what is shown on each
"""
from arrow import get as arrowGet
from flask import render_template, flash, redirect, url_for, abort
from flask_login import current_user, login_required
from markdown import markdown
from bleach import clean
from bleach_whitelist import markdown_tags, markdown_attrs
from app import db
from app.models import Competition, Category, Review, User
from app.competition import bp
from app.competition.forms import CompetitionCreateForm, CategoryCreateForm, ReviewCreateForm

@bp.route('/')
@login_required
def index():
    """Makes dynamic page listing all competitions"""
    competitions = [competition.to_json() for competition in Competition.query.all()]
    return render_template('competition/index.html', title="Competitions", competitions=competitions)

@bp.route('/<int:comp_id>')
@login_required
def competition_overview(comp_id):
    """Makes dynamic competition pages"""
    competition = Competition.query.filter_by(id=comp_id).first_or_404()
    categories = [category.to_json() for category in Category.query.filter_by(comp_id=comp_id)]
    return render_template('competition/competition.html', title=competition.name, name=competition.name, body=competition.body, categories=categories, id=comp_id)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def competition_create():
    """Creates competitions"""
    form = CompetitionCreateForm()
    if form.validate_on_submit():
        competition = Competition(name=form.name.data,
                                  body=form.body.data
                                 )
        db.session.add(competition)
        db.session.commit()
        flash('Competition created successfully')
        return redirect(url_for('competition.competition_overview', comp_id=competition.id))
    return render_template('competition/competitionCreate.html', title='Competition Create', form=form)

@bp.route('/<int:comp_id>/<int:cat_id>')
@login_required
def category_overview(comp_id, cat_id):
    """Makes dynamic categories pages"""
    category = Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).first_or_404()
    review = Review.query.filter_by(comp_id=comp_id).all()
    reviews_in_cat = []
    for i in range(len(review)):
        for j in range(len(review[i].categories)):
            if review[i].categories[j].id == cat_id:
                reviews_in_cat.append(review[i].to_json())

    return render_template('competition/category.html', title=category.name, name=category.name, body=category.body, reviews=reviews_in_cat, comp_id=comp_id, cat_id=cat_id)

@bp.route('/<int:comp_id>/create', methods=['GET', 'POST'])
@login_required
def category_create(comp_id):
    """Create categories"""
    form = CategoryCreateForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data,
                            body=form.body.data,
                            comp_id=comp_id
                            )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully')
        return redirect(url_for('competition.category_overview', comp_id=comp_id, cat_id=category.id))
    return render_template('competition/categoryCreate.html', title='Category Create', form=form)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:review_id>')
@login_required
def review_overview(comp_id, cat_id, review_id):
    """Makes dynamic review pages"""
    review = Review.query.filter_by(id=review_id).filter_by(comp_id=comp_id).first_or_404()
    cat_correct = False
    for i in range(len(review.categories)):
        if cat_id == review.categories[i].id:
            cat_correct = True
            break
    if not cat_correct:
        abort(404)
    body = markdown(review.body, output_format="html5")
    body = clean(body, markdown_tags, markdown_attrs)
    user = User.query.filter_by(id=review.user_id).first_or_404()
    timestamp = arrowGet(review.timestamp).humanize()
    return render_template('competition/review.html', title=review.name, name=review.name,
                           body=body, user=user, humanTime=timestamp, machineTime=review.timestamp)

@bp.route('/<int:comp_id>/<int:cat_id>/create', methods=['GET', 'POST'])
@login_required
def review_create(comp_id, cat_id):
    """Create reviews"""
    form = ReviewCreateForm()
    if form.validate_on_submit():
        review = Review(name=form.name.data,
                        body=form.body.data,
                        user_id=int(current_user.id),
                        comp_id=int(comp_id)
                        )
        db.session.add(review)
        category = Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).first_or_404()
        review.categories.append(category)
        db.session.commit()

        flash('Review created successfully')
        return redirect(url_for('competition.review_overview', comp_id=comp_id, cat_id=cat_id, review_id=review.id))
    return render_template('competition/reviewCreate.html', title='Review Create', form=form)
