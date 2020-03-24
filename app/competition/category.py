"""
Controls pages directly related to categories
"""
from sqlalchemy.sql import text
from flask import render_template, flash, redirect, url_for, abort, request
from flask_login import current_user, login_required
from app import db
from app.database.models import Competition, Category, Submission
from app.competition import bp
from app.competition.forms import CategoryForm, submission_edit_categories_form
from app.admin.routes import check_permissions

@bp.route('/<int:comp_id>/')
@login_required
def categories_overview(comp_id):
    """Lists all categories in a competition"""
    competition = db.session.execute("""SELECT name, body FROM competition WHERE id = :comp
                                     LIMIT 1 OFFSET 0""", {'comp': comp_id}).fetchone()
    query = text("SELECT name, body, id, comp_id FROM category WHERE comp_id = :comp_id")
    categories = [category.to_json() for category in db.session.query(Category).from_statement(query).params(comp_id=comp_id).all()]
    return render_template('competition/competition.html', title=competition.name,
                           competition=competition, categories=categories, id=comp_id,
                           admin=current_user.admin)

@bp.route('/<int:comp_id>/create', methods=['GET', 'POST'])
@login_required
def category_create(comp_id):
    """Create categories"""
    check_permissions()
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data,
                            body=form.body.data,
                            comp_id=comp_id
                            )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully')
        return redirect(url_for('competition.submissions_overview', comp_id=comp_id,
                                cat_id=category.id))
    return render_template('competition/categoryCreate.html', title='Create Category', form=form)

@bp.route('/<int:comp_id>/<int:cat_id>/edit', methods=['GET', 'POST'])
@login_required
def category_edit(comp_id, cat_id):
    """Edits a submission"""
    query = text("SELECT id, name, body FROM category WHERE id = :id AND comp_id = :comp_id LIMIT 1 OFFSET 0")
    category = db.session.query(Category).from_statement(query).params(id=cat_id, comp_id=comp_id).first_or_404()
    form = CategoryForm()
    check_permissions()
    if request.method == 'GET':
        form.name.data = category.name
        form.body.data = category.body
    if form.validate_on_submit():
        category.name = form.name.data
        category.body = form.body.data
        db.session.commit()
        flash('Category edited successfully')
        return redirect(url_for('competition.submissions_overview', comp_id=comp_id, cat_id=cat_id))
    return render_template('competition/categoryEdit.html', title='Edit Category', form=form)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:sub_id>/edit/categories', methods=['GET', 'POST'])
@login_required
def submission_edit_category(comp_id, cat_id, sub_id):
    """Allows assigning categories to a submission"""
    query = text("SELECT id, user_id FROM submission WHERE id = :id AND comp_id = :comp_id LIMIT 1 OFFSET 0")
    submission = db.session.query(Submission).from_statement(query).params(id=sub_id, comp_id=comp_id).first_or_404()
    query = text("SELECT id FROM category WHERE comp_id = :comp_id")
    categories = db.session.query(Category).from_statement(query).params(comp_id=comp_id).all()
    form = submission_edit_categories_form(submission, categories)
    if not submission.check_category(cat_id):
        abort(404)
    if int(current_user.id) != int(submission.user_id):
        abort(403)
    if form.validate_on_submit():
        for _, checkbox in enumerate(form):
            try:
                int(checkbox.name)
            except ValueError:
                break
            else:
                if submission.check_category(int(checkbox.name)) != checkbox.data:
                    query = text("SELECT id FROM category WHERE id = :id AND comp_id = :comp_id LIMIT 1 OFFSET 0")
                    category = db.session.query(Category).from_statement(query).params(id=int(checkbox.name), comp_id=comp_id).first_or_404()
                    if checkbox.data:
                        submission.categories.append(category)
                    else:
                        submission.categories.remove(category)
        db.session.commit()
        flash('Submission categories updated successfully')
        return redirect(url_for('competition.categories_overview', comp_id=comp_id))
    return render_template('competition/submissionCategoryEdit.html', title='Edit Category', form=form)
