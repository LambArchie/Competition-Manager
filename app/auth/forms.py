"""
Controls forms for auth
"""
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.database.models import User
from app.auth.passwords import strength_check

class LoginForm(FlaskForm):
    """Login Form fields"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Registration Form fields"""
    name = StringField('Name', validators=[DataRequired()])
    organisation = StringField('Organisation', validators=[DataRequired(
        message="If not appliable use N/A")], description="If not appliable use N/A")
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    admin = BooleanField('Admin')
    reviewer = BooleanField('Reviewer')
    recaptcha = RecaptchaField()
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Checks if username is already used"""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """Checks if email is already used"""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_password(self, password):
        """Calls function to check password"""
        ans = strength_check(password.data)
        if ans != 0:
            raise ValidationError(ans)

class ChangePasswordForm(FlaskForm):
    """Change Your Password"""
    currentpassword = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')

    def validate_password(self, password):
        """Calls function to check password"""
        ans = strength_check(password.data)
        if ans != 0:
            raise ValidationError(ans)
