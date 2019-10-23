"""
Controls forms for user control
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email
from app.database.models import User
from app import avatar_uploads

class EditProfileForm(FlaskForm):
    """Allows profile editing"""
    name = StringField('Name', validators=[DataRequired()])
    organisation = StringField('Organisation', validators=[DataRequired(
        message="If not appliable use N/A")], description="If not appliable use N/A")
    username = StringField('Username')
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Edit Profile')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        """Checks if username is already used unless its current username"""
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """Checks if email is already used unless its current email"""
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')

class UploadAvatarForm(FlaskForm):
    """Upload an Avatar"""
    avatar = FileField('Avatar', validators=[FileRequired(), FileAllowed(avatar_uploads, 'Images only!')])
    submit = SubmitField('Upload Avatar')
