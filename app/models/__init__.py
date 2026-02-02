"""
Database models for the Forex Confluence application.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """
    User model for authentication and account management.
    
    Inherits from:
        - UserMixin: Provides default implementations for Flask-Login
        - db.Model: SQLAlchemy base class for database models
    """
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # User credentials (unique and required)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Account settings
    account_balance = db.Column(db.Float, default=10000.0)  # Default demo account
    risk_percentage = db.Column(db.Float, default=2.0)  # Default 2% risk per trade
    
    def set_password(self, password):
        """
        Hash and store password securely.
        
        Args:
            password (str): Plain text password
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verify password against stored hash.
        
        Args:
            password (str): Plain text password to check
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def update_last_seen(self):
        """Update last seen timestamp to current time."""
        self.last_seen = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        """String representation for debugging."""
        return f'<User {self.username}>'