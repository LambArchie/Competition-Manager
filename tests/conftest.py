"""
Sets up features the rest of the tests use
"""
from os import path as osPath
from sys import path as sysPath
import pytest
myPath = osPath.dirname(osPath.abspath(__file__))
sysPath.insert(0, myPath + '/../')
from app import create_app, db
from app.database.models import User

class TestConfig():
    """Test Config (Should be similar to real config)"""
    TESTING = True
    DISABLE_PUBLIC_REGISTRATION = False
    SECRET_KEY = 'a'
    MIN_LENGTH = 6
    HIBP_PW_CHECK = True
    CAPTCHA_ENABLED = False 
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 2
    WTF_CSRF_ENABLED = False
    UPLOADS_DEFAULT_DEST = '/tmp/'
    UPLOADED_IMAGES_DEST = UPLOADS_DEFAULT_DEST
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class Variables():
    def __init__(self, app, db, users):
        self.app = app
        self.db = db
        self.users = users

db_users = [["admin", "admin@org.com", "Administrator", "N/A", True, True, "AYyQ6S69rMr5.a^4"],
        ["reviewer", "reviewer@org.com", "Reviewer", "N/A", False, True, "AYyQ6S69rMr5.a^4"],
        ["standard", "standard@org.com", "Standard Account", "N/A", False, False, "AYyQ6S69rMr5.a^4"]
        ]

def create_user(db, username, email, name, organisation, admin, reviewer, password):
    u = User(username=username, email=email, name=name, organisation=organisation, admin=admin, reviewer=reviewer)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u

@pytest.fixture(scope='module')
def test_client():
    app = create_app(TestConfig)
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()

@pytest.fixture(scope='module')
def test_database(test_client):
    db.create_all()
    db.session.commit()

    yield Variables(test_client, db, [])
    db.drop_all()

@pytest.fixture(scope='module')
def test_users(test_database):
    for _, user in enumerate(db_users):
        create_user(test_database.db, user[0], user[1], user[2], user[3], user[4], user[5], user[6])

    yield Variables(test_database.app, test_database.db, db_users)