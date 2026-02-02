"""
Confluence analysis engine for technical analysis scoring.

This module implements a weighted scoring system that combines multiple
technical analysis factors to provide trading recommendations.
"""
import json
from enum import Enum
from typing import Dict, Tuple, Optional


class Timeframe(Enum):
    """Supported timeframes for analysis."""
    FOUR_HOUR = '4H'
    DAILY = 'D'
    WEEKLY = 'W'


class Direction(Enum):
    """Market direction."""
    BULLISH = 'bullish'
    BEARISH = 'bearish'
    NEUTRAL = 'neutral'


class PatternType(Enum):
    """Chart pattern types."""
    HEAD_SHOULDERS = 'head_shoulders'
    INVERSE_HEAD_SHOULDERS = 'inverse_head_shoulders'
    ENGULFING = 'engulfing_bullish'
    ENGULFING_BEARISH = 'engulfing_bearish'
    NONE = 'none'


class SupportResistance(Enum):
    """Price position relative to S/R levels."""
    AT_RESISTANCE = 'at_resistance'
    AT_SUPPORT = 'at_support'
    NEUTRAL = 'neutral'


class EMAStatus(Enum):
    """Price position relative to EMA."""
    TESTING_EMA = 'testing_ema'
    ABOVE_EMA = 'above_ema'
    BELOW_EMA = 'below_ema'
    NEUTRAL = 'neutral'


# Weighted confluence factors
# Higher weight = more important factor
CONFLUENCE_WEIGHTS = {
    'timeframe_alignment': 0.30,  # 30% weight - most important
    'pattern_confirmation': 0.25,  # 25% weight
    'support_resistance': 0.20,  # 20% weight
    'ema_alignment': 0.15,  # 15% weight
    'volume_confirmation': 0.10,  # 10% weight
}


def calculate_timeframe_score(timeframe_dir: Direction) -> Tuple[float, str]:
    """
    Calculate score for timeframe alignment.
    
    Args:
        timeframe_dir: Market direction on selected timeframe
        
    Returns:
        Tuple of (score, explanation)
    """
    if timeframe_dir == Direction.BULLISH:
        return 1.0, "Bullish timeframe alignment"
    elif timeframe_dir == Direction.BEARISH:
        return 0.0, "Bearish timeframe alignment"
    else:
        return 0.5, "Neutral timeframe"


def calculate_pattern_score(pattern: PatternType) -> Tuple[float, str]:
    """
    Calculate score for pattern confirmation.
    
    Args:
        pattern: Identified chart pattern
        
    Returns:
        Tuple of (score, explanation)
    """
    pattern_scores = {
        PatternType.HEAD_SHOULDERS: 0.1,  # Bearish pattern
        PatternType.INVERSE_HEAD_SHOULDERS: 0.9,  # Bullish pattern
        PatternType.ENGULFING: 0.85,  # Bullish engulfing
        PatternType.ENGULFING_BEARISH: 0.15,  # Bearish engulfing
        PatternType.NONE: 0.5,  # No pattern
    }
    explanations = {
        PatternType.HEAD_SHOULDERS: "Head & Shoulders (bearish)",
        PatternType.INVERSE_HEAD_SHOULDERS: "Inverse H&S (bullish)",
        PatternType.ENGULFING: "Bullish engulfing pattern",
        PatternType.ENGULFING_BEARISH: "Bearish engulfing pattern",
        PatternType.NONE: "No significant pattern",
    }
    return pattern_scores[pattern], explanations[pattern]


def calculate_sr_score(sr_position: SupportResistance) -> Tuple[float, str]:
    """
    Calculate score for support/resistance position.
    
    Args:
        sr_position: Price position relative to S/R
        
    Returns:
        Tuple of (score, explanation)
    """
    if sr_position == SupportResistance.AT_SUPPORT:
        return 0.8, "Price at support level (bullish)"
    elif sr_position == SupportResistance.AT_RESISTANCE:
        return 0.2, "Price at resistance level (bearish)"
    else:
        return 0.5, "Neutral S/R position"


def calculate_ema_score(ema_status: EMAStatus) -> Tuple[float, str]:
    """
    Calculate score for EMA alignment.
    
    Args:
        ema_status: Price position relative to EMA
        
    Returns:
        Tuple of (score, explanation)
    """
    if ema_status == EMAStatus.ABOVE_EMA:
        return 0.7, "Price above EMA (bullish)"
    elif ema_status == EMAStatus.BELOW_EMA:
        return 0.3, "Price below EMA (bearish)"
    elif ema_status == EMAStatus.TESTING_EMA:
        return 0.6, "Price testing EMA (potential bounce)"
    else:
        return 0.5, "Neutral EMA position"


def calculate_volume_score(has_volume: bool) -> Tuple[float, str]:
    """
    Calculate score for volume confirmation.
    
    Args:
        has_volume: Whether volume confirms the setup
        
    Returns:
        Tuple of (score, explanation)
    """
    if has_volume:
        return 0.7, "Volume confirms setup"
    else:
        return 0.5, "No volume data"


def calculate_confluence_score(
    timeframe_dir: Direction,
    pattern: PatternType,
    sr_position: SupportResistance,
    ema_status: EMAStatus,
    has_volume: bool = False
) -> Dict:
    """
    Calculate overall confluence score based on multiple factors.
    
    Uses weighted scoring system where each factor contributes
    to the final recommendation.
    
    Args:
        timeframe_dir: Market direction on selected timeframe
        pattern: Identified chart pattern
        sr_position: Price position relative to support/resistance
        ema_status: Price position relative to EMA
        has_volume: Whether volume confirms the setup
        
    Returns:
        Dictionary with score, recommendation, and detailed breakdown
    """
    # Calculate individual factor scores
    timeframe_score, timeframe_exp = calculate_timeframe_score(timeframe_dir)
    pattern_score, pattern_exp = calculate_pattern_score(pattern)
    sr_score, sr_exp = calculate_sr_score(sr_position)
    ema_score, ema_exp = calculate_ema_score(ema_status)
    volume_score, volume_exp = calculate_volume_score(has_volume)
    
    # Apply weights
    weighted_scores = {
        'timeframe_alignment': {
            'raw_score': timeframe_score,
            'weighted_score': timeframe_score * CONFLUENCE_WEIGHTS['timeframe_alignment'],
            'explanation': timeframe_exp,
            'weight': CONFLUENCE_WEIGHTS['timeframe_alignment']
        },
        'pattern_confirmation': {
            'raw_score': pattern_score,
            'weighted_score': pattern_score * CONFLUENCE_WEIGHTS['pattern_confirmation'],
            'explanation': pattern_exp,
            'weight': CONFLUENCE_WEIGHTS['pattern_confirmation']
        },
        'support_resistance': {
            'raw_score': sr_score,
            'weighted_score': sr_score * CONFLUENCE_WEIGHTS['support_resistance'],
            'explanation': sr_exp,
            'weight': CONFLUENCE_WEIGHTS['support_resistance']
        },
        'ema_alignment': {
            'raw_score': ema_score,
            'weighted_score': ema_score * CONFLUENCE_WEIGHTS['ema_alignment'],
            'explanation': ema_exp,
            'weight': CONFLUENCE_WEIGHTS['ema_alignment']
        },
        'volume_confirmation': {
            'raw_score': volume_score,
            'weighted_score': volume_score * CONFLUENCE_WEIGHTS['volume_confirmation'],
            'explanation': volume_exp,
            'weight': CONFLUENCE_WEIGHTS['volume_confirmation']
        }
    }
    
    # Calculate total weighted score (0-1 range)
    total_score = sum(factor['weighted_score'] for factor in weighted_scores.values())
    
    # Convert to percentage (0-100)
    confidence_percentage = round(total_score * 100, 1)
    
    # Determine recommendation based on score
    if total_score >= 0.7:
        recommendation = 'BUY'
        recommendation_text = 'Strong Buy Signal'
    elif total_score >= 0.6:
        recommendation = 'BUY'
        recommendation_text = 'Buy Signal'
    elif total_score >= 0.4:
        recommendation = 'HOLD'
        recommendation_text = 'Neutral / Wait'
    elif total_score >= 0.3:
        recommendation = 'SELL'
        recommendation_text = 'Sell Signal'
    else:
        recommendation = 'SELL'
        recommendation_text = 'Strong Sell Signal'
    
    # Calculate strength indicators
    strength = 'Strong' if confidence_percentage >= 70 else \
               'Moderate' if confidence_percentage >= 50 else 'Weak'
    
    return {
        'total_score': total_score,
        'confidence_percentage': confidence_percentage,
        'recommendation': recommendation,
        'recommendation_text': recommendation_text,
        'strength': strength,
        'factors': weighted_scores,
        'summary': f"{recommendation} ({confidence_percentage}%) - {strength} signal"
    }


def get_signal_color(confidence: float, recommendation: str) -> str:
    """
    Get color code for signal visualization.
    
    Args:
        confidence: Confidence percentage (0-100)
        recommendation: 'BUY', 'SELL', or 'HOLD'
        
    Returns:
        Color class name for Bootstrap
    """
    if recommendation == 'HOLD':
        return 'warning'
    elif confidence >= 70:
        return 'success' if recommendation == 'BUY' else 'danger'
    elif confidence >= 50:
        return 'info' if recommendation == 'BUY' else 'secondary'
    else:
        return 'secondary'


def get_signal_icon(recommendation: str) -> str:
    """
    Get icon for signal type.
    
    Args:
        recommendation: 'BUY', 'SELL', or 'HOLD'
        
    Returns:
        Font Awesome icon class
    """
    icons = {
        'BUY': 'fa-arrow-up',
        'SELL': 'fa-arrow-down',
        'HOLD': 'fa-minus'
    }
    return icons.get(recommendation, 'fa-minus')