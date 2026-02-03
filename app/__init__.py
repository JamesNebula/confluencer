from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_wtf.csrf import CSRFProtect
from config import ProductionConfig, get_config
import os

# Initialize extensions WITHOUT app instance (deferred initialization)
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name='development'):
    """
    Application factory function.
    
    Creates and configures a Flask app instance with the given configuration.
    
    Args:
        config_name (str): Configuration name ('development', 'testing', 'production')
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask app instance
    app = Flask(__name__, instance_relative_config=True)
    
    # Ensure instance folder exists FIRST (before config needs it)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        print(f"✅ Instance folder: {app.instance_path}")
    except OSError as e:
        print(f"⚠️  Could not create instance folder: {e}")
        raise
    
    if config_name == 'production':
    # Production uses DATABASE_URL from environment
        app.config.from_object(ProductionConfig())
    else:
    # Development uses instance folder
        config_obj = get_config(config_name, app.instance_path)
        app.config.from_object(config_obj)
    
    # Initialize extensions with app instance
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'  # type: ignore # Where to redirect if login required
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'  # Bootstrap alert class
    
    # Tell Flask-Login how to load users from the database
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """
        Flask-Login callback to load user from database.
        
        This is REQUIRED for Flask-Login to work.
        
        Args:
            user_id (str): User ID as string (from session)
            
        Returns:
            User or None: User object if found, None otherwise
        """
        return User.query.get(int(user_id))
    
    from app.routes import auth_bp, dashboard_bp, confluence_bp, predictions_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(confluence_bp)
    app.register_blueprint(predictions_bp)
    
    # Create database tables if they don't exist
    with app.app_context():
        print("🔄 Creating database tables...")
        db.create_all()
        print("✅ Database tables created!")
    
    # Register error handlers
    register_error_handlers(app)
    
    return app


def register_error_handlers(app):
    """
    Register custom error handlers for the application.
    """
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors"""
        return {
            'error': 'Page not found',
            'message': 'The page you requested does not exist.'
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error"""
        db.session.rollback()
        return {
            'error': 'Internal server error',
            'message': 'Something went wrong on our end. Please try again later.'
        }, 500