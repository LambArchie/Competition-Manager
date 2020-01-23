"""
Initialises app
"""
import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, IMAGES, DEFAULTS, AUDIO, ARCHIVES
from flask_bootstrap import Bootstrap
from config import Config

bootstrap = Bootstrap()
db = SQLAlchemy()
login = LoginManager()
migrate = Migrate()
login.login_view = 'auth.login'
login.login_message_category = 'error'
avatar_uploads = UploadSet('avatars', IMAGES)
submission_uploads = UploadSet('submissions', DEFAULTS + AUDIO + ARCHIVES +
                               tuple('''psd xcf ai eps opus mp4 mkv mov wmv mpg avi m4v webm
                               tiff tif odt vsd vss vdx vsx vsdx vssx'''.split()))

def create_app(config_class=Config):
    """Initialises the app"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    bootstrap.init_app(app)
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)
    configure_uploads(app, avatar_uploads)
    configure_uploads(app, submission_uploads)

    from app.api_v1 import bp as api_v1_bp
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.home import bp as home_bp
    app.register_blueprint(home_bp, url_prefix='/')

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.competition import bp as competition_bp
    app.register_blueprint(competition_bp, url_prefix='/competition')

    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/microblog.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app
