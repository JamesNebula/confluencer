import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    """
    Base config class with settings common to all environments.
    """
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-prod'

    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///instance/forex_app.db'
    
    # Disable track modifications 
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Record queries for debugging
    SQLALCHEMY_RECORD_QUERIES = True

class DevelopmentConfig(Config):
    """
    Dev config with debug features enabled
    """
    DEBUG = True
    # Echo SQL queries to console for debugging
    SQLALCHEMY_ECHO = False # set to true to see all SQL queries

class TestingConfig(Config):
    """
    Testing config with isolated database
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/test.db'
    # Disable csrf for easier testing
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """
    Production config with security hardening
    """
    DEBUG = False
    # security enhancements
    SESSION_COOKIE_SECURE = True # only send cookies over https
    SESSION_COOKIE_HTTPONLY = True # prevent javascript access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax' # CSRF protection

    # in production we expect database_url to be set externally
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    # Validate required production settings
    @classmethod
    def init_app(cls, app):
        if not app.config.get('SECRET_KEY') or 'dev-secret' in app.config.get('SECRET_KEY', ''):
            raise ValueError('SECRET_KEY must be set and secure in production!')
        if not app.config.get('DATABASE_URL'):
            raise ValueError('DATABASE_URL must be set in production!')
        
# Configuration dictionary for easy selection
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}