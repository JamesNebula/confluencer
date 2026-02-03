# 📈 Forex Confluence App

A professional Flask-based web application for forex trading analysis combining technical analysis with machine learning predictions.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Features

### 🔍 Technical Analysis
- **Confluence Scoring System** - Weighted analysis combining 5 key factors:
  - Timeframe alignment (30%)
  - Pattern confirmation (25%)
  - Support/Resistance levels (20%)
  - EMA alignment (15%)
  - Volume confirmation (10%)
- Visual breakdown of each factor's contribution
- Save and review historical analyses

### 🤖 Machine Learning Predictions
- **Random Forest Classifier** trained on 14 technical indicators
- Real-time forex data from Alpha Vantage API
- Daily/Weekly trend probability forecasts
- Feature importance visualization
- Model persistence (saves after first training)

### 📊 Trade Tracking
- Complete trade history with P/L calculation
- Performance metrics: Win rate, profit factor, avg win/loss
- Pagination for large trade histories
- Close trades with automatic P/L calculation

### 🔐 Secure Authentication
- Password hashing with bcrypt
- CSRF protection on all forms
- Session management with Flask-Login
- User-specific data isolation

## 🚀 Tech Stack

### Backend
- **Flask 3.0** - Web framework
- **Flask-SQLAlchemy** - ORM for database
- **Flask-Login** - User session management
- **Flask-WTF** - Forms and CSRF protection
- **Flask-Migrate** - Database migrations

### Database
- **SQLite** (development)
- **PostgreSQL** (production-ready)

### Data & ML
- **Alpha Vantage API** - Real forex data
- **pandas** - Data manipulation
- **scikit-learn** - Machine learning (Random Forest)

### Frontend
- **Bootstrap 5** - Responsive UI
- **Jinja2** - Template engine