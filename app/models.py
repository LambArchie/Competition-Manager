"""
Controls DB models
"""
import base64
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

CATEGORY_REVIEW_ASSOC = db.Table('category_review_assoc',
                                 db.Column('categories', db.Integer, db.ForeignKey('category.id')),
                                 db.Column('reviews', db.Integer, db.ForeignKey('review.id'))
                                )

@login.user_loader
def load_user(user_id):
    """Returns user details"""
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """Controls the User SQL Table"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    review = db.relationship('Review', backref='author', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    avatar = db.Column(db.String(70), default="")
    admin = db.Column(db.Boolean, default=False)
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

    def to_json(self):
        """Returns user objects for api creation"""
        return {
            "admin": self.admin,
            "email": self.email,
            "id": self.id,
            "lastSeen": self.last_seen,
            "username": self.username
        }

    def from_json(self, data, new_user=False):
        """Creates or modifies user"""
        for field in ['username', 'email', 'admin']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        """Generates a new token"""
        now = datetime.utcnow()
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
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

class Competition(db.Model):
    """Controls Competition SQL table"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    body = db.Column(db.String(280))
    categories = db.relationship("Category")
    reviews = db.relationship("Review")

    def __repr__(self):
        """Printable return"""
        return '<Competition {}>'.format(self.body)

    def to_json(self):
        """Returns user objects for api creation"""
        return {
            "body": self.body,
            "id": self.id,
            "name": self.name
        }

class Category(db.Model):
    """Controls Categories SQL table"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    body = db.Column(db.String(280))
    comp_id = db.Column(db.Integer, db.ForeignKey('competition.id'))

    def __repr__(self):
        """Printable return"""
        return '<Category {}>'.format(self.body)

    def to_json(self):
        """Returns user objects for api creation"""
        return {
            "body": self.body,
            "comp_id": self.comp_id,
            "id": self.id,
            "name": self.name
        }

class Review(db.Model):
    """Controls the Review SQL table"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    body = db.Column(db.String(10000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comp_id = db.Column(db.Integer, db.ForeignKey('competition.id'))
    categories = db.relationship(
        "Category", secondary=CATEGORY_REVIEW_ASSOC,
        backref='reviews')

    def __repr__(self):
        """Printable return"""
        return '<Review {}>'.format(self.body)

    def to_json(self):
        """Returns user objects for api creation"""
        return {
            "body": self.body,
            "cat_id": self.id,
            "comp_id": self.comp_id,
            "id": self.id,
            "name": self.name,
            "timestamp": self.timestamp,
            "user_id": self.user_id
        }

    def check_category(self, category):
        """Checks review is in category"""
        cat_correct = False
        for i in range(len(self.categories)):
            if category == self.categories[i].id:
                cat_correct = True
                break
        return cat_correct
