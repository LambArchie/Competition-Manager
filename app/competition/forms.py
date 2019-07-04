"""
Controls forms in competitions
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length

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
