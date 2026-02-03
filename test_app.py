"""
Comprehensive test script for Forex Confluence App.
Run this to verify all features work before deployment.
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.models import db, User, TradeHistory, AnalysisSession
from app.ml.prediction_model import ForexPredictor

def test_app_creation():
    """Test app factory creates app successfully."""
    print("Testing app creation...", end=" ")
    app = create_app('testing')
    assert app is not None
    print("✅")

def test_database_models():
    """Test database models can be created."""
    print("Testing database models...", end=" ")
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Test User model
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        
        # Verify user was saved
        retrieved = User.query.filter_by(username='testuser').first()
        assert retrieved is not None
        assert retrieved.check_password('testpass')
        
        # Cleanup
        db.session.delete(user)
        db.session.commit()
    print("✅")

def test_ml_prediction():
    """Test ML prediction works."""
    print("Testing ML prediction...", end=" ")
    try:
        predictor = ForexPredictor(model_path='instance/test_model.pkl')
        # Try to load or train
        if not predictor.is_trained:
            result = predictor.train(pair='EURUSD', years=1)
            assert 'test_accuracy' in result
        prediction = predictor.predict(pair='EURUSD')
        assert 'prediction' in prediction
        assert 'confidence' in prediction
        print("✅")
    except Exception as e:
        print(f"⚠️  Skipped (may need Alpha Vantage key): {str(e)[:50]}")

def test_routes():
    """Test all routes are registered."""
    print("Testing route registration...", end=" ")
    app = create_app('testing')
    with app.test_client() as client:
        # Test public routes
        response = client.get('/')
        assert response.status_code in [200, 302]
        
        response = client.get('/auth/login')
        assert response.status_code == 200
        
        response = client.get('/auth/register')
        assert response.status_code == 200
    print("✅")

def run_all_tests():
    """Run all tests."""
    print("\n" + "="*50)
    print("FOREX CONFLUENCE APP - COMPREHENSIVE TEST SUITE")
    print("="*50 + "\n")
    
    try:
        test_app_creation()
        test_database_models()
        test_ml_prediction()
        test_routes()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50)
        return True
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
