"""
Controls pages related to submissions
"""
from flask import render_template, flash, redirect, url_for, abort, request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from markdown import markdown
from arrow import get as arrowGet
from bleach import clean
from bleach_whitelist import markdown_tags, markdown_attrs
from app import db, submission_uploads
from app.database.models import Category, Submission, SubmissionUploads, User, Votes
from app.competition import bp
from app.competition.forms import (SubmissionCreateForm, SubmissionEditForm, SubmissionUploadForm,
                                   SubmissionVotingForm)

@bp.route('/<int:comp_id>/<int:cat_id>/')
@login_required
def category_overview(comp_id, cat_id):
    """Makes dynamic categories pages"""
    category = Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).first_or_404()
    submissions = Submission.query.filter_by(comp_id=comp_id).all()
    votes = Votes.query.filter_by(comp_id=comp_id).filter_by(cat_id=cat_id).all()
    votes_count = Votes.query.filter_by(comp_id=comp_id).filter_by(cat_id=cat_id).count()
    admin = User.query.filter_by(username=current_user.username).first().admin
    cat_submissions = []
    for _, submission in enumerate(submissions):
        for j in range(len(submission.categories)):
            if submission.categories[j].id == cat_id:
                cat_submissions.append(submission.to_json())
    scores = []
    for i in range(len(cat_submissions)):
        score = 0
        current_votes = 0
        for j in range(votes_count):
            if votes[j].submission_id == submissions[i].id:
                score = score + votes[j].score
                current_votes = current_votes + 1
        try:
            average = score/current_votes
        except ZeroDivisionError:
            average = 0
        scores.append([average, current_votes])
    return render_template('competition/category.html', title=category.name, name=category.name,
                           body=category.body, submissions=cat_submissions, comp_id=comp_id,
                           cat_id=cat_id, scores=scores, admin=admin)

@bp.route('/<int:comp_id>/<int:cat_id>/create', methods=['GET', 'POST'])
@login_required
def submission_create(comp_id, cat_id):
    """Create submission"""
    form = SubmissionCreateForm()
    if form.validate_on_submit():
        submission = Submission(name=form.name.data,
                                body=form.body.data,
                                user_id=int(current_user.id),
                                comp_id=int(comp_id)
                                )
        db.session.add(submission)
        category = Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).first_or_404()
        submission.categories.append(category)
        db.session.commit()

        flash('Submission created successfully')
        return redirect(url_for('competition.submission_overview',
                                comp_id=comp_id, cat_id=cat_id, submission_id=submission.id))
    return render_template('competition/submissionCreate.html', title='Submission Create', form=form)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:submission_id>/')
@login_required
def submission_overview(comp_id, cat_id, submission_id):
    """Makes dynamic submission pages"""
    submission = Submission.query.filter_by(id=submission_id).filter_by(comp_id=comp_id).first_or_404()
    if not submission.check_category(cat_id):
        abort(404)
    body = markdown(submission.body, output_format="html5")
    body = clean(body, markdown_tags, markdown_attrs)
    user = User.query.filter_by(id=submission.user_id).first_or_404()
    timestamp = arrowGet(submission.timestamp).humanize()
    uploads_count = SubmissionUploads.query.filter_by(submission_id=submission_id).count()
    owner = current_user.id == user.id
    return render_template('competition/submission.html', title=submission.name, submission=submission,
                           body=body, user=user, cat_id=cat_id, humanTime=timestamp,
                           uploadsCount=uploads_count, owner=owner)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:submission_id>/delete', methods=['GET', 'POST'])
@login_required
def submission_delete(comp_id, cat_id, submission_id):
    """Deletes the submission"""
    submission = Submission.query.filter_by(id=submission_id).filter_by(comp_id=comp_id).first_or_404()
    if not submission.check_category(cat_id):
        abort(404)
    if int(current_user.id) != int(submission.user_id):
        abort(403)
    db.session.delete(submission)
    db.session.commit()
    flash('Submission deleted successfully')
    return redirect(url_for('competition.category_overview', comp_id=comp_id, cat_id=cat_id))

@bp.route('/<int:comp_id>/<int:cat_id>/<int:submission_id>/edit', methods=['GET', 'POST'])
@login_required
def submission_edit(comp_id, cat_id, submission_id):
    """Edits the submission"""
    submission = Submission.query.filter_by(id=submission_id).filter_by(comp_id=comp_id).first_or_404()
    form = SubmissionEditForm()
    if not submission.check_category(cat_id):
        abort(404)
    if int(current_user.id) != int(submission.user_id):
        abort(403)
    if request.method == 'GET':
        form.name.data = submission.name
        form.body.data = submission.body
    if form.validate_on_submit():
        submission.name = form.name.data
        submission.body = form.body.data
        db.session.commit()
        flash('Submission edited successfully')
        return redirect(url_for('competition.submission_overview',
                                comp_id=comp_id, cat_id=cat_id, submission_id=submission.id))
    return render_template('competition/submissionEdit.html', title='Submission Edit', form=form,
                           comp_id=comp_id, cat_id=cat_id, submission_id=submission.id)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:submission_id>/files')
@login_required
def submission_files(comp_id, cat_id, submission_id):
    """Shows all attached files"""
    submission = Submission.query.filter_by(id=submission_id).filter_by(comp_id=comp_id).first_or_404()
    if not submission.check_category(cat_id):
        abort(404)
    uploads = SubmissionUploads.query.filter_by(submission_id=submission_id)
    return render_template('competition/submissionFiles.html', title='Attached Files', uploads=uploads,
                           comp_id=comp_id, cat_id=cat_id, submission_id=submission_id)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:submission_id>/upload', methods=['GET', 'POST'])
@login_required
def submission_upload(comp_id, cat_id, submission_id):
    """Allow documents to be uploaded"""
    submission = Submission.query.filter_by(id=submission_id).filter_by(comp_id=comp_id).first_or_404()
    form = SubmissionUploadForm()
    if not submission.check_category(cat_id):
        abort(404)
    if int(current_user.id) != int(submission.user_id):
        abort(403)
    if request.method == 'POST' and 'fileUpload' in request.files:
        if form.validate_on_submit():
            uploads = SubmissionUploads.query.order_by(SubmissionUploads.id.desc()).filter_by(
                submission_id=submission_id).first()
            if uploads is None:
                next_id = 1
            else:
                next_id = uploads.id+1 #ids are per submission
            file_obj = request.files['fileUpload']
            file_name = secure_filename(file_obj.filename)
            uploads = SubmissionUploads(id=next_id,
                                        filename=file_name,
                                        submission_id=int(submission_id))
            db.session.add(uploads)
            db.session.flush() #Needed so uuid generated
            disk_name = str(uploads.uuid)
            submission_uploads.save(file_obj, name=disk_name)
            db.session.commit()
            flash('File Uploaded')
            return redirect(url_for('competition.submission_overview',
                                    comp_id=comp_id, cat_id=cat_id, submission_id=submission.id))
        flash('File failed to upload')
    return render_template('competition/submissionUpload.html', title='Upload Files', form=form)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:submission_id>/vote', methods=['GET', 'POST'])
@login_required
def submission_voting(comp_id, cat_id, submission_id):
    """Allows you to vote"""
    submission = Submission.query.filter_by(id=submission_id).filter_by(comp_id=comp_id).first_or_404()
    category = Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).first_or_404()
    if not submission.check_category(cat_id):
        abort(404)
    if current_user.reviewer == 0:
        abort(403)
    if current_user.id == submission.user_id:
        abort(403)
    form = SubmissionVotingForm()
    if form.validate_on_submit():
        vote = Votes(score=form.score.data,
                     comments=form.comment.data,
                     user_id=int(current_user.id),
                     comp_id=int(comp_id),
                     cat_id=int(cat_id),
                     submission_id=int(submission_id))
        db.session.add(vote)
        db.session.commit()
        flash('Successfully Voted')
        return redirect(url_for('competition.submission_overview',
                                comp_id=comp_id, cat_id=cat_id, submission_id=submission.id))
    return render_template('competition/submissionVoting.html', title='Voting', form=form,
                           cat=category, submission=submission)
