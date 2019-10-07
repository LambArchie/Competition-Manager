"""
Controls pages directly related to categories
"""
from flask import render_template, flash, redirect, url_for, abort
from flask_login import current_user, login_required
from app import db
from app.database.models import Competition, Category, Review
from app.competition import bp
from app.competition.forms import CategoryCreateForm, review_edit_categories_form

@bp.route('/<int:comp_id>')
@login_required
def competition_overview(comp_id):
    """Makes dynamic competition pages"""
    competition = Competition.query.filter_by(id=comp_id).first_or_404()
    categories = [category.to_json() for category in Category.query.filter_by(comp_id=comp_id)]
    return render_template('competition/competition.html', title=competition.name,
                           competition=competition, categories=categories, id=comp_id)

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
        return redirect(url_for('competition.category_overview', comp_id=comp_id,
                                cat_id=category.id))
    return render_template('competition/categoryCreate.html', title='Category Create', form=form)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:review_id>/edit/categories', methods=['GET', 'POST'])
@login_required
def review_edit_category(comp_id, cat_id, review_id):
    """Allows assigning categories"""
    review = Review.query.filter_by(id=review_id).filter_by(comp_id=comp_id).first_or_404()
    categories = Category.query.filter_by(comp_id=comp_id)
    form = review_edit_categories_form(review, categories)
    if not review.check_category(cat_id):
        abort(404)
    if int(current_user.id) != int(review.user_id):
        abort(403)
    if form.validate_on_submit():
        for _, checkbox in enumerate(form):
            try:
                int(checkbox.name)
            except ValueError:
                break
            else:
                if review.check_category(int(checkbox.name)) != checkbox.data:
                    category = (Category.query.filter_by(id=int(checkbox.name)).
                                filter_by(comp_id=comp_id).first_or_404())
                    if checkbox.data:
                        review.categories.append(category)
                    else:
                        review.categories.remove(category)
        db.session.commit()
        flash('Review categories updated successfully')
        return redirect(url_for('competition.competition_overview', comp_id=comp_id))
    return render_template('competition/reviewCategoryEdit.html', title='Edit Category', form=form)
