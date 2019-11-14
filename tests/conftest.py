"""
Sets up features the rest of the tests use
"""
from os import path as osPath
from sys import path as sysPath
import pytest
myPath = osPath.dirname(osPath.abspath(__file__))
sysPath.insert(0, myPath + '/../')
from app import create_app, db

class TestConfig():
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    BCRYPT_LOG_ROUNDS = 2
    WTF_CSRF_ENABLED = False
    UPLOADS_DEFAULT_DEST = '/tmp/'
    UPLOADED_IMAGES_DEST = UPLOADS_DEFAULT_DEST
    SQLALCHEMY_TRACK_MODIFICATIONS = False

@pytest.fixture(scope='module')
def test_client():
    app = create_app(TestConfig)
    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()

@pytest.fixture(scope='module')
def setup_database(test_client):
    db.create_all()
    db.session.commit()

    yield db

    db.drop_all()