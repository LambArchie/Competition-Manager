"""
Controls which pages load and what is shown on each
"""
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db
from app.models import Competition, Category, Review
from app.competition import bp
from app.competition.forms import CompetitionCreateForm, CategoryCreateForm, ReviewCreateForm

@bp.route('/')
@login_required
def competitionBase():
    """Makes dynamic page listing all competitions"""
    return render_template('competition/index.html', title="Competitions")

@bp.route('/<comp_id>')
@login_required
def compId(comp_id):
    """Makes dynamic competition pages"""
    competition = Competition.query.filter_by(id=comp_id).first_or_404()
    return render_template('competition/competition.html', title=competition.name, name=competition.name, body=competition.body)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def competitionCreate():
    """Creates competitions"""
    form = CompetitionCreateForm()
    if form.validate_on_submit():
        competition = Competition(name=form.name.data,
                                  body=form.body.data
                                 )
        db.session.add(competition)
        db.session.commit()
        flash('Competition created successfully')
        return redirect(url_for('index'))
    return render_template('competition/competitionCreate.html', title='Competition Create', form=form)

@bp.route('/<comp_id>/<cat_id>')
@login_required
def catId(comp_id, cat_id):
    """Makes dynamic categories pages"""
    category = Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).first_or_404()
    return render_template('competition/category.html', title=category.name, name=category.name, body=category.body)

@bp.route('/<comp_id>/create', methods=['GET', 'POST'])
@login_required
def categoryCreate(comp_id):
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
        return redirect(url_for('index'))
    return render_template('competition/categoryCreate.html', title='Category Create', form=form)

@bp.route('/<comp_id>/<cat_id>/<review_id>')
@login_required
def reviewId(comp_id, cat_id, review_id):
    """Makes dynamic review pages"""
    review = Review.query.filter_by(id=review_id).filter_by(comp_id=comp_id).first_or_404()
    return render_template('competition/review.html', title=review.name, name=review.name, body=review.body, user=review.user_id)

@bp.route('/<comp_id>/<cat_id>/create', methods=['GET', 'POST'])
@login_required
def reviewCreate(comp_id, cat_id):
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
        return redirect(url_for('index'))
    return render_template('competition/reviewCreate.html', title='Review Create', form=form)
