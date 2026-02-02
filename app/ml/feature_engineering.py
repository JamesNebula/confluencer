"""
Feature engineering for forex trend prediction.

Creates technical indicators as features for ML model.
"""
import pandas as pd
import numpy as np
from typing import List


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        series: Price series
        period: Lookback period
        
    Returns:
        RSI values (0-100)
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average.
    
    Args:
        series: Price series
        period: EMA period
        
    Returns:
        EMA values
    """
    return series.ewm(span=period, adjust=False).mean()


def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
    """
    Calculate MACD indicator.
    
    Args:
        series: Price series
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line period
        
    Returns:
        Tuple of (MACD line, Signal line, Histogram)
    """
    ema_fast = calculate_ema(series, fast)
    ema_slow = calculate_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(series: pd.Series, period: int = 20, std_dev: int = 2) -> tuple:
    """
    Calculate Bollinger Bands.
    
    Args:
        series: Price series
        period: Lookback period
        std_dev: Standard deviation multiplier
        
    Returns:
        Tuple of (Upper band, Middle band, Lower band)
    """
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    
    return upper, middle, lower


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (volatility indicator).
    
    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: Lookback period
        
    Returns:
        ATR values
    """
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer technical indicator features from OHLCV data.
    
    Args:
        df: DataFrame with OHLCV columns
        
    Returns:
        DataFrame with original columns + engineered features
    """
    df = df.copy()
    
    # Price-based features
    df['returns'] = df['close'].pct_change()
    df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
    
    # Moving averages
    df['ema_20'] = calculate_ema(df['close'], 20)
    df['ema_50'] = calculate_ema(df['close'], 50)
    df['ema_200'] = calculate_ema(df['close'], 200)
    
    # EMA relationships
    df['ema_20_50'] = df['ema_20'] - df['ema_50']
    df['ema_50_200'] = df['ema_50'] - df['ema_200']
    
    # RSI
    df['rsi_14'] = calculate_rsi(df['close'], 14)
    
    # MACD
    macd_line, signal_line, histogram = calculate_macd(df['close'])
    df['macd'] = macd_line
    df['macd_signal'] = signal_line
    df['macd_hist'] = histogram
    
    # Bollinger Bands
    upper, middle, lower = calculate_bollinger_bands(df['close'])
    df['bb_upper'] = upper
    df['bb_middle'] = middle
    df['bb_lower'] = lower
    df['bb_width'] = (upper - lower) / middle  # Normalized bandwidth
    
    # ATR (volatility)
    df['atr_14'] = calculate_atr(df['high'], df['low'], df['close'], 14)
    
    # Support/Resistance proxies
    df['range'] = df['high'] - df['low']
    df['body_size'] = abs(df['close'] - df['open'])
    df['body_ratio'] = df['body_size'] / df['range'].replace(0, np.nan)
    
    # Target variable: Next day's direction (1 = up, 0 = down/same)
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    
    # Drop NaN rows (caused by rolling calculations)
    df = df.dropna()
    
    return df


def get_feature_columns() -> List[str]:
    """
    Get list of feature column names for model training.
    
    Returns:
        List of feature column names
    """
    return [
        'returns', 'log_returns',
        'ema_20', 'ema_50', 'ema_200',
        'ema_20_50', 'ema_50_200',
        'rsi_14',
        'macd', 'macd_signal', 'macd_hist',
        'bb_width', 'atr_14',
        'body_ratio'
    ]