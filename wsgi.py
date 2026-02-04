"""
WSGI entry point for production deployment.
Used by Gunicorn on Render.
"""
import os
from app import create_app

# Use production config by default, but allow override via environment
config_name = os.environ.get('FLASK_CONFIG', 'production')
app = create_app(config_name)

if __name__ == "__main__":
    app.run()
