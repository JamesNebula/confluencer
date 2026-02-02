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
    
    # Relationships
    trades = db.relationship('TradeHistory', backref='trader', lazy='dynamic',
                           cascade='all, delete-orphan')
    
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


class TradeHistory(db.Model):
    """
    Track user's trading history with full trade details.
    
    Supports both open and closed trades with P/L calculation.
    """
    __tablename__ = 'trade_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Trade identification
    currency_pair = db.Column(db.String(10), nullable=False, index=True)  # e.g., 'EURUSD'
    direction = db.Column(db.String(10), nullable=False)  # 'BUY' or 'SELL'
    
    # Price levels
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float)  # Null if trade still open
    stop_loss = db.Column(db.Float)
    take_profit = db.Column(db.Float)
    
    # Position sizing
    position_size = db.Column(db.Float, default=0.01)  # Lot size (default 0.01 mini lot)
    
    # Results
    pnl = db.Column(db.Float)  # Profit/Loss in account currency
    pnl_percentage = db.Column(db.Float)  # P/L as percentage of account
    status = db.Column(db.String(20), default='OPEN')  # OPEN, CLOSED, STOPPED_OUT
    
    # Optional notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    closed_at = db.Column(db.DateTime)
    
    def calculate_pnl(self):
        """
        Calculate profit/loss based on entry and exit prices.
        
        For BUY trades: P/L = (exit - entry) * position_size * pip_value
        For SELL trades: P/L = (entry - exit) * position_size * pip_value
        
        Note: Simplified calculation - real forex would use pip values per pair
        """
        if self.exit_price is None:
            return None
        
        # Simplified P/L calculation (assuming 100,000 units per standard lot)
        # In real forex, pip values vary by currency pair
        if self.direction == 'BUY':
            price_diff = self.exit_price - self.entry_price
        else:  # SELL
            price_diff = self.entry_price - self.exit_price
        
        # Calculate P/L (simplified - real trading uses pip values)
        self.pnl = price_diff * self.position_size * 100000  # 100k units per lot
        
        # Calculate P/L as percentage of entry value
        entry_value = self.entry_price * self.position_size * 100000
        if entry_value != 0:
            self.pnl_percentage = (self.pnl / entry_value) * 100
        
        self.status = 'CLOSED'
        self.closed_at = datetime.utcnow()
        
        return self.pnl
    
    def get_pip_value(self, currency_pair):
        """
        Get pip value for a currency pair (simplified).
        
        In real trading, pip values depend on:
        - Currency pair
        - Account currency
        - Position size
        
        Args:
            currency_pair (str): Currency pair like 'EURUSD'
            
        Returns:
            float: Pip value in account currency
        """
        # Simplified: Most major pairs have $10 per pip per standard lot
        # This would be more complex in a real trading system
        return 10.0 * self.position_size
    
    def __repr__(self):
        """String representation for debugging."""
        return f'<Trade {self.direction} {self.currency_pair} @ {self.entry_price}>'

class AnalysisSession(db.Model):
    """
    Store user's technical analysis sessions for confluence scoring.
    
    Tracks all factors considered and the resulting recommendation.
    """
    __tablename__ = 'analysis_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Analysis parameters
    currency_pair = db.Column(db.String(10), nullable=False, index=True)
    timeframe = db.Column(db.String(5), nullable=False)  # '4H', 'D', 'W'
    
    # Confluence factors (stored as JSON for flexibility)
    confluence_data = db.Column(db.Text)  # JSON string of all factors and their values
    
    # Results
    recommendation = db.Column(db.String(10))  # 'BUY', 'SELL', 'HOLD', 'NEUTRAL'
    confidence_score = db.Column(db.Float)  # 0-100%
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        """String representation for debugging."""
        return f'<Analysis {self.currency_pair} {self.timeframe} - {self.recommendation}>'

