"""
Controls which pages load and what is shown on each
"""
from os import path, remove
from flask import render_template, flash, redirect, url_for, request, send_from_directory, current_app, abort
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import db, avatar_uploads
from app.database.models import User
from app.user import bp
from app.user.forms import EditProfileForm, UploadAvatarForm

@bp.route('/<username>')
@login_required
def user_profile(username):
    """Makes dynamic user pages"""
    user = User.query.filter_by(username=username).first_or_404()
    reviews = [
        {'author': user, 'body': 'Test reviews #1'},
        {'author': user, 'body': 'Test reviews #2'}
    ]
    return render_template('users/user.html', title=user.username, user=user, reviews=reviews)

@bp.route('/<username>/avatar')
def avatar(username):
    """Gets avatar if one is set else uses default"""
    user = User.query.filter_by(username=username).first_or_404()
    if user.avatar == "":
        return redirect("https://www.gravatar.com/avatar?d=identicon&s=128")
    return send_from_directory(
        current_app.config['UPLOADS_DEFAULT_DEST'] + "avatars/", user.avatar)

@bp.route('/<username>/upload_avatar', methods=['GET', 'POST'])
@login_required
def upload_avatar(username):
    """Controls avatar uploads"""
    if username == current_user.username:
        form = UploadAvatarForm()
        if request.method == 'POST' and 'avatar' in request.files:
            if form.validate_on_submit():
                user = User.query.filter_by(username=current_user.username).first()
                if (user.avatar != "") and (path.exists(
                        current_app.config['UPLOADS_DEFAULT_DEST']+"avatars/"+user.avatar)):
                    remove(current_app.config['UPLOADS_DEFAULT_DEST'] + "avatars/" + user.avatar)
                    user.avatar_filename("")
                file_obj = request.files['avatar']
                file_extension = (file_obj.filename.split('.')[-1]).lower()
                file_name = secure_filename(current_user.username + '.' + file_extension)
                file_name = avatar_uploads.save(file_obj, name=file_name)
                user.avatar_filename(file_name)
                db.session.commit()
                flash('Avatar updated')
                return redirect(url_for('user.user_profile', username=current_user.username))
            flash('Avatar not uploaded')
        return render_template('users/upload_avatar.html', title='Upload Avatar', form=form)
    abort(403)

@bp.route('/<username>/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    """Profile edit page"""
    if username == current_user.username:
        form = EditProfileForm(current_user.username, current_user.email)
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('user.edit_profile', username=current_user.username))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
        return render_template('users/edit_profile.html', title='Edit Profile', form=form)
    abort(403)
