"""
Initialises app
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_uploads import UploadSet, IMAGES, configure_uploads
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'auth.login'
bootstrap = Bootstrap(app)
avatars = UploadSet('avatars', IMAGES)
configure_uploads(app, avatars)

from app.admin import bp as admin_bp
from app.api import bp as api_bp
from app.auth import bp as auth_bp
from app.competition import bp as competition_bp
from app.user import bp as user_bp
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(competition_bp, url_prefix='/competition')
app.register_blueprint(user_bp, url_prefix='/user')

from app import routes, models, errors
