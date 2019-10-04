"""
Controls pages related to reviews
"""
from arrow import get as arrowGet
from flask import render_template, flash, redirect, url_for, abort, request
from flask_login import current_user, login_required
from markdown import markdown
from bleach import clean
from bleach_whitelist import markdown_tags, markdown_attrs
from werkzeug.utils import secure_filename
from app import db, review_uploads
from app.database.models import Category, Review, ReviewUploads, User, Votes
from app.competition import bp
from app.competition.forms import (ReviewCreateForm, ReviewEditForm, ReviewUploadForm,
                                   ReviewVotingForm)

@bp.route('/<int:comp_id>/<int:cat_id>')
@login_required
def category_overview(comp_id, cat_id):
    """Makes dynamic categories pages"""
    category = Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).first_or_404()
    reviews = Review.query.filter_by(comp_id=comp_id).all()
    cat_reviews = []
    for _, review in enumerate(reviews):
        for j in range(len(review.categories)):
            if review.categories[j].id == cat_id:
                cat_reviews.append(review.to_json())

    return render_template('competition/category.html', title=category.name, name=category.name,
                           body=category.body, reviews=cat_reviews, comp_id=comp_id, cat_id=cat_id)

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
        return redirect(url_for('competition.review_overview',
                                comp_id=comp_id, cat_id=cat_id, review_id=review.id))
    return render_template('competition/reviewCreate.html', title='Review Create', form=form)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:review_id>')
@login_required
def review_overview(comp_id, cat_id, review_id):
    """Makes dynamic review pages"""
    review = Review.query.filter_by(id=review_id).filter_by(comp_id=comp_id).first_or_404()
    if not review.check_category(cat_id):
        abort(404)
    body = markdown(review.body, output_format="html5")
    body = clean(body, markdown_tags, markdown_attrs)
    user = User.query.filter_by(id=review.user_id).first_or_404()
    timestamp = arrowGet(review.timestamp).humanize()
    uploads_count = ReviewUploads.query.filter_by(review_id=review_id).count()
    owner = current_user.id == user.id
    return render_template('competition/review.html', title=review.name, review=review,
                           body=body, user=user, cat_id=cat_id, humanTime=timestamp,
                           uploadsCount=uploads_count, owner=owner)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:review_id>/delete', methods=['GET', 'POST'])
@login_required
def review_delete(comp_id, cat_id, review_id):
    """Deletes the review"""
    review = Review.query.filter_by(id=review_id).filter_by(comp_id=comp_id).first_or_404()
    if not review.check_category(cat_id):
        abort(404)
    if int(current_user.id) != int(review.user_id):
        abort(403)
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted successfully')
    return redirect(url_for('competition.category_overview', comp_id=comp_id, cat_id=cat_id))

@bp.route('/<int:comp_id>/<int:cat_id>/<int:review_id>/edit', methods=['GET', 'POST'])
@login_required
def review_edit(comp_id, cat_id, review_id):
    """Edits the review"""
    review = Review.query.filter_by(id=review_id).filter_by(comp_id=comp_id).first_or_404()
    form = ReviewEditForm()
    if not review.check_category(cat_id):
        abort(404)
    if int(current_user.id) != int(review.user_id):
        abort(403)
    if request.method == 'GET':
        form.name.data = review.name
        form.body.data = review.body
    if form.validate_on_submit():
        review.name = form.name.data
        review.body = form.body.data
        db.session.commit()
        flash('Review edited successfully')
        return redirect(url_for('competition.review_overview',
                                comp_id=comp_id, cat_id=cat_id, review_id=review.id))
    return render_template('competition/reviewEdit.html', title='Review Edit', form=form,
                           comp_id=comp_id, cat_id=cat_id, review_id=review.id)


@bp.route('/<int:comp_id>/<int:cat_id>/<int:review_id>/files')
@login_required
def review_files(comp_id, cat_id, review_id):
    """Shows all attached files"""
    review = Review.query.filter_by(id=review_id).filter_by(comp_id=comp_id).first_or_404()
    if not review.check_category(cat_id):
        abort(404)
    uploads = ReviewUploads.query.filter_by(review_id=review_id)
    return render_template('competition/reviewFiles.html', title='Attached Files', uploads=uploads, comp_id=comp_id, cat_id=cat_id, review_id=review_id)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:review_id>/upload', methods=['GET', 'POST'])
@login_required
def review_upload(comp_id, cat_id, review_id):
    """Allow documents to be uploaded"""
    review = Review.query.filter_by(id=review_id).filter_by(comp_id=comp_id).first_or_404()
    form = ReviewUploadForm()
    if not review.check_category(cat_id):
        abort(404)
    if int(current_user.id) != int(review.user_id):
        abort(403)
    if request.method == 'POST' and 'fileUpload' in request.files:
        if form.validate_on_submit():
            uploads = ReviewUploads.query.order_by(ReviewUploads.id.desc()).filter_by(review_id=review_id).first()
            if uploads is None:
                next_id = 1
            else:
                next_id = uploads.id+1 #ids are per review
            file_obj = request.files['fileUpload']
            file_name = secure_filename(file_obj.filename)
            uploads = ReviewUploads(id=next_id,
                                    filename=file_name,
                                    review_id=int(review_id))
            db.session.add(uploads)
            db.session.flush() #Needed so uuid generated
            disk_name = str(uploads.uuid)
            review_uploads.save(file_obj, name=disk_name)
            db.session.commit()
            flash('File Uploaded')
            return redirect(url_for('competition.review_overview',
                                    comp_id=comp_id, cat_id=cat_id, review_id=review.id))
        flash('File failed to upload')
    return render_template('competition/reviewUpload.html', title='Upload Files', form=form)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:review_id>/voting', methods=['GET', 'POST'])
@login_required
def review_voting(comp_id, cat_id, review_id):
    """Allows you to vote"""
    review = Review.query.filter_by(id=review_id).filter_by(comp_id=comp_id).first_or_404()
    if not review.check_category(cat_id):
        abort(404)
    if current_user.reviewer == 0:
        abort(403)
    form = ReviewVotingForm()
    if form.validate_on_submit():
        vote = Votes(score=form.score.data,
                     comments=form.comment.data,
                     user_id=int(current_user.id),
                     comp_id=int(comp_id),
                     cat_id=int(cat_id),
                     review_id=int(review_id))
        db.session.add(vote)
        db.session.commit()
        flash('Successfully Voted')
        return redirect(url_for('competition.review_overview',
                                comp_id=comp_id, cat_id=cat_id, review_id=review.id))
    return render_template('competition/reviewVoting.html', title='Voting', form=form)
