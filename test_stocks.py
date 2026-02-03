import yfinance as yf
import pandas as pd

print("Testing with AAPL (stock)...")
data = yf.download("AAPL", period="1y", interval="1d", progress=False)
print(f"Shape: {data.shape}")
print(f"Columns: {list(data.columns)}")
if not data.empty:
    print(f"First row:\n{data.head(1)}")
else:
    print("❌ Empty data - Yahoo Finance may be blocking all requests")
