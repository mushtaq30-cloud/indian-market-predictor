"""
AI-powered stock analysis service
Analyzes scraped stocks with sentiment data and AI recommendations
"""

import logging
from typing import List, Dict, Any
import asyncio
from datetime import datetime

from .stock_scraper import get_top_trending_stocks
from .news_service import get_market_news
from .ai_service import analyze_with_ai
from ..analysis.sentiment import analyze_articles_sentiment, analyze_text_sentiment

logger = logging.getLogger(__name__)


async def analyze_stocks_with_sentiment_and_ai(stock_limit: int = 10) -> Dict[str, Any]:
    """
    Get trending stocks, analyze their sentiment from news, and generate AI recommendations
    
    Process:
    1. Scrape real-time trending stocks
    2. Fetch news for each stock
    3. Calculate sentiment for each stock
    4. Use AI to analyze and generate buy/sell recommendations
    5. Return structured recommendations
    """
    try:
        logger.info("🔍 Starting AI-powered stock analysis with real-time data")
        
        # Step 1: Get trending stocks from scraper
        stocks = await get_top_trending_stocks(limit=stock_limit)
        
        if not stocks:
            logger.warning("⚠️ No stocks found from scraper")
            return {
                "top_buys": [],
                "top_sells": [],
                "market_trend": "Neutral",
                "analysis_timestamp": datetime.now().isoformat(),
                "status": "No real-time data available"
            }
        
        logger.info(f"📊 Found {len(stocks)} trending stocks")
        
        # Step 2 & 3: Fetch news and analyze sentiment for each stock
        analyzed_stocks = []
        
        for stock in stocks:
            try:
                symbol = stock.get('symbol', 'UNKNOWN')
                name = stock.get('name', symbol)
                
                logger.info(f"📰 Analyzing sentiment for {name} ({symbol})")
                
                # Fetch news for this stock
                news_items = await get_market_news(query=f"{name} {symbol} stock", limit=5)
                
                # Analyze sentiment
                if news_items:
                    sentiment_analysis = analyze_articles_sentiment(news_items)
                    sentiment_score = sentiment_analysis.get('overall_score', 0)
                    sentiment_polarity = sentiment_analysis.get('overall_polarity', 'neutral')
                    confidence = sentiment_analysis.get('confidence', 0)
                else:
                    sentiment_score = 0
                    sentiment_polarity = 'neutral'
                    confidence = 0
                
                # Combine stock data with sentiment
                stock_with_sentiment = {
                    **stock,
                    "sentiment_score": sentiment_score,
                    "sentiment_polarity": sentiment_polarity,
                    "sentiment_confidence": confidence,
                    "news_count": len(news_items),
                    "recent_news": [
                        {
                            "title": n.get('title'),
                            "source": n.get('source'),
                            "published": str(n.get('published', ''))
                        }
                        for n in news_items[:3]
                    ]
                }
                
                analyzed_stocks.append(stock_with_sentiment)
                
            except Exception as e:
                logger.error(f"❌ Error analyzing {stock.get('name')}: {e}")
                # Still add the stock without sentiment data
                analyzed_stocks.append({
                    **stock,
                    "sentiment_score": 0,
                    "sentiment_polarity": "neutral",
                    "sentiment_confidence": 0,
                    "news_count": 0,
                    "recent_news": []
                })
        
        # Step 4: Use AI to generate recommendations
        logger.info("🤖 Generating AI-powered recommendations")
        
        buy_recommendations = []
        sell_recommendations = []
        hold_recommendations = []
        
        for stock in analyzed_stocks:
            try:
                # Prepare data for AI analysis
                stock_name = stock.get('name', stock.get('symbol', 'Unknown'))
                current_price = stock.get('price', 0)
                price_change = stock.get('change_percent', 0)
                sentiment_score = stock.get('sentiment_score', 0)
                sentiment_polarity = stock.get('sentiment_polarity', 'neutral')
                
                # Build context for AI analysis
                analysis_context = f"""
                Stock: {stock_name}
                Current Price: ₹{current_price}
                24h Change: {price_change}%
                Market Sentiment: {sentiment_polarity} (Score: {sentiment_score:.2f})
                News Articles Analyzed: {stock.get('news_count', 0)}
                """
                
                # Get AI recommendation
                ai_analysis = analyze_with_ai(
                    asset_name=stock_name,
                    current_price=current_price,
                    indicators={
                        "price_change": price_change,
                        "sentiment_score": sentiment_score,
                        "trend": "up" if price_change > 0 else "down" if price_change < 0 else "stable"
                    },
                    news_summary={
                        "sentiment": sentiment_polarity,
                        "sentiment_score": sentiment_score,
                        "article_count": stock.get('news_count', 0),
                        "trend": "bullish" if sentiment_score > 0.2 else "bearish" if sentiment_score < -0.2 else "neutral"
                    }
                )
                
                # Parse AI response to get recommendation
                recommendation = parse_ai_recommendation(ai_analysis)
                
                # Enhance recommendation with our data
                rec_data = {
                    "symbol": stock.get('symbol'),
                    "name": stock_name,
                    "current_price": current_price,
                    "price_change_24h": f"{price_change:+.1f}%",
                    "recommendation": recommendation.get('action'),
                    "confidence": recommendation.get('confidence', 75),
                    "target_price": recommendation.get('target_price', current_price),
                    "upside_potential": recommendation.get('upside_potential', 0),
                    "reason": recommendation.get('reason', ''),
                    "sentiment": sentiment_polarity,
                    "sentiment_score": sentiment_score,
                    "ai_analysis": recommendation.get('analysis', ''),
                    "risk_level": recommendation.get('risk', 'Medium'),
                }
                
                # Categorize recommendation
                if recommendation.get('action') == 'BUY':
                    buy_recommendations.append(rec_data)
                elif recommendation.get('action') == 'SELL':
                    sell_recommendations.append(rec_data)
                else:
                    hold_recommendations.append(rec_data)
                    
            except Exception as e:
                logger.error(f"❌ Error getting AI recommendation for {stock.get('name')}: {e}")
                # Create a basic recommendation from sentiment if AI fails
                basic_rec = create_basic_recommendation(stock)
                if basic_rec.get('recommendation') == 'BUY':
                    buy_recommendations.append(basic_rec)
                elif basic_rec.get('recommendation') == 'SELL':
                    sell_recommendations.append(basic_rec)
                else:
                    hold_recommendations.append(basic_rec)
        
        # Sort by confidence
        buy_recommendations.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        sell_recommendations.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # Determine overall market trend
        market_trend = determine_market_trend(
            buy_recommendations, 
            sell_recommendations, 
            hold_recommendations
        )
        
        result = {
            "top_buys": buy_recommendations[:5],
            "top_sells": sell_recommendations[:3],
            "holds": hold_recommendations[:5],
            "market_trend": market_trend,
            "total_stocks_analyzed": len(analyzed_stocks),
            "analysis_timestamp": datetime.now().isoformat(),
            "data_source": "Real-time scraper + News sentiment + AI analysis",
            "update_frequency": "Hourly",
            "next_update": "Typically within 60 minutes"
        }
        
        logger.info(f"✅ Stock analysis complete: {len(buy_recommendations)} BUYs, {len(sell_recommendations)} SELLs")
        return result
        
    except Exception as e:
        logger.error(f"❌ Critical error in stock analysis: {e}", exc_info=True)
        return {
            "top_buys": [],
            "top_sells": [],
            "holds": [],
            "market_trend": "Neutral",
            "error": str(e),
            "analysis_timestamp": datetime.now().isoformat()
        }


def parse_ai_recommendation(ai_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse AI analysis to extract recommendation details
    """
    try:
        action = ai_response.get('recommendation', 'HOLD').upper()
        
        # Map AI recommendation to action
        if 'buy' in action.lower():
            action = 'BUY'
        elif 'sell' in action.lower():
            action = 'SELL'
        else:
            action = 'HOLD'
        
        return {
            'action': action,
            'confidence': ai_response.get('confidence', 75),
            'target_price': ai_response.get('target_price', 0),
            'upside_potential': ai_response.get('upside_potential', 0),
            'reason': ai_response.get('analysis_summary', ai_response.get('reason', '')),
            'analysis': ai_response.get('detailed_analysis', ''),
            'risk': ai_response.get('risk_level', 'Medium')
        }
    except Exception as e:
        logger.error(f"Error parsing AI recommendation: {e}")
        return {
            'action': 'HOLD',
            'confidence': 50,
            'target_price': 0,
            'upside_potential': 0,
            'reason': 'Unable to generate recommendation',
            'analysis': '',
            'risk': 'Unknown'
        }


def create_basic_recommendation(stock: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a basic recommendation if AI analysis fails
    Uses sentiment and price action
    """
    price_change = stock.get('change_percent', 0)
    sentiment_score = stock.get('sentiment_score', 0)
    
    # Determine action based on sentiment and price
    if sentiment_score > 0.3 and price_change > 1:
        action = 'BUY'
        confidence = min(85, 50 + abs(sentiment_score) * 100)
    elif sentiment_score < -0.3 and price_change < -1:
        action = 'SELL'
        confidence = min(80, 50 + abs(sentiment_score) * 100)
    else:
        action = 'HOLD'
        confidence = 60
    
    return {
        "symbol": stock.get('symbol'),
        "name": stock.get('name'),
        "current_price": stock.get('price', 0),
        "price_change_24h": f"{price_change:+.1f}%",
        "recommendation": action,
        "confidence": int(confidence),
        "target_price": stock.get('price', 0) * (1 + sentiment_score * 0.05),
        "upside_potential": sentiment_score * 100,
        "reason": f"Based on {stock.get('sentiment_polarity')} sentiment and {price_change:+.1f}% price change",
        "sentiment": stock.get('sentiment_polarity', 'neutral'),
        "sentiment_score": sentiment_score,
        "ai_analysis": "Sentiment-based analysis",
        "risk_level": "Medium"
    }


def determine_market_trend(buys: List[Dict], sells: List[Dict], holds: List[Dict]) -> str:
    """
    Determine overall market trend based on recommendations
    """
    total = len(buys) + len(sells) + len(holds)
    
    if total == 0:
        return "Neutral"
    
    buy_ratio = len(buys) / total
    sell_ratio = len(sells) / total
    
    if buy_ratio > 0.5:
        return "Strong Bullish"
    elif buy_ratio > 0.35:
        return "Bullish"
    elif sell_ratio > 0.5:
        return "Strong Bearish"
    elif sell_ratio > 0.35:
        return "Bearish"
    else:
        return "Neutral"
