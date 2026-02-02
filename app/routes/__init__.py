"""
Routes package exports all blueprint objects for easy import.
"""
from .auth import auth_bp
from .dashboard import dashboard_bp
from .analysis import confluence_bp

__all__ = ['auth_bp', 'dashboard_bp', 'confluence_bp']