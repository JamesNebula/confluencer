import os
import requests

# Load API key from .env
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
if not api_key:
    print("❌ ALPHA_VANTAGE_API_KEY not set in .env")
    exit(1)

print(f"Testing Alpha Vantage API with key: {api_key[:5]}...")
url = "https://www.alphavantage.co/query"
params = {
    'function': 'FX_DAILY',
    'from_symbol': 'EUR',
    'to_symbol': 'USD',
    'apikey': api_key,
    'outputsize': 'compact'
}

response = requests.get(url, params=params, timeout=10)
data = response.json()

if 'Error Message' in data:
    print(f"❌ API Error: {data['Error Message']}")
elif 'Time Series FX (Daily)' in data:
    ts = data['Time Series FX (Daily)']
    dates = list(ts.keys())[:3]
    print(f"✅ SUCCESS! Retrieved {len(ts)} days of EUR/USD data")
    print(f"   Most recent dates: {dates}")
    print(f"   Sample data: {ts[dates[0]]}")
else:
    print(f"⚠️ Unexpected response. Keys: {list(data.keys())}")
    print(f"   Full response: {data}")