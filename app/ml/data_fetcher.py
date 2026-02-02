"""
Forex data fetching utilities using yfinance.

Note: yfinance doesn't support all forex pairs directly.
We use the convention: 'EURUSD=X' for EUR/USD
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional


def get_forex_symbol(pair: str) -> str:
    """
    Convert currency pair to yfinance symbol format.
    
    Args:
        pair: Currency pair like 'EURUSD'
        
    Returns:
        yfinance symbol like 'EURUSD=X'
    """
    # Handle common forex pairs
    valid_pairs = [
        'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 
        'NZDUSD', 'USDCHF', 'EURGBP', 'EURJPY', 'GBPJPY'
    ]
    
    if pair not in valid_pairs:
        raise ValueError(f"Unsupported currency pair: {pair}. Supported pairs: {valid_pairs}")
    
    return f"{pair}=X"


def fetch_historical_data(pair: str, period: str = '4y') -> pd.DataFrame:
    """
    Fetch historical forex data using yfinance.
    
    Args:
        pair: Currency pair (e.g., 'EURUSD')
        period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '4y', 'max')
        
    Returns:
        DataFrame with OHLCV data
    """
    symbol = get_forex_symbol(pair)
    
    try:
        # Fetch data
        data = yf.download(symbol, period=period, interval='1d')
        
        if data.empty:
            raise ValueError(f"No data returned for {pair}")
        
        # Reset index to make Date a column
        data = data.reset_index()
        
        # Rename columns for consistency
        data.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        
        # Convert date to datetime
        data['date'] = pd.to_datetime(data['date']).dt.date
        
        # Fill NaN volume with 0 (forex often has no volume data)
        data['volume'] = data['volume'].fillna(0)
        
        return data
    
    except Exception as e:
        raise RuntimeError(f"Failed to fetch data for {pair}: {str(e)}")


def get_recent_data(pair: str, days: int = 30) -> pd.DataFrame:
    """
    Fetch recent data for prediction.
    
    Args:
        pair: Currency pair
        days: Number of days to fetch
        
    Returns:
        DataFrame with recent OHLCV data
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    symbol = get_forex_symbol(pair)
    
    data = yf.download(symbol, start=start_date, end=end_date, interval='1d')
    
    if data.empty:
        raise ValueError(f"No recent data for {pair}")
    
    data = data.reset_index()
    data.rename(columns={
        'Date': 'date',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    }, inplace=True)
    
    data['date'] = pd.to_datetime(data['date']).dt.date
    data['volume'] = data['volume'].fillna(0)
    
    return data