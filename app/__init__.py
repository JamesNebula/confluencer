from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config
import os

# initialize extensions WITHOUT app instance
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_name='default'):
    """
    Application factory function.
    - creates and configures a flask app instance with the given configuration
    - Args:
        config_name (str): configuration name ('development', 'testing', 'production')
    - Returns:
        Flask: configured Flask application instance
    """
    # Create flask app instance
    app = Flask(__name__, instance_relative_config=True)

    # load config from config.py
    app.config.from_object(config[config_name])

    # Ensure instance folder exists (for SQlite database file)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # folder already exists

    # inititalise extensions with app instance
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Configure flask-login
    login_manager.login_view = 'auth.login' # where to redirect if login required
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info' # bootstrap alert class

    # Register blueprints (modular route handlers)
    # These will be created in future steps
    from app.routes import auth, dashboard
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(dashboard.dashboard_bp)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    # Register error handlers
    register_error_handlers(app)

    return app

def register_error_handlers(app):
    """
    register custom error handlers for the application.
    provides user-friendly error pages instead of default flask errors
    """
    @app.errorhandler(404)
    def not_found_error(error):
        # handle 404 not found errors
        return {
            'error': 'Page not found',
            'message': 'The page you requested does not exist.'
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        # handle 500 internal server error
        # rollback database session on error to prevent stale connections
        db.session.rollback()
        return {
            'error': 'Internal server error',
            'message': 'Something went wrong on our end. Please try again later.'
        }, 500
    