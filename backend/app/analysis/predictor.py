import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import logging

logger = logging.getLogger(__name__)

def predict_trend_with_news(indicators: dict, news_impact: dict):
    """
    Enhanced prediction combining technical analysis + comprehensive news
    Weighting: 40% technical + 60% news
    """
    
    # === TECHNICAL ANALYSIS (40% weight) ===
    price = indicators.get("latest_price", 0)
    ma_20 = indicators.get("ma_20", price)
    ma_50 = indicators.get("ma_50", price)
    rsi = indicators.get("rsi", 50)
    recent_return = indicators.get("recent_return_20d", 0)
    volatility = indicators.get("volatility", 0)
    
    # MA trend score
    ma_score = 0
    if ma_20 and price:
        ma_score = (price - ma_20) / ma_20 * 5
        ma_score = max(-1, min(1, ma_score))
    
    # RSI score (contrarian)
    rsi_score = 0
    if rsi:
        if rsi > 70:
            rsi_score = -0.4  # Overbought -> bearish
        elif rsi < 30:
            rsi_score = 0.4   # Oversold -> bullish
        else:
            rsi_score = (50 - rsi) / 50 * 0.3  # Slight mean reversion
    
    # Momentum score
    return_score = max(-1, min(1, recent_return * 10))
    
    # Combine technical signals
    technical_score = (
        0.40 * ma_score +
        0.25 * rsi_score +
        0.35 * return_score
    )
    
    # === NEWS ANALYSIS (60% weight) ===
    news_score = news_impact['impact_score']
    news_confidence = news_impact['sentiment']['confidence'] / 100
    events = news_impact['events']
    
    # Critical events amplification
    critical_event_types = ['Rbi Policy', 'Budget', 'Inflation']
    critical_events = [e for e in events if any(et in e['type'] for et in critical_event_types)]
    event_multiplier = 1 + (len(critical_events) * 0.25)
    
    # === COMBINED SCORE ===
    trend_score = (
        0.40 * technical_score +
        0.60 * news_score * event_multiplier
    )
    
    # === DIRECTION & CONFIDENCE ===
    # Lower thresholds for more decisive predictions (not too neutral)
    if trend_score > 0.05:
        direction = "bullish"
        base_confidence = 70
    elif trend_score < -0.05:
        direction = "bearish"
        base_confidence = 70
    else:
        direction = "neutral"
        base_confidence = 55  # Higher base for neutral
    
    # Boost confidence with high news agreement
    confidence_boost = news_confidence * 30  # Increased from 20
    
    # Reduce confidence in high volatility (but not too much)
    volatility_penalty = 0
    if volatility and volatility > 0.05:
        volatility_penalty = 5  # Reduced from 10
    
    final_confidence = min(92, max(30, base_confidence + confidence_boost - volatility_penalty))
    
    # === KEY DRIVERS ===
    drivers = []
    
    # Add critical events first
    for event in critical_events[:2]:
        drivers.append(f"📰 {event['type']}: {event['title'][:65]}...")
    
    # Add sentiment
    sentiment = news_impact['sentiment']
    drivers.append(
        f"📊 {sentiment['label'].title()} sentiment: "
        f"{sentiment['positive_count']}✓ {sentiment['negative_count']}✗ "
        f"across {sentiment['article_count']} sources"
    )
    
    # Add technical signals
    if abs(ma_score) > 0.3:
        direction_text = "above" if ma_score > 0 else "below"
        drivers.append(f"📈 Price {direction_text} 20-day MA (trend: {ma_score:+.2f})")
    
    if rsi and (rsi > 70 or rsi < 30):
        condition = "overbought" if rsi > 70 else "oversold"
        drivers.append(f"📉 RSI at {rsi:.1f} ({condition})")
    
    if abs(return_score) > 0.3:
        momentum = "upward" if return_score > 0 else "downward"
        drivers.append(f"🎯 Strong {momentum} momentum ({recent_return:+.2%})")
    
    # Add volatility warning
    if volatility and volatility > 0.03:
        drivers.append(f"⚠️ High volatility detected ({volatility:.2%})")
    
    logger.info(
        f"Prediction: {direction.upper()} | "
        f"Confidence: {final_confidence:.1f}% | "
        f"Score: {trend_score:+.3f} | "
        f"Tech: {technical_score:+.3f} | News: {news_score:+.3f}"
    )
    
    return {
        "direction": direction,
        "confidence": round(final_confidence, 1),
        "trend_score": round(trend_score, 3),
        "drivers": drivers[:6],  # Top 6 drivers
        "technical_contribution": round(technical_score * 0.4, 3),
        "news_contribution": round(news_score * 0.6, 3),
        "critical_events_count": len(critical_events),
        "news_confidence": round(news_confidence * 100, 1)
    }
