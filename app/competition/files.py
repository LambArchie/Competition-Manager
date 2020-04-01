"""
Controls files/attachments
"""
from sqlalchemy.sql import text
from flask import redirect, url_for, abort, current_app, send_from_directory, make_response
from flask_login import login_required
from werkzeug.utils import secure_filename
from app import db
from app.database.models import Submission, SubmissionUploads
from app.competition import bp

@bp.route('/file/<uuid>/<filename>')
@login_required
def file_download(uuid, filename):
    """Sends file"""
    if not secure_filename(uuid) == uuid:
        abort(404)
    uploads = SubmissionUploads.query.filter_by(uuid=uuid).first_or_404()
    if not filename == uploads.filename:
        abort(404)
    extension = uploads.filename.split('.')[-1]
    if not secure_filename(extension) == extension:
        abort(404)
    response = make_response(send_from_directory(
        current_app.config['UPLOADS_DEFAULT_DEST'] + "submissions/", uuid + "." + extension))
    response.headers['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)
    return response

@bp.route('/<int:comp_id>/<int:cat_id>/<int:sub_id>/files/<int:file_id>')
@login_required
def submission_download_redirect(comp_id, cat_id, sub_id, file_id):
    """Redirects you to the download url"""
    query = text("SELECT id FROM submission WHERE id = :id AND comp_id = :comp_id LIMIT 1 OFFSET 0")
    submission = db.session.query(Submission).from_statement(query).params(id=sub_id, comp_id=comp_id).first_or_404()
    if not submission.check_category(cat_id):
        abort(404)
    uploads = SubmissionUploads.query.filter_by(submission_id=sub_id).filter_by(
        id=file_id).first_or_404()
    return redirect(url_for('competition.file_download', uuid=str(uploads.uuid),
                            filename=uploads.filename))
