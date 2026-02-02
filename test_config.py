"""
Test script to verify configuration loads correctly
"""

import os 
from dotenv import load_dotenv
from config import config

load_dotenv()

print(f"Environment variables loaded:")
print(f"    FLASK_APP: {os.environ.get('FLASK_APP')}")
print(f"    FLASK_ENV: {os.environ.get('FLASK_ENV')}")
print(f"    SECRET_KEY starts with: {os.environ.get('SECRET_KEY', '')[:10]}...")

print('\nConfiguration Classes:')
for env_name, config_class in config.items():
    cfg = config_class()
    print(f"    {env_name:12s} -> DB: {cfg.SQLALCHEMY_DATABASE_URI[:30]}...")

print("\nConfiguration Test Passed!")