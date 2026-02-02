from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

# Create blueprint with URL prefix
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    
    GET: Display login form
    POST: Process login form submission
    
    Returns:
        Rendered template or redirect response
    """
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('dashboard.index'))
    
    # Create form instance
    form = LoginForm()
    
    # Process form submission (POST request)
    if form.validate_on_submit():
        # Find user by username OR email
        user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.username.data)
        ).first()
        
        # Check if user exists and password is correct
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        # Log user in
        login_user(user, remember=form.remember_me.data)
        
        # Update last seen timestamp
        user.update_last_seen()
        
        # Flash success message
        flash(f'Welcome back, {user.username}!', 'success')
        
        # Redirect to next page or dashboard
        # The 'next' parameter is used for redirecting after login
        next_page = request.args.get('next')
        
        # Security check: only redirect to relative URLs (prevent open redirect vulnerability)
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard.index')
        
        return redirect(next_page)
    
    # Render login form (GET request)
    return render_template('auth/login.html', title='Sign In', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    
    GET: Display registration form
    POST: Process registration form submission
    
    Returns:
        Rendered template or redirect response
    """
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        flash('You are already logged in!', 'info')
        return redirect(url_for('dashboard.index'))
    
    # Create form instance
    form = RegistrationForm()
    
    # Process form submission (POST request)
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            account_balance=10000.0  # Default demo account balance
        )
        
        # Set hashed password
        user.set_password(form.password.data)
        
        # Add to database session
        db.session.add(user)
        
        # Commit to database
        db.session.commit()
        
        # Flash success message
        flash('Congratulations, you are now a registered user!', 'success')
        
        # Redirect to login page
        return redirect(url_for('auth.login'))
    
    # Render registration form (GET request)
    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/logout')
def logout():
    """
    Handle user logout.
    
    Returns:
        Redirect response to login page
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))