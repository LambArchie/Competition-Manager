import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """Settings below can be changed"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    GOOGLE_ANALYTICS_ID = "UA-58178887-2"

    UPLOADS_DEFAULT_DEST = basedir + '/uploads/'
    MAX_UPLOAD_SIZE = 4  # In MiB

    # Do not edit below this line unless you know what you are doing
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = float(MAX_UPLOAD_SIZE) * 1024 * 1024 # Flask-Uploads need in bytes
    UPLOADED_IMAGES_DEST = UPLOADS_DEFAULT_DEST