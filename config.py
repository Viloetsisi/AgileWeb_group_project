import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change_this_to_a_secure_random_key')
    DB_PATH = os.path.join(os.path.dirname(__file__), 'pathfinder.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'pathfinder.donotreply@gmail.com'
    MAIL_PASSWORD = 'lwzm kdun lziv ywfv'
    MAIL_DEFAULT_SENDER = "PathFinder <pathfinder.donotreply@gmail.com>"
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
