import os
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <xiaoaoxtu@yahoo.com>'
    FLASKY_ADMIN = os.getenv('FLASKY_ADMIN')

    @staticmethod
    def init_app(app):
    	pass


class DevelopmentConfig(Config):
    UPLOAD_FOLDER = 'uploads'
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_URE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = 'mysql://root:myaws@127.0.0.1/qiubaiDB'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class ReleaseConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:myaws@52.43.221.136/qiubaiDB'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
config = {
		'development' : DevelopmentConfig,
        'release' : ReleaseConfig,
	}