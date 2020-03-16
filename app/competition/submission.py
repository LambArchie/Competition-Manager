"""
Controls pages related to submissions
"""
from datetime import datetime
from flask import render_template, flash, redirect, url_for, abort, request
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from markdown import markdown
from arrow import get as arrowGet
from bleach import clean
from bleach_whitelist import markdown_tags, markdown_attrs
from app import db, submission_uploads
from app.database.models import Competition, Category, Submission, SubmissionUploads, User, Votes
from app.competition import bp
from app.competition.forms import SubmissionForm, SubmissionUploadForm, SubmissionVotingForm

@bp.route('/<int:comp_id>/<int:cat_id>/')
@login_required
def submissions_overview(comp_id, cat_id):
    """Lists all submissions in found in the category and competition"""
    category = Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).first_or_404()
    submissions = Submission.query.filter_by(comp_id=comp_id).order_by(Submission.timestamp.desc()).all()
    comp_name = Competition.query.filter_by(id=comp_id).value('name')
    cat_submissions = []
    for _, submission in enumerate(submissions):
        for j in range(len(submission.categories)):
            if submission.categories[j].id == cat_id:
                json = submission.to_json()
                json['humantime'] = arrowGet(submission.timestamp).humanize()
                cat_submissions.append(json)
    scores = []
    if current_user.admin:
        votes = Votes.query.filter_by(comp_id=comp_id).filter_by(cat_id=cat_id).all()
        votes_count = Votes.query.filter_by(comp_id=comp_id).filter_by(cat_id=cat_id).count()
        for _, sub in enumerate(cat_submissions):
            score = 0
            current_votes = 0
            for j in range(votes_count):
                if votes[j].submission_id == sub.get('id'):
                    score = score + votes[j].score
                    current_votes = current_votes + 1
            try:
                average = score / current_votes
            except ZeroDivisionError:
                average = 0
            scores.append([average, current_votes])
    return render_template('competition/category.html', title=category.name, name=category.name,
                           body=category.body, submissions=cat_submissions, scores=scores,
                           comp_id=comp_id, comp_name=comp_name, cat_id=cat_id,
                           admin=current_user.admin, )

@bp.route('/<int:comp_id>/<int:cat_id>/create', methods=['GET', 'POST'])
@login_required
def submission_create(comp_id, cat_id):
    """Create a submission"""
    form = SubmissionForm()
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
        return redirect(url_for('competition.submission_page',
                                comp_id=comp_id, cat_id=cat_id, sub_id=submission.id))
    return render_template('competition/submissionCreate.html', title='Create Submission', form=form)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:sub_id>/')
@login_required
def submission_page(comp_id, cat_id, sub_id):
    """Retreives data for a specific submission"""
    submission = Submission.query.filter_by(id=sub_id).filter_by(comp_id=comp_id).first_or_404()
    if not submission.check_category(cat_id):
        abort(404)
    body = markdown(submission.body, output_format="html5")
    body = clean(body, markdown_tags, markdown_attrs)
    user = User.query.filter_by(id=submission.user_id).first_or_404()
    timestamp = arrowGet(submission.timestamp).format('D MMMM YYYY')
    uploads_count = SubmissionUploads.query.filter_by(submission_id=sub_id).count()
    owner = current_user.id == user.id
    comp_name = Competition.query.filter_by(id=comp_id).value('name')
    cat_name = Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).value('name')
    return render_template('competition/submission.html', title=submission.name,
                           submission=submission, body=body, user=user, cat_id=cat_id,
                           cat_name=cat_name, comp_name=comp_name, humanTime=timestamp,
                           uploadsCount=uploads_count, owner=owner)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:sub_id>/delete', methods=['GET', 'POST'])
@login_required
def submission_delete(comp_id, cat_id, sub_id):
    """Deletes a submission"""
    submission = Submission.query.filter_by(id=sub_id).filter_by(comp_id=comp_id).first_or_404()
    if not submission.check_category(cat_id):
        abort(404)
    if int(current_user.id) != int(submission.user_id):
        abort(403)
    db.session.delete(submission)
    db.session.commit()
    flash('Submission deleted successfully')
    return redirect(url_for('competition.submissions_overview', comp_id=comp_id, cat_id=cat_id))

@bp.route('/<int:comp_id>/<int:cat_id>/<int:sub_id>/edit', methods=['GET', 'POST'])
@login_required
def submission_edit(comp_id, cat_id, sub_id):
    """Edits a submission"""
    submission = Submission.query.filter_by(id=sub_id).filter_by(comp_id=comp_id).first_or_404()
    form = SubmissionForm()
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
        submission.timestamp = datetime.utcnow()
        db.session.commit()
        flash('Submission edited successfully')
        return redirect(url_for('competition.submission_page',
                                comp_id=comp_id, cat_id=cat_id, sub_id=submission.id))
    return render_template('competition/submissionEdit.html', title='Edit Submission', form=form,
                           comp_id=comp_id, cat_id=cat_id, sub_id=submission.id)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:sub_id>/files')
@login_required
def submission_files(comp_id, cat_id, sub_id):
    """Shows all attached files to the submission"""
    submission = Submission.query.filter_by(id=sub_id).filter_by(comp_id=comp_id).first_or_404()
    if not submission.check_category(cat_id):
        abort(404)
    owner = (submission.user_id == current_user.id)  # Checks if true or not then sets owner
    uploads = SubmissionUploads.query.filter_by(submission_id=sub_id)
    comp_name = Competition.query.filter_by(id=comp_id).value('name')
    cat_name = Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).value('name')
    return render_template('competition/submissionFiles.html', title='Attached Files',
                           uploads=uploads, comp_id=comp_id, cat_id=cat_id, sub_id=sub_id, owner=owner,
                           sub_name=submission.name, cat_name=cat_name, comp_name=comp_name)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:sub_id>/upload', methods=['GET', 'POST'])
@login_required
def submission_upload(comp_id, cat_id, sub_id):
    """Allow documents to be attached to the submission"""
    submission = Submission.query.filter_by(id=sub_id).filter_by(comp_id=comp_id).first_or_404()
    form = SubmissionUploadForm()
    if not submission.check_category(cat_id):
        abort(404)
    if int(current_user.id) != int(submission.user_id):
        abort(403)
    if request.method == 'POST' and 'fileUpload' in request.files:
        if form.validate_on_submit():
            uploads = SubmissionUploads.query.order_by(SubmissionUploads.id.desc()).filter_by(
                submission_id=sub_id).first()
            if uploads is None:
                next_id = 1
            else:
                next_id = uploads.id + 1  # id's are per submission
            file_obj = request.files['fileUpload']
            file_name = secure_filename(file_obj.filename)
            uploads = SubmissionUploads(id=next_id,
                                        filename=file_name,
                                        submission_id=int(sub_id))
            db.session.add(uploads)
            db.session.flush()  # Needed so uuid generated
            disk_name = str(uploads.uuid)
            # File extension has to be appended to pass checks
            submission_uploads.save(file_obj, name=disk_name + '.')
            db.session.commit()
            flash('File Uploaded')
            return redirect(url_for('competition.submission_page',
                                    comp_id=comp_id, cat_id=cat_id, sub_id=submission.id))
        flash('File failed to upload', 'error')
    return render_template('competition/submissionUpload.html', title='Upload Files', form=form)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:sub_id>/vote', methods=['GET', 'POST'])
@login_required
def submission_voting(comp_id, cat_id, sub_id):
    """Allows reviews to vote on a submission for that category"""
    submission = Submission.query.filter_by(id=sub_id).filter_by(comp_id=comp_id).first_or_404()
    category = Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).first_or_404()
    if not submission.check_category(cat_id):
        abort(404)
    if current_user.reviewer == 0:
        abort(403)
    if current_user.id == submission.user_id:
        abort(403)
    form = SubmissionVotingForm()
    previous_vote = Votes.query.filter_by(user_id=current_user.id).filter_by(submission_id=sub_id).filter_by(
        comp_id=comp_id).filter_by(cat_id=cat_id).first()
    if form.validate_on_submit():
        if previous_vote is None:
            vote = Votes(score=form.score.data,
                         comments=form.comment.data,
                         user_id=int(current_user.id),
                         comp_id=int(comp_id),
                         cat_id=int(cat_id),
                         submission_id=int(sub_id))
            db.session.add(vote)
        else:
            previous_vote.score = form.score.data
            previous_vote.comments = form.comment.data
        db.session.commit()
        flash('Successfully Voted')
        return redirect(url_for('competition.submission_page',
                                comp_id=comp_id, cat_id=cat_id, sub_id=submission.id))
    elif previous_vote is not None:
        form.score.data = previous_vote.score
        form.comment.data = previous_vote.comments
    return render_template('competition/submissionVoting.html', title='Voting', form=form,
                           cat=category, submission=submission)

@bp.route('/<int:comp_id>/<int:cat_id>/<int:sub_id>/votes_overview', methods=['GET', 'POST'])
@login_required
def submission_vote_overviewer(comp_id, cat_id, sub_id):
    """Lists how every reviewer has voted"""
    if current_user.admin:
        submission = Submission.query.filter_by(id=sub_id).filter_by(comp_id=comp_id).first_or_404()
        if not submission.check_category(cat_id):
            abort(404)
        votes = Votes.query.filter_by(comp_id=comp_id, cat_id=cat_id, submission_id=sub_id).all()
        for i in range(len(votes)):
            votes[i].reviewer_name = User.query.filter_by(id=votes[i].user_id).value('name')
            votes[i].username = User.query.filter_by(id=votes[i].user_id).value('username')
        comp_name = Competition.query.filter_by(id=comp_id).value('name')
        cat_name = Category.query.filter_by(id=cat_id).filter_by(comp_id=comp_id).value('name')
        return render_template('competition/submissionVotesOverview.html', title='Vote Overview',
                               votes=votes, comp_id=comp_id, cat_id=cat_id, sub_id=sub_id,
                               sub_name=submission.name, cat_name=cat_name, comp_name=comp_name)
    abort(403)
