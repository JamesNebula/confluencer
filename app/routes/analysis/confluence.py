"""
Confluence analysis routes for technical analysis scoring.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
import json
from flask_login import login_required, current_user
from app import db
from app.forms import ConfluenceAnalysisForm
from app.models import AnalysisSession
from app.utils.confluence_engine import (
    calculate_confluence_score,
    Direction, PatternType, SupportResistance, EMAStatus
)

# Create blueprint
confluence_bp = Blueprint('analysis', __name__, url_prefix='/analysis')


@confluence_bp.route('/confluence', methods=['GET', 'POST'])
@login_required
def confluence():
    """
    Confluence analysis page.
    
    GET: Display analysis form
    POST: Process analysis and show results
    """
    form = ConfluenceAnalysisForm()
    
    if form.validate_on_submit():
        # Convert form data to enum types for scoring engine
        timeframe_dir = Direction(form.timeframe_direction.data)
        pattern = PatternType(form.pattern.data)
        sr_position = SupportResistance(form.support_resistance.data)
        ema_status = EMAStatus(form.ema_status.data)
        has_volume = form.volume_confirmation.data
        
        # Calculate confluence score
        result = calculate_confluence_score(
            timeframe_dir=timeframe_dir,
            pattern=pattern,
            sr_position=sr_position,
            ema_status=ema_status,
            has_volume=has_volume
        )
        
        # Save analysis session to database
        analysis_session = AnalysisSession(
            user_id=current_user.id,
            currency_pair=form.currency_pair.data,
            timeframe=form.timeframe.data,
            confluence_data=json.dumps({
                'timeframe_direction': form.timeframe_direction.data,
                'pattern': form.pattern.data,
                'support_resistance': form.support_resistance.data,
                'ema_status': form.ema_status.data,
                'volume_confirmation': has_volume,
                'notes': form.notes.data
            }),
            recommendation=result['recommendation'],
            confidence_score=result['confidence_percentage']
        )
        
        db.session.add(analysis_session)
        db.session.commit()
        
        # Store result in session or pass to template
        return render_template('analysis/confluence.html',
                             title='Confluence Analysis',
                             form=form,
                             result=result,
                             analysis_id=analysis_session.id)
    
    # GET request - show empty form
    return render_template('analysis/confluence.html',
                         title='Confluence Analysis',
                         form=form)


@confluence_bp.route('/analysis-history')
@login_required
def analysis_history():
    """
    View historical analysis sessions.
    """
    page = request.args.get('page', 1, type=int)
    
    analyses = AnalysisSession.query.filter_by(
        user_id=current_user.id
    ).order_by(
        AnalysisSession.created_at.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('analysis/history.html',
                         title='Analysis History',
                         analyses=analyses)