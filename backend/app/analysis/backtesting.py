import pandas as pd
from datetime import datetime, timedelta
from ..services import gold_service, stock_service, news_service
from .predictor import predict_trend_with_news
import logging

logger = logging.getLogger(__name__)

async def run_backtest(asset_type: str, days: int = 30):
    """
    Backtest prediction accuracy - FIXED VERSION
    """
    logger.info(f"Starting backtest for {asset_type} over {days} days...")
    
    results = []
    correct = 0
    total = 0
    cumulative_return = 0
    
    try:
        # Fetch historical data
        if asset_type.lower() == 'gold':
            historical_data = await gold_service.fetch_gold_history(days=days+90)
            compute_func = gold_service.compute_indicators
            price_col = 'price_inr'
        else:
            historical_data = await stock_service.fetch_stock_history(asset_type, days=days+90)
            compute_func = stock_service.compute_indicators
            price_col = 'close'
        
        if historical_data.empty or len(historical_data) < days + 1:
            return {
                "error": "Insufficient historical data",
                "accuracy": 0,
                "total": 0,
                "correct": 0,
                "profit_loss": 0,
                "daily_results": []
            }
        
        # Simulate day-by-day predictions
        for i in range(len(historical_data) - days - 1, len(historical_data) - 1):
            # Use data up to day i
            current_data = historical_data.iloc[:i+1].copy()
            
            # Compute indicators
            indicators = compute_func(current_data)
            
            # Simplified news sentiment (historical news not available)
            mock_news_impact = {
                'impact_score': 0,
                'sentiment': {
                    'confidence': 50,
                    'label': 'neutral',
                    'article_count': 0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0
                },
                'events': []
            }
            
            # Make prediction
            prediction = predict_trend_with_news(indicators, mock_news_impact)
            
            # Check actual next-day movement
            current_price = historical_data.iloc[i][price_col]
            next_price = historical_data.iloc[i+1][price_col]
            
            actual_change = (next_price - current_price) / current_price
            
            # Compare prediction vs actual
            predicted_direction = prediction['direction']
            
            is_correct = False
            if predicted_direction == 'bullish' and actual_change > 0:
                is_correct = True
                cumulative_return += actual_change
            elif predicted_direction == 'bearish' and actual_change < 0:
                is_correct = True
                cumulative_return += abs(actual_change)
            elif predicted_direction == 'neutral':
                # Neutral doesn't count toward accuracy
                continue
            
            if is_correct:
                correct += 1
            
            total += 1
            
            results.append({
                'date': str(historical_data.iloc[i]['date']),
                'prediction': predicted_direction,
                'confidence': prediction['confidence'],
                'actual_change': round(actual_change * 100, 2),
                'correct': is_correct
            })
        
        accuracy = (correct / total * 100) if total > 0 else 0
        
        logger.info(f"Backtest complete: {accuracy:.1f}% accuracy over {total} predictions")
        
        return {
            "accuracy": round(accuracy, 1),
            "total": total,
            "correct": correct,
            "profit_loss": round(cumulative_return * 100, 2),
            "daily_results": results[-10:]  # Last 10 days
        }
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        return {
            "error": str(e),
            "accuracy": 0,
            "total": 0,
            "correct": 0,
            "profit_loss": 0,
            "daily_results": []
        }
