"""
Controls forms in competitions
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
from app import submission_uploads

class CompetitionForm(FlaskForm):
    """Creates or edits a Competition"""
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=64)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=1, max=280)])
    submit = SubmitField('Submit')

class CategoryForm(FlaskForm):
    """Creates or edits a Category"""
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=64)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=1, max=280)])
    submit = SubmitField('Submit')

class SubmissionForm(FlaskForm):
    """Creates or edits a Submission"""
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=64)])
    body = TextAreaField('Body', validators=[DataRequired(), Length(min=1, max=10000)])
    submit = SubmitField('Submit')


def submission_edit_categories_form(submission, categories):
    """Generates form"""
    for _, category in enumerate(categories):
        if submission.check_category(category.id) == 1:
            passed = "checked"
        else:
            passed = ""
        setattr(BlankForm, str(category.id), BooleanField(category.name, default=passed))
    BlankForm.submit = SubmitField('Submit')
    return BlankForm()

class SubmissionUploadForm(FlaskForm):
    """Upload an Avatar"""
    fileUpload = FileField('File', validators=[FileRequired(), FileAllowed(
        submission_uploads, 'File type not allowed')])
    submit = SubmitField('Upload File')

class SubmissionVotingForm(FlaskForm):
    """Upload an Avatar"""
    score = IntegerField('Score', validators=[NumberRange(min=0, max=10)])
    comment = TextAreaField('Comment', validators=[DataRequired(), Length(min=1, max=10000)])
    submit = SubmitField('Vote')

class BlankForm(FlaskForm):
    """Supposed to be blank"""
