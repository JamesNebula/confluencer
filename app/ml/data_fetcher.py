"""
Forex data fetching using Alpha Vantage API with rate limit handling.

FREE TIER LIMITS (enforced):
- 5 requests per minute
- 100 requests per day
- Always add 12-second delay between requests to stay under 5/min limit
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time
import json


def get_forex_symbol(pair: str) -> tuple:
    """Split pair into from_currency and to_currency."""
    valid_pairs = [
        'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD',
        'NZDUSD', 'USDCHF', 'EURGBP', 'EURJPY', 'GBPJPY'
    ]
    if pair not in valid_pairs:
        raise ValueError(f"Unsupported pair: {pair}. Supported: {', '.join(valid_pairs)}")
    return pair[:3], pair[3:]


def _generate_synthetic_forex_data(pair: str, days: int = 365) -> pd.DataFrame:
    """Generate realistic synthetic forex data for demo/portfolio purposes."""
    import numpy as np
    
    np.random.seed(hash(pair) % 2**32)
    
    # Start from a realistic base price
    base_prices = {
        'EURUSD': 1.0800,
        'GBPUSD': 1.2600,
        'USDJPY': 148.50,
        'AUDUSD': 0.6500,
        'USDCAD': 1.3500,
        'NZDUSD': 0.6000,
        'USDCHF': 0.8800,
        'EURGBP': 0.8550,
        'EURJPY': 160.00,
        'GBPJPY': 187.00
    }
    base = base_prices.get(pair, 1.0000)
    
    # Generate realistic random walk
    returns = np.random.normal(0.0001, 0.008, days)
    prices = base * np.exp(np.cumsum(returns))
    
    # Create dates (working backwards from yesterday)
    end_date = datetime.now() - timedelta(days=1)
    dates = [end_date - timedelta(days=i) for i in range(days)]
    dates.reverse()
    
    # Build DataFrame
    df = pd.DataFrame({
        'date': [d.date() for d in dates],
        'open': prices * (1 + np.random.normal(0, 0.0005, days)),
        'high': prices * (1 + np.abs(np.random.normal(0, 0.001, days))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.001, days))),
        'close': prices,
        'volume': np.random.randint(50000, 200000, days)
    })
    
    return df


def _normalize_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize DataFrame to consistent OHLC format."""
    data = data.copy().reset_index()
    
    # Find date column
    date_col = None
    for col in data.columns:
        if str(col).lower() in ['date', 'time', 'index', '0']:
            date_col = col
            break
    
    if date_col:
        data.rename(columns={date_col: 'date'}, inplace=True)
    
    # Find OHLC columns
    ohlc_map = {
        'open': ['1. open', 'open', 'o'],
        'high': ['2. high', 'high', 'h'],
        'low': ['3. low', 'low', 'l'],
        'close': ['4. close', 'close', 'c']
    }
    
    for target, candidates in ohlc_map.items():
        for candidate in candidates:
            if candidate in data.columns:
                data.rename(columns={candidate: target}, inplace=True)
                break
    
    # Convert date column
    if 'date' in data.columns:
        data['date'] = pd.to_datetime(data['date'], errors='coerce')
        data = data.dropna(subset=['date'])
        data['date'] = data['date'].dt.date
    else:
        end_date = datetime.now() - timedelta(days=1)
        dates = [end_date - timedelta(days=i) for i in range(len(data))]
        dates.reverse()
        data['date'] = [d.date() for d in dates]
    
    # Ensure numeric OHLC columns
    for col in ['open', 'high', 'low', 'close']:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
            data[col] = data[col].fillna(method='ffill').fillna(method='bfill')
        else:
            base = 1.0800 if 'EUR' in str(data.columns) else 1.0
            data[col] = base * (1 + pd.Series(range(len(data))) * 0.0001)
    
    if 'volume' not in data.columns:
        data['volume'] = 0
    
    if len(data) < 50:
        raise ValueError(f"Insufficient data ({len(data)} rows). Need minimum 50.")
    
    return data


def _handle_alpha_vantage_response(response_json: dict, pair: str) -> pd.DataFrame:
    """
    Handle Alpha Vantage API response with proper error detection.
    
    Returns DataFrame if successful, raises informative error otherwise.
    """
    # Check for rate limiting / informational messages
    if 'Information' in response_json:
        msg = response_json['Information']
        if 'per minute' in msg.lower() or 'per day' in msg.lower():
            raise RuntimeError(
                f"Alpha Vantage rate limit exceeded for {pair}.\n"
                f"Free tier: 5 requests/minute, 100/day.\n"
                f"Wait 60 seconds and try again with EURUSD (most reliable pair)."
            )
        else:
            raise RuntimeError(f"Alpha Vantage info: {msg}")
    
    # Check for errors
    if 'Error Message' in response_json:
        raise RuntimeError(f"Alpha Vantage error: {response_json['Error Message']}")
    
    # Check for time series data
    if 'Time Series FX (Daily)' not in response_json:
        raise RuntimeError(
            f"No forex data found for {pair}. Response keys: {list(response_json.keys())}\n"
            f"💡 Try EURUSD - it has the most reliable data on Alpha Vantage free tier."
        )
    
    # Parse time series
    ts_data = response_json['Time Series FX (Daily)']
    df = pd.DataFrame.from_dict(ts_data, orient='index')
    df.index.name = 'date'
    df = df.sort_index()
    df.index = pd.to_datetime(df.index)
    
    # Keep only last 2 years
    cutoff_date = datetime.now() - timedelta(days=730)
    df = df[df.index >= cutoff_date]
    
    if len(df) < 50:
        raise RuntimeError(f"Insufficient data retrieved ({len(df)} days) for {pair}.")
    
    return _normalize_dataframe(df)


def fetch_historical_data(pair: str, years: int = 1) -> pd.DataFrame:
    """
    Fetch forex data from Alpha Vantage API with rate limit protection.
    
    FREE TIER: 5 requests/minute → we add 12-second delay between requests
    """
    from_currency, to_currency = get_forex_symbol(pair)
    
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        raise RuntimeError(
            "❌ ALPHA_VANTAGE_API_KEY not configured!\n"
            "Get free key: https://www.alphavantage.co/support/#api-key\n"
            "Add to Render Environment tab: ALPHA_VANTAGE_API_KEY=your_key"
        )
    
    # CRITICAL: Add delay to respect 5 requests/minute limit
    print(f"⏳ Waiting 12 seconds to respect Alpha Vantage rate limits (5/min)...")
    time.sleep(12)
    
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'FX_DAILY',
        'from_symbol': from_currency,
        'to_symbol': to_currency,
        'apikey': api_key,
        'outputsize': 'full'
    }
    
    print(f"📡 Fetching {pair} data from Alpha Vantage...")
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Handle API response (rate limits, errors, success)
        df = _handle_alpha_vantage_response(data, pair)
        
        print(f"✅ Retrieved {len(df)} days of {pair} data")
        return df
        
    except requests.exceptions.Timeout:
        print("⚠️  Request timeout. Falling back to synthetic demo data...")
        return _generate_synthetic_forex_data(pair, days=365)
    except requests.exceptions.ConnectionError:
        print("⚠️  Connection error. Falling back to synthetic demo data...")
        return _generate_synthetic_forex_data(pair, days=365)
    except Exception as e:
        print(f"⚠️  {str(e)}")
        print(f"💡 Falling back to synthetic demo data for portfolio demo...")
        return _generate_synthetic_forex_data(pair, days=365)


def get_recent_data(pair: str, days: int = 30) -> pd.DataFrame:
    """Get recent data for prediction."""
    df = fetch_historical_data(pair, years=1)
    return df.tail(days)