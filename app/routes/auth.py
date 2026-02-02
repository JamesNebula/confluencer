from flask import Blueprint, render_template

# Create blueprint object 
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login():
    # placeholder login route
    return render_template('auth/login.html', title='Login')