from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User


class LoginForm(FlaskForm):
    """
    Form for user login.
    
    Fields:
        username: Username or email (accepts either)
        password: User's password
        remember_me: Keep user logged in across sessions
        submit: Submit button
    """
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """
    Form for user registration.
    
    Fields:
        username: Unique username (3-64 characters)
        email: Valid email address
        password: Password (minimum 6 characters)
        password2: Password confirmation
        submit: Submit button
    """
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=64, message='Username must be between 3 and 64 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """
        Custom validator to check if username already exists.
        
        Args:
            username: Username field to validate
            
        Raises:
            ValidationError: If username already exists in database
        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        """
        Custom validator to check if email already exists.
        
        Args:
            email: Email field to validate
            
        Raises:
            ValidationError: If email already exists in database
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')