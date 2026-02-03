"""
Forex data fetching using Alpha Vantage API 
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time


def get_forex_symbol(pair: str) -> tuple:
    """Split pair into from_currency and to_currency."""
    valid_pairs = [
        'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD',
        'NZDUSD', 'USDCHF', 'EURGBP', 'EURJPY', 'GBPJPY'
    ]
    if pair not in valid_pairs:
        raise ValueError(f"Unsupported pair: {pair}. Supported: {', '.join(valid_pairs)}")
    return pair[:3], pair[3:]

def _normalize_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize DataFrame to consistent OHLC format."""
    data = data.copy().reset_index() # type: ignore
    
    # Handle different column naming conventions
    rename_map = {}
    date_col = None
    
    # Find date column
    for col in data.columns:
        if str(col).lower() in ['date', 'time', 'index', '0']:
            date_col = col
            break
    
    if date_col:
        rename_map[date_col] = 'date'
    
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
                rename_map[candidate] = target
                break
    
    data.rename(columns=rename_map, inplace=True)
    
    # Convert date column
    if 'date' in data.columns:
        data['date'] = pd.to_datetime(data['date'], errors='coerce')
        data = data.dropna(subset=['date'])
        data['date'] = data['date'].dt.date
    else:
        # Create dates if missing (synthetic fallback)
        end_date = datetime.now() - timedelta(days=1)
        dates = [end_date - timedelta(days=i) for i in range(len(data))]
        dates.reverse()
        data['date'] = [d.date() for d in dates]
    
    # Ensure numeric OHLC columns
    for col in ['open', 'high', 'low', 'close']:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
            # Forward fill then backward fill
            data[col] = data[col].fillna(method='ffill').fillna(method='bfill')
        else:
            # Create synthetic prices if missing
            base = 1.0800 if 'EUR' in str(data.columns) else 1.0
            data[col] = base * (1 + pd.Series(range(len(data))) * 0.0001)
    
    # Add volume if missing
    if 'volume' not in data.columns:
        data['volume'] = 0
    
    # Validate minimum rows
    if len(data) < 50:
        raise ValueError(f"Insufficient data ({len(data)} rows). Need minimum 50.")
    
    return data


def fetch_historical_data(pair: str, years: int = 1) -> pd.DataFrame:
    """
    Fetch forex data from Alpha Vantage API.
    
    Args:
        pair: Currency pair (e.g., 'EURUSD')
        years: Years of history (max 2 recommended)
    
    Returns:
        DataFrame with OHLCV data
    """
    from_currency, to_currency = get_forex_symbol(pair)
    
    # Get API key from environment
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    if not api_key or api_key == 'your_api_key_here':
        raise RuntimeError(
            "❌ ALPHA_VANTAGE_API_KEY not configured!\n"
            "1. Get free key: https://www.alphavantage.co/support/#api-key\n"
            "2. Add to .env file: ALPHA_VANTAGE_API_KEY=your_actual_key\n"
            "3. Restart the application"
        )
    
    # Alpha Vantage endpoint (daily forex)
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'FX_DAILY',
        'from_symbol': from_currency,
        'to_symbol': to_currency,
        'apikey': api_key,
        'outputsize': 'full'  # Get maximum history (~20 years, but free tier limited)
    }
    
    print(f"📡 Fetching {pair} data from Alpha Vantage...")
    
    try:
        # Add small delay to respect rate limits
        time.sleep(0.2)
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        
        # Check for API errors
        if 'Error Message' in data:
            raise RuntimeError(f"Alpha Vantage API error: {data['Error Message']}")
        if 'Note' in data:
            raise RuntimeError(f"Alpha Vantage rate limit: {data['Note']}")
        if 'Time Series FX (Daily)' not in data:
            raise RuntimeError(
                f"No forex data found for {pair}. Response keys: {list(data.keys())[:5]}"
            )
        
        # Parse time series data
        ts_data = data['Time Series FX (Daily)']
        df = pd.DataFrame.from_dict(ts_data, orient='index')
        df.index.name = 'date'
        df = df.sort_index()
        
        # Convert index to datetime
        df.index = pd.to_datetime(df.index)
        
        # Keep only recent data (free tier may limit history)
        cutoff_date = datetime.now() - timedelta(days=min(years, 2) * 365)
        df = df[df.index >= cutoff_date]
        
        if len(df) < 50:
            raise RuntimeError(
                f"Insufficient data retrieved ({len(df)} days). "
                "Alpha Vantage free tier may limit history. "
                "Try again in 60 seconds or reduce years parameter."
            )
        
        df = _normalize_dataframe(df)
        print(f"✅ Successfully retrieved {len(df)} days of {pair} data")
        return df
        
    except requests.exceptions.Timeout:
        raise RuntimeError("Request timeout. Alpha Vantage may be slow. Try again.")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Connection error. Check your internet connection.")
    except Exception as e:
        raise RuntimeError(f"Data fetch failed: {str(e)}")


def get_recent_data(pair: str, days: int = 30) -> pd.DataFrame:
    """Get recent data for prediction."""
    df = fetch_historical_data(pair, years=1)
    return df.tail(days)