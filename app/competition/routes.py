"""
Controls which pages load and what is shown on each
"""
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import app, db, avatars
from app.models import User, Competition, Category, Review
from app.competition import bp
from app.competition.forms import CompetitionCreateForm, CategoryCreateForm, ReviewCreateForm

@bp.route('/')
@login_required
def competitionBase():
    return render_template('competition/index.html', title="Competitions")

@bp.route('/<compId>')
@login_required
def compId(compId):
    """Makes dynamic competition pages"""
    competition = Competition.query.filter_by(id=compId).first_or_404()
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

@bp.route('/<compId>/<catId>')
@login_required
def catId(compId, catId):
    """Makes dynamic categories pages"""
    category = Category.query.filter_by(id=catId).filter_by(comp_id=compId).first_or_404()
    return render_template('competition/category.html', title=category.name, name=category.name, body=category.body)

@bp.route('/<compId>/create', methods=['GET', 'POST'])
@login_required
def categoryCreate(compId):
    """Create categories"""
    form = CategoryCreateForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data,
                    body=form.body.data,
                    comp_id=compId
                    )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully')
        return redirect(url_for('index'))
    return render_template('competition/categoryCreate.html', title='Category Create', form=form)

@bp.route('/<compId>/<catId>/<reviewId>')
@login_required
def reviewId(compId, catId, reviewId):
    """Makes dynamic review pages"""
    review = Review.query.filter_by(id=reviewId).filter_by(comp_id=compId).first_or_404()
    return render_template('competition/review.html', title=review.name, name=review.name, body=review.body, user=review.user_id)

@bp.route('/<compId>/<catId>/create', methods=['GET', 'POST'])
@login_required
def reviewCreate(compId, catId):
    """Create reviews"""
    form = ReviewCreateForm()
    if form.validate_on_submit():
        review = Review(name=form.name.data,
                        body=form.body.data,
                        user_id=int(current_user.id),
                        comp_id=int(compId)
                        )
        db.session.add(review)
        category = Category.query.filter_by(id=catId).filter_by(comp_id=compId).first_or_404()
        review.categories.append(category)
        db.session.commit()

        flash('Review created successfully')
        return redirect(url_for('index'))
    return render_template('competition/reviewCreate.html', title='Review Create', form=form)
