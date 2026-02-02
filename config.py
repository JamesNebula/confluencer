import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Base configuration class with settings common to all environments.
    """
    # Secret key for sessions, CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Disable track modifications to suppress warning
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Record queries for debugging
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Database will be set in subclass __init__

class DevelopmentConfig(Config):
    """
    Development configuration with debug features enabled.
    """
    DEBUG = True
    SQLALCHEMY_ECHO = False
    
    def __init__(self, instance_path=None):
        """Initialize development config with database path"""
        if instance_path:
            # Use absolute path for SQLite database
            database_path = os.path.join(instance_path, 'forex_app.db')
            # Note: 4 slashes for absolute path on Unix: sqlite:////absolute/path
            self.SQLALCHEMY_DATABASE_URI = f'sqlite:///{database_path}'
            print(f"✅ Database URI: {self.SQLALCHEMY_DATABASE_URI}")
            print(f"✅ Database file: {database_path}")
        else:
            # Fallback to relative path
            self.SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/forex_app.db'

class TestingConfig(Config):
    """
    Testing configuration with isolated database.
    """
    TESTING = True
    
    def __init__(self, instance_path=None):
        """Initialize testing config"""
        if instance_path:
            test_db_path = os.path.join(instance_path, 'test.db')
            self.SQLALCHEMY_DATABASE_URI = f'sqlite:///{test_db_path}'
        else:
            self.SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/test.db'

class ProductionConfig(Config):
    """
    Production configuration with security hardening.
    """
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    def __init__(self):
        """Initialize production config"""
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError('DATABASE_URL must be set in production!')
        self.SQLALCHEMY_DATABASE_URI = database_url
        
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key or 'dev-secret' in secret_key:
            raise ValueError('SECRET_KEY must be set and secure in production!')

# Factory function to get config instance
def get_config(config_name='development', instance_path=None):
    """
    Get configuration instance with proper initialization.
    
    Args:
        config_name: 'development', 'testing', or 'production'
        instance_path: Path to instance folder (for SQLite databases)
    
    Returns:
        Config instance
    """
    if config_name == 'development':
        return DevelopmentConfig(instance_path)
    elif config_name == 'testing':
        return TestingConfig(instance_path)
    elif config_name == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig(instance_path)
