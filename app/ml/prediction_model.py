"""
Machine learning model for forex trend prediction.

Uses a simple Random Forest classifier for interpretability.
"""
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from app.ml.data_fetcher import fetch_historical_data
from app.ml.feature_engineering import engineer_features, get_feature_columns


class ForexPredictor:
    """
    Forex trend predictor using Random Forest classifier.
    """
    
    def __init__(self, model_path: str = 'instance/ml_model.pkl'):
        """
        Initialize predictor.
        
        Args:
            model_path: Path to save/load trained model
        """
        self.model_path = model_path
        self.model = None
        self.feature_columns = get_feature_columns()
        self.is_trained = False
        
        # Try to load existing model
        if os.path.exists(model_path):
            self.load_model()
    
    def train(self, pair: str = 'EURUSD', period: str = '4y') -> dict:
        """
        Train model on historical data.
        
        Args:
            pair: Currency pair to train on
            period: Historical period to use
            
        Returns:
            Dictionary with training metrics
        """
        # Fetch and prepare data
        df = fetch_historical_data(pair, period)
        df = engineer_features(df)
        
        # Prepare features and target
        X = df[self.feature_columns]
        y = df['target']
        
        # Split data (time-series aware - no shuffling)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=20,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        train_accuracy = accuracy_score(y_train, y_pred_train)
        test_accuracy = accuracy_score(y_test, y_pred_test)
        
        # Save model
        self.save_model()
        
        return {
            'pair': pair,
            'period': period,
            'train_accuracy': round(train_accuracy * 100, 2),
            'test_accuracy': round(test_accuracy * 100, 2),
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'features_used': len(self.feature_columns),
            'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def predict(self, pair: str = 'EURUSD') -> dict:
        """
        Predict next day's trend direction.
        
        Args:
            pair: Currency pair to predict
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_trained and not os.path.exists(self.model_path):
            raise RuntimeError("Model not trained. Call train() first or load a saved model.")
        
        if self.model is None:
            self.load_model()
        
        # Fetch recent data
        df = fetch_historical_data(pair, period='6mo')  # Need enough data for indicators
        df = engineer_features(df)
        
        # Get most recent features
        latest = df.iloc[-1]
        X_latest = latest[self.feature_columns].values.reshape(1, -1)
        
        # Predict probability
        proba = self.model.predict_proba(X_latest)[0]
        prediction = self.model.predict(X_latest)[0]
        
        # Determine direction
        direction = 'UP' if prediction == 1 else 'DOWN'
        confidence = proba[prediction] * 100
        
        # Get feature importances
        importances = dict(zip(self.feature_columns, self.model.feature_importances_))
        top_features = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'pair': pair,
            'prediction': direction,
            'confidence': round(confidence, 2),
            'probability_up': round(proba[1] * 100, 2),
            'probability_down': round(proba[0] * 100, 2),
            'prediction_date': datetime.now().strftime('%Y-%m-%d'),
            'next_period': 'Daily',
            'top_features': top_features,
            'model_accuracy': round(self.model.score(
                df[self.feature_columns][-100:], 
                df['target'][-100:]
            ) * 100, 2) if len(df) >= 100 else None
        }
    
    def save_model(self):
        """Save trained model to disk."""
        if self.model is None:
            raise RuntimeError("No model to save")
        
        # Ensure instance directory exists
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        joblib.dump({
            'model': self.model,
            'feature_columns': self.feature_columns,
            'trained_date': datetime.now()
        }, self.model_path)
    
    def load_model(self):
        """Load trained model from disk."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        data = joblib.load(self.model_path)
        self.model = data['model']
        self.feature_columns = data['feature_columns']
        self.is_trained = True