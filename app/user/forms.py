"""
Controls forms for user control
"""
from sqlalchemy.sql import text
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Email
from app import db, avatar_uploads
from app.database.models import User

class DeleteUserForm(FlaskForm):
    """Deletes the user"""
    password = StringField('Your Password', validators=[DataRequired()])
    check = StringField('To verify, type "delete my account" below', validators=[DataRequired()])
    submit = SubmitField('Delete Account')

    def validate_password(self, password):
        """Checks if the password entered is correct"""
        if not current_user.check_password(password.data):
            raise ValidationError('Incorrect Password')

    def validate_check(self, check):
        """Checks if """
        if check.data != "delete my account":
            raise ValidationError("Not typed correctly")

class EditProfileForm(FlaskForm):
    """Allows profile editing"""
    name = StringField('Name', validators=[DataRequired()])
    organisation = StringField('Organisation', validators=[DataRequired(
        message="If not appliable use N/A")], description="If not appliable use N/A")
    username = StringField('Username')
    email = StringField('Email', validators=[DataRequired(), Email()])
    admin = BooleanField("Is Admin?")
    reviewer = BooleanField("Is Reviewer?")
    submit = SubmitField('Edit Profile')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        """Checks if username is already used unless its current username"""
        if username.data != self.original_username:
            query = text("SELECT id, username FROM user WHERE username = :username LIMIT 1 OFFSET 0")
            user = db.session.query(User).from_statement(query).params(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """Checks if email is already used unless its current email"""
        if email.data != self.original_email:
            query = text("SELECT id, email FROM user WHERE email = :email LIMIT 1 OFFSET 0")
            user = db.session.query(User).from_statement(query).params(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')

class UploadAvatarForm(FlaskForm):
    """Upload an Avatar"""
    avatar = FileField('Avatar', validators=[FileRequired(), FileAllowed(avatar_uploads, 'Images only!')])
    submit = SubmitField('Upload Avatar')
