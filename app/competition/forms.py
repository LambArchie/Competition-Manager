"""
Controls forms in competitions
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from app import review_uploads

class CompetitionCreateForm(FlaskForm):
    """Creates a Competition"""
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=64)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=1, max=280)])
    submit = SubmitField('Submit')

class CategoryCreateForm(FlaskForm):
    """Creates a Category"""
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=64)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=1, max=280)])
    submit = SubmitField('Submit')

class ReviewCreateForm(FlaskForm):
    """Creates a Review"""
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=64)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=1, max=10000)])
    submit = SubmitField('Submit')

class ReviewEditForm(FlaskForm):
    """Creates a Review"""
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=64)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=1, max=10000)])
    submit = SubmitField('Submit')

class ReviewUploadForm(FlaskForm):
    """Upload an Avatar"""
    fileUpload = FileField('File', validators=[FileRequired(), FileAllowed(review_uploads, 'File type not allowed')])
    submit = SubmitField('Upload File')
