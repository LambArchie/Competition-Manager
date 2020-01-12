"""Controls the config of the application"""
from os import environ, path, urandom
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

# Converts passed booleans to the correct format
def str2bool(v):
    if str(v).lower() in ("yes", "true", "t", "1"):
        return True
    return False

class Config(object):
    """
    Default settings, set variable in .env or set enviromental variables to edit
    """
    # Set or every restart users will have to relogin
    # Use random string. E.g. python -c "import os; os.urandom(24).hex()"
    SECRET_KEY = environ.get('SECRET_KEY') or urandom(24).hex()
    # Use an external db for all production use, sqlite for dev only
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or \
        'sqlite:///' + path.join(basedir, 'app.db')
    MAX_UPLOAD_SIZE = environ.get('MAX_UPLOAD_SIZE') or 4 # MiB
    # Can always create user in admin area
    DISABLE_PUBLIC_REGISTRATION = environ.get('DISABLE_PUBLIC_REGISTRATION') or "False"
    BRAND_NAME = environ.get('BRAND_NAME') or ""

    # Security
    CAPTCHA_ENABLED = environ.get('CAPTCHA_ENABLED') or "False"
    RECAPTCHA_PUBLIC_KEY = environ.get('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = environ.get('RECAPTCHA_PRIVATE_KEY')
    MIN_LENGTH = environ.get('MIN_LENGTH') or 12
    # Uses https://haveibeenpwned.com/Passwords to check password
    # has been in a data breach. Uses k-anonymity for security
    HIBP_PW_CHECK = environ.get('HIBP_PW_CHECK') or "True"

    # Only change below if know what you are doing
    DISABLE_PUBLIC_REGISTRATION = str2bool(DISABLE_PUBLIC_REGISTRATION)
    CAPTCHA_ENABLED = str2bool(CAPTCHA_ENABLED)
    HIBP_PW_CHECK = str2bool(HIBP_PW_CHECK)
    UPLOADS_DEFAULT_DEST = basedir + '/uploads/'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = float(MAX_UPLOAD_SIZE) * 1024 * 1024  # Flask-Uploads need in bytes
    UPLOADED_IMAGES_DEST = UPLOADS_DEFAULT_DEST
