"""
Controls which pages load and what is shown on each
"""
from os import path, remove
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, send_from_directory, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app import app, db, avatars
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm, UploadAvatarForm
from app.models import User

@app.before_request
def before_request():
    """Code which is run before every request"""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    """Landing page"""
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('users/login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    """Logout page"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if app.config['DISABLE_PUBLIC_REGISTRATION']:
        return render_template('errors/403.html')
    elif current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        form = RegistrationForm()
        del form.admin # Hides option to make user admin
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data, admin=False)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        return render_template('users/register.html', title='Register', form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Profile edit page"""
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('users/edit_profile.html', title='Edit Profile', form=form)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password form"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=current_user.username).first()
        if not user.check_password(form.currentpassword.data):
            flash('Wrong current password')
        elif form.password.data == form.currentpassword.data:
            flash('Same as exsisting password')
        else:
            user.set_password(form.password.data)
            db.session.commit()
            flash('Your password has been changed successfully.')
            return redirect(url_for('user', username=current_user.username))
    return render_template('users/change_password.html', title='Change Password', form=form)

@app.route('/upload_avatar', methods=['GET', 'POST'])
@login_required
def upload_avatar():
    """Controls avatar uploads"""
    form = UploadAvatarForm()
    if request.method == 'POST' and 'avatar' in request.files:
        if form.validate_on_submit():
            user = User.query.filter_by(username=current_user.username).first()
            if (user.avatar != "") and (path.exists(app.config['UPLOADS_DEFAULT_DEST']+"avatars/"+user.avatar)):
                remove(app.config['UPLOADS_DEFAULT_DEST'] + "avatars/" + user.avatar)
                user.avatar_filename("")
            file_obj = request.files['avatar']
            file_extension = (file_obj.filename.split('.')[-1]).lower()
            file_name = secure_filename(current_user.username + '.' + file_extension)
            file_name = avatars.save(file_obj, name=file_name)
            user.avatar_filename(file_name)
            db.session.commit()
            flash('Avatar updated')
            return redirect(url_for('user_profile', username=current_user.username))
        else:
            flash('Avatar not uploaded')
    return render_template('users/upload_avatar.html', title='Upload Avatar', form=form)

@app.route('/user/<username>')
@login_required
def user_profile(username):
    """Makes dynamic user pages"""
    user = User.query.filter_by(username=username).first_or_404()
    reviews = [
        {'author': user, 'body': 'Test reviews #1'},
        {'author': user, 'body': 'Test reviews #2'}
    ]
    return render_template('users/user.html', user=user, reviews=reviews)

@app.route('/avatar/<username>')
def avatar(username):
    """Gets avatar if one is set else uses default"""
    user = User.query.filter_by(username=username).first_or_404()
    if user.avatar == "":
        return redirect("https://www.gravatar.com/avatar?d=identicon&s=128")
    print(app.config['UPLOADS_DEFAULT_DEST'] + user.avatar)
    return send_from_directory(app.config['UPLOADS_DEFAULT_DEST'] + "avatars/", user.avatar)

@app.route('/admin')
@login_required
def admin():
    """Shows default admin page if got permissions"""
    if (current_user.admin is False) or (current_user.admin is None):
        return render_template('errors/403.html')
    else:
        return render_template('admin/admin.html')

@app.route('/admin/register', methods=['GET', 'POST'])
@login_required
def admin_register():
    """Registration page"""
    if (current_user.admin is False) or (current_user.admin is None):
        return render_template('errors/403.html')
    else:
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data, admin=bool(form.admin.data))
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('User registed successfully')
            return redirect(url_for('admin'))
        return render_template('users/register.html', title='Register', form=form)

@app.route('/api/admin/users')
@login_required
def admin_users():
    if (current_user.admin is False) or (current_user.admin is None):
        return render_template('errors/403.html')
    else:
        users = [user.serialize_user() for user in User.query.all()]
        return jsonify(users)