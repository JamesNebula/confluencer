"""
Prediction routes for ML-based market direction forecasting.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.forms import PredictionForm
from app.ml.prediction_model import ForexPredictor
import os


# Create blueprint
predictions_bp = Blueprint('predictions', __name__, url_prefix='/predictions')


@predictions_bp.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """
    ML prediction page.
    
    GET: Display prediction form
    POST: Process prediction request
    """
    form = PredictionForm()
    
    # Initialize predictor (will load saved model if exists)
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                             'instance', 'ml_model.pkl')
    predictor = ForexPredictor(model_path=model_path)
    
    prediction_result = None
    training_result = None
    
    if form.validate_on_submit():
        pair = form.currency_pair.data
        pred_type = form.prediction_type.data
        retrain = form.train_model.data
        
        try:
            # Retrain model if requested
            if retrain:
                flash('Training model on 4 years of historical data...', 'info')
                training_result = predictor.train(pair=pair, period='4y')
                flash(f"Model trained! Test accuracy: {training_result['test_accuracy']}%", 'success')
            
            # Get prediction
            prediction_result = predictor.predict(pair=pair)
            
            flash(f"Prediction generated for {pair} ({pred_type})", 'success')
            
        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
            return redirect(url_for('predictions.predict'))
    
    return render_template('predictions/predict.html',
                         title='Market Predictions',
                         form=form,
                         prediction=prediction_result,
                         training=training_result)