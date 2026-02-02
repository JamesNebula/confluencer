from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange
from app.models import User


class LoginForm(FlaskForm):
    """
    Form for user login.
    """
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """
    Form for user registration.
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
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class TradeEntryForm(FlaskForm):
    """
    Form for entering a new trade.
    """
    currency_pair = StringField('Currency Pair', validators=[
        DataRequired(message='Currency pair is required'),
        Length(max=10, message='Currency pair too long')
    ], default='EURUSD')
    
    direction = SelectField('Direction', choices=[
        ('BUY', 'BUY'),
        ('SELL', 'SELL')
    ], validators=[DataRequired()])
    
    entry_price = FloatField('Entry Price', validators=[
        DataRequired(message='Entry price is required'),
        NumberRange(min=0, message='Price must be positive')
    ])
    
    stop_loss = FloatField('Stop Loss', validators=[
        NumberRange(min=0, message='Stop loss must be positive')
    ], description='Optional: Price to exit if trade goes against you')
    
    take_profit = FloatField('Take Profit', validators=[
        NumberRange(min=0, message='Take profit must be positive')
    ], description='Optional: Price to exit for profit')
    
    position_size = FloatField('Position Size (lots)', validators=[
        DataRequired(message='Position size is required'),
        NumberRange(min=0.01, max=100, message='Position size must be between 0.01 and 100 lots')
    ], default=0.01, description='Standard lot = 1.0, Mini lot = 0.1, Micro lot = 0.01')
    
    notes = TextAreaField('Notes', description='Optional: Your trade rationale or notes')
    
    submit = SubmitField('Save Trade')