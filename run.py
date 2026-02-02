"""
Application entry point.
Run with: python run.py
"""
from app import create_app

# Create app instance with development configuration
app = create_app('development')

# Shell context for 'flask shell' command
@app.shell_context_processor
def make_shell_context():
    from app import db
    return {'db': db}

if __name__ == '__main__':
    # Run development server
    app.run(debug=True, host='0.0.0.0', port=5000)