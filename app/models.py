"""
Controls DB models
"""
import base64
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

@login.user_loader
def load_user(id):
    """Returns user details"""
    return User.query.get(int(id))

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
        return '/avatar/{}'.format(self.username)

    def avatar_filename(self, filename):
        """Sets avatar name"""
        self.avatar = filename

    def to_json(self):
        """Returns user objects for api creation"""
        return {
            "email": self.email,
            "isAdmin": self.admin,
            "lastSeen": self.last_seen,
            "username": self.username
        }

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

class Review(db.Model):
    """Controls the Review SQL table"""
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        """Printable return"""
        return '<Review {}>'.format(self.body)
