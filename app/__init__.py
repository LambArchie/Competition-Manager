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
from flask_uploads import UploadSet, configure_uploads, AllExcept, EXECUTABLES, IMAGES, SCRIPTS
from flask_bootstrap import Bootstrap
from config import Config

bootstrap = Bootstrap()
db = SQLAlchemy()
login = LoginManager()
migrate = Migrate()
login.login_view = 'auth.login'
avatar_uploads = UploadSet('avatars', IMAGES)
submission_uploads = UploadSet('submissions', AllExcept(SCRIPTS + EXECUTABLES + tuple('''
                                                docm docb dotm xlsm xltm xll xlam xla pptm potm ppsm
                                                sldm swf app jar scr com msi pif hta cpl msc bat cmd
                                                vb vbs vbe ps1 ps1xml ps2 ps2xml psc1 psc2 inf reg
                                                ws wsf msh msh1 msh2 mshxml msh1xml msh2xml jse py
                                                bash cgi 386 torrent vscript asp cer csr drv sys cpl
                                                crt htaccess htpasswd lnk ksh url pyc'''.split())))

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

from app.database import models
