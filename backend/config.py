import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY     = os.environ.get('SECRET_KEY',     'workforce-secret-key-fixed-2026')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'workforce-jwt-secret-key-fixed-2026-secure-32char')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = False

    # Render gives DATABASE_URL starting with postgres:// — SQLAlchemy needs postgresql://
    _db_url = os.environ.get('DATABASE_URL', 'sqlite:///employee_mgmt.db')
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development':  DevelopmentConfig,
    'production':   ProductionConfig,
    'default':      DevelopmentConfig
}
