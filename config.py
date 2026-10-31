import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'easyshare-dev-insecure-secret-key-2026')
    SITE_NAME = os.environ.get('SITE_NAME', 'EasyShare')
    SITE_TAGLINE = os.environ.get('SITE_TAGLINE', 'Borrow. Lend. Sell. Reuse.')

    # Database
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith('postgres://'):
        # Fix legacy postgres:// URI for SQLAlchemy compatibility
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = db_url or f"sqlite:///{BASE_DIR / 'instance' / 'easyshare.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = BASE_DIR / 'app' / 'static' / 'uploads'
    PROFILE_UPLOAD_FOLDER = UPLOAD_FOLDER / 'profiles'
    ITEM_UPLOAD_FOLDER = UPLOAD_FOLDER / 'items'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24 * 14  # 14 days
    REMEMBER_COOKIE_HTTPONLY = True

    # TrustScore Defaults
    INITIAL_TRUST_SCORE = 100.0


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key-for-unit-tests'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENV = 'production'
    # In production, SECRET_KEY must come from environment
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
