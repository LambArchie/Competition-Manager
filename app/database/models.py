"""
Controls DB models
"""
import base64
import os
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login
from app.database.uuid import GUID

db.GUID = GUID
CATEGORY_SUBMISSION_ASSOC = db.Table('category_submission_assoc',
                                     db.Column('categories', db.Integer, db.ForeignKey('category.id')),
                                     db.Column('submissions', db.Integer, db.ForeignKey('submission.id'))
                                     )

@login.user_loader
def load_user(user_id):
    """Returns user details"""
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """Controls the User SQL Table"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    name = db.Column(db.String(64))
    organisation = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    submission = db.relationship('Submission', backref='author', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(70), default="")
    admin = db.Column(db.Boolean, default=False)
    reviewer = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __repr__(self):
        """Printable return"""
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """Returns the hash of the given password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the password matches"""
        return check_password_hash(self.password_hash, password)

    def avatar_get(self):
        """Returns avatar url"""
        return '/user/{}/avatar'.format(self.username)

    def avatar_filename(self, filename):
        """Sets avatar name"""
        self.avatar = filename

    def to_json(self, admin=False):
        """Returns the user object for the api"""
        user = {
            "name": self.name,
            "id": self.id,
            "lastSeen": self.last_seen,
            "organisation": self.organisation,
            "username": self.username
        }
        if admin:
            user.update({
                "admin": self.admin,
                "email": self.email,
                "reviewer": self.reviewer,
            })
        return user

    def from_json(self, data, admin=False, new_user=False):
        """Creates or modifies user"""
        for field in ['name', 'username', 'organisation', 'email', 'admin', 'reviewer']:
            if field in data:
                setattr(self, field, data[field])
        if 'password' in data and (admin or new_user):
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        """Generates a new token"""
        now = datetime.utcnow()
        self.token_expiration = datetime.strptime(self.token_expiration, "%Y-%m-%d %H:%M:%S.%f")
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        """Revokes token immediately"""
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        """Checks if token is currently valid for that user"""
        query = text("SELECT * FROM user WHERE token = :token LIMIT 1 OFFSET 0")
        user = db.session.query(User).from_statement(query).params(token=token).first()
        if user is None or datetime.strptime(user.token_expiration, "%Y-%m-%d %H:%M:%S.%f") < datetime.utcnow():
            return None
        return user

class Competition(db.Model):
    """Controls Competition SQL table"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    body = db.Column(db.String(1024))
    categories = db.relationship("Category")
    submissions = db.relationship("Submission")

    def __repr__(self):
        """Printable return"""
        return '<Competition {}>'.format(self.body)

    def to_json(self):
        """Returns the competition object for the api"""
        return {
            "body": self.body,
            "id": self.id,
            "name": self.name
        }

class Category(db.Model):
    """Controls Categories SQL table"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    body = db.Column(db.String(1024))
    comp_id = db.Column(db.Integer, db.ForeignKey('competition.id'))

    def __repr__(self):
        """Printable return"""
        return '<Category {}>'.format(self.body)

    def to_json(self):
        """Returns the category object for the api"""
        return {
            "body": self.body,
            "comp_id": self.comp_id,
            "id": self.id,
            "name": self.name
        }

class Submission(db.Model):
    """Controls the Submission SQL table"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    body = db.Column(db.String(32768))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comp_id = db.Column(db.Integer, db.ForeignKey('competition.id'))
    categories = db.relationship(
        "Category", secondary=CATEGORY_SUBMISSION_ASSOC,
        backref='submissions')

    def __repr__(self):
        """Printable return"""
        return '<Submission {}>'.format(self.body)

    def to_json(self, detail=True):
        """Returns the submission object for the api"""
        submission = {
            "id": self.id,
            "name": self.name,
            "timestamp": self.timestamp,
            "user_id": self.user_id
        }
        if detail:
            categories = []
            for _, category in enumerate(self.categories):
                categories.append(category.id)
            submission.update({
                "body": self.body,
                "categories": categories,
                "comp_id": self.comp_id
                })
        return submission

    def check_category(self, cat_check):
        """Checks the submission is in category"""
        cat_correct = False
        categories = self.categories
        for _, category in enumerate(categories):
            if cat_check == category.id:
                cat_correct = True
                break
        return cat_correct

class SubmissionUploads(db.Model):
    """Contains filenames for Uploads
    id is only unique per submission"""
    uuid = db.Column(db.GUID, primary_key=True, default=uuid4)
    id = db.Column(db.Integer)
    filename = db.Column(db.String(64))
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))

    def __repr__(self):
        """Printable return"""
        return '<SubmissionUploads {}>'.format(self.uuid)

    def to_json(self):
        """Returns the uploads object for the api"""
        return {
            "uuid": self.uuid,
            "id": self.id,
            "filename": self.filename,
            "sub_id": self.submission_id
        }

class Votes(db.Model):
    """Contains voting information"""
    id = db.Column(db.Integer, primary_key=True)
    comp_id = db.Column(db.Integer, db.ForeignKey('competition.id'))
    cat_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Integer)
    comments = db.Column(db.String(8192))

    def __repr__(self):
        """Printable return"""
        return '<Votes {}>'.format(self.id)

    def to_json(self):
        """Returns the vote object for the api"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "sub_id": self.submission_id,
            "cat_id": self.cat_id,
            "comp_id": self.comp_id,
            "score": self.score,
            "comments": self.comments
        }
