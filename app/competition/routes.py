"""
Controls which pages load and what is shown on each
"""
from arrow import get as arrowGet
from flask import render_template, flash, redirect, url_for, abort, request, current_app, send_from_directory, make_response
from flask_login import current_user, login_required
from markdown import markdown
from bleach import clean
from bleach_whitelist import markdown_tags, markdown_attrs
from werkzeug.utils import secure_filename
from app import db, review_uploads
from app.database.models import Competition, Category, Review, ReviewUploads, User
from app.competition import bp
from app.competition.forms import CompetitionCreateForm, CategoryCreateForm, ReviewCreateForm, ReviewEditForm, ReviewUploadForm

@bp.route('/')
@login_required
def index():
    """Makes dynamic page listing all competitions"""
    comps = [competition.to_json() for competition in Competition.query.all()]
    return render_template('competition/index.html', title="Competitions", competitions=comps)

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

@bp.route('/file/<uuid>/<filename>')
@login_required
def file_download(uuid, filename):
    """Sends file"""
    if not secure_filename(uuid) == uuid:
        abort(404)
    uploads = ReviewUploads.query.filter_by(uuid=uuid).first_or_404()
    if not filename == uploads.filename:
        abort(404)
    r = make_response(send_from_directory(current_app.config['UPLOADS_DEFAULT_DEST'] + "reviews/", uuid))
    r.headers['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)
    return r

@bp.route('/<int:comp_id>')
@login_required
def competition_overview(comp_id):
    """Makes dynamic competition pages"""
    competition = Competition.query.filter_by(id=comp_id).first_or_404()
    categories = [category.to_json() for category in Category.query.filter_by(comp_id=comp_id)]
    return render_template('competition/competition.html', title=competition.name, name=competition.name,
                           body=competition.body, categories=categories, id=comp_id)

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
    uploadsCount = ReviewUploads.query.filter_by(review_id=review_id).count()
    return render_template('competition/review.html', title=review.name, review=review,
                           body=body, user=user, cat_id=cat_id, humanTime=timestamp, uploadsCount=uploadsCount)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:review_id>/delete', methods=['GET', 'POST'])
@login_required
def review_delete(comp_id, cat_id, review_id):
    """Deletes the review"""
    review = Review.query.filter_by(id=review_id).filter_by(comp_id=comp_id).first_or_404()
    if not review.check_category(cat_id):
        abort(404)
    if User.query.filter_by(id=review.user_id).first() is None:
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
    if User.query.filter_by(id=review.user_id).first() is None:
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
    return render_template('competition/reviewEdit.html', title='Review Edit', form=form)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:review_id>/upload', methods=['GET', 'POST'])
@login_required
def review_upload(comp_id, cat_id, review_id):
    """Allow documents to be uploaded"""
    review = Review.query.filter_by(id=review_id).filter_by(comp_id=comp_id).first_or_404()
    form = ReviewUploadForm()
    if not review.check_category(cat_id):
        abort(404)
    if User.query.filter_by(id=review.user_id).first() is None:
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

@bp.route('/<int:comp_id>/<int:cat_id>/<int:review_id>/files')
@login_required
def review_files(comp_id, cat_id, review_id):
    """Shows all attached files"""
    review = Review.query.filter_by(id=review_id).filter_by(comp_id=comp_id).first_or_404()
    if not review.check_category(cat_id):
        abort(404)
    if User.query.filter_by(id=review.user_id).first() is None:
        abort(403)
    uploads = ReviewUploads.query.filter_by(review_id=review_id)
    return render_template('competition/reviewFiles.html', title='Attached Files', uploads=uploads, comp_id=comp_id, cat_id=cat_id, review_id=review_id)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:review_id>/files/<int:file_id>')
@login_required
def review_download_redirect(comp_id, cat_id, review_id, file_id):
    """Redirects you to the download url"""
    review = Review.query.filter_by(id=review_id).filter_by(comp_id=comp_id).first_or_404()
    if not review.check_category(cat_id):
        abort(404)
    if User.query.filter_by(id=review.user_id).first() is None:
        abort(403)
    uploads = ReviewUploads.query.filter_by(review_id=review_id).filter_by(id=file_id).first_or_404()
    return redirect(url_for('competition.file_download', uuid=str(uploads.uuid), filename=uploads.filename))
