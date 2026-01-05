from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .services import (
    gold_service,
    silver_service,
    stock_service,
    stock_recommendations,
    news_service,
    ai_service,
    chatbot_service
)

from .analysis.predictor import predict_trend_with_news
from .analysis.backtesting import run_backtest
from .models.schemas import (
    DashboardResponse,
    PredictionResponse,
    MarketOverviewResponse,
    ChatbotRequest,
    ChatbotResponse
)

import logging
import pandas as pd
import numpy as np
import asyncio


# ==================================================================
# Logging
# ==================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.main")


# ==================================================================
# FastAPI App
# ==================================================================
app = FastAPI(
    title="AI-Powered Indian Market Predictor",
    description="Real-time AI market analysis for Indian Gold, Silver & Stocks",
    version="2.0.0"
)


# ==================================================================
# CORS
# ==================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================================
# ROOT / HEALTH
# ==================================================================
@app.get("/")
def root():
    return {
        "message": "AI-Powered Indian Market Predictor API",
        "version": "2.0.0",
        "status": "running",
        "ai_provider": settings.AI_PROVIDER
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "ai_configured": bool(settings.GROQ_API_KEY or settings.GEMINI_API_KEY)
    }


# ==================================================================
# HELPER FUNCTIONS
# ==================================================================
def calculate_tomorrow_price(current_price: float, prediction: str, confidence: float = 50, volatility: float = 0.01) -> float:
    """Calculate predicted price for tomorrow based on trend and confidence"""
    try:
        if not current_price or current_price == 0:
            return current_price
            
        if not prediction:
            return current_price
            
        prediction_upper = str(prediction).upper().strip()
        confidence_multiplier = max(0.5, min(1.5, confidence / 50))  # 30% → 0.6x, 90% → 1.8x
        
        if "BULL" in prediction_upper:
            # Bullish: price up by (1.5-2.5)% based on confidence
            change_pct = (0.015 + volatility * 0.5) * confidence_multiplier
        elif "BEAR" in prediction_upper:
            # Bearish: price down by (1.5-2.5)% based on confidence
            change_pct = -(0.015 + volatility * 0.5) * confidence_multiplier
        else:
            # Neutral: random ±0.5% movement
            change_pct = np.random.uniform(-0.005, 0.005)
        
        tomorrow_price = current_price * (1 + change_pct)
        return round(tomorrow_price, 2)
    except Exception as e:
        logger.error(f"Error calculating tomorrow price: {e}, returning current price")
        return current_price


# ==================================================================
# DASHBOARD
# ==================================================================
@app.get("/dashboard", response_model=DashboardResponse)
async def dashboard():
    try:
        logger.info("Dashboard → fetching data")

        # Parallelize ALL async operations for speed
        (gold, silver, nifty, sensex, 
         business_news, gold_news, silver_news) = await asyncio.gather(
            gold_service.fetch_current_gold_price(),
            silver_service.fetch_current_silver_price(),
            stock_service.fetch_current_price("^NSEI"),
            stock_service.fetch_current_price("^BSESN"),
            news_service.fetch_india_business_news(limit=20),
            news_service.fetch_gold_news_india(limit=15),
            news_service.fetch_multi_source_news("silver", 48, 15)
        )

        # Fetch history with already-fetched prices (no double fetching)
        try:
            gold_history, silver_history = await asyncio.gather(
                gold_service.fetch_gold_history(30, current_price=gold["price"]),
                silver_service.fetch_silver_history(30, current_price=silver["price"])
            )
            logger.info(f"✅ History fetched - Gold: {gold_history.shape if not gold_history.empty else 'empty'}, Silver: {silver_history.shape if not silver_history.empty else 'empty'}")
        except Exception as e:
            logger.error(f"❌ Error fetching history: {e}", exc_info=True)
            raise

        # Compute indicators
        try:
            gold_indicators = gold_service.compute_indicators(gold_history)
            silver_indicators = silver_service.compute_indicators(silver_history)
            logger.info("✅ Indicators computed")
        except Exception as e:
            logger.error(f"❌ Error computing indicators: {e}", exc_info=True)
            raise

        # Process news for sentiment
        try:
            all_news = business_news + gold_news + silver_news
            sentiment = news_service.compute_sentiment(all_news)
            logger.info("✅ Sentiment computed")
        except Exception as e:
            logger.error(f"❌ Error computing sentiment: {e}", exc_info=True)
            raise

        # AI market summary
        try:
            ai_insights = ai_service.generate_market_insights(
                gold_data=gold,
                silver_data=silver,
                stock_indices={"nifty": nifty, "sensex": sensex},
                news_headlines=all_news[:20]
            )
            logger.info("✅ AI insights generated")
        except Exception as e:
            logger.error(f"❌ Error generating AI insights: {e}", exc_info=True)
            raise

        # Quick predictions using already-fetched data
        try:
            gold_news_impact = news_service.get_news_impact_score(gold_news, asset_type="gold")
            silver_news_impact = news_service.get_news_impact_score(silver_news, asset_type="silver")
            
            gold_prediction = predict_trend_with_news(gold_indicators, gold_news_impact)
            silver_prediction = predict_trend_with_news(silver_indicators, silver_news_impact)
            logger.info("✅ Predictions generated")
            
            # Get AI analysis for both assets
            gold_ai = ai_service.analyze_with_ai(
                "Gold (India)",
                gold_indicators["latest_price"],
                gold_indicators,
                gold_news_impact["sentiment"]
            )
            silver_ai = ai_service.analyze_with_ai(
                "Silver (India)",
                silver_indicators["latest_price"],
                silver_indicators,
                silver_news_impact["sentiment"]
            )
            logger.info("✅ AI analysis generated")
        except Exception as e:
            logger.error(f"❌ Error generating predictions/AI: {e}", exc_info=True)
            raise

        # Calculate tomorrow's predicted prices
        try:
            gold_tomorrow = calculate_tomorrow_price(
                gold["price"], 
                gold_prediction["direction"],
                gold_prediction["confidence"],
                gold_indicators.get("volatility", 0.008)
            )
            silver_tomorrow = calculate_tomorrow_price(
                silver["price"], 
                silver_prediction["direction"],
                silver_prediction["confidence"],
                silver_indicators.get("volatility", 0.012)
            )
            logger.info(f"✅ Tomorrow prices calculated: Gold={gold_tomorrow} ({gold_prediction['direction']}, {gold_prediction['confidence']}% conf), Silver={silver_tomorrow} ({silver_prediction['direction']}, {silver_prediction['confidence']}% conf)")
        except Exception as e:
            logger.error(f"❌ Error calculating tomorrow prices: {e}", exc_info=True)
            raise

        # Convert history to JSON-serializable format
        gold_history_records = []
        if not gold_history.empty:
            try:
                for idx, row in gold_history.iterrows():
                    # Ensure proper datetime handling
                    date_val = row['date']
                    if hasattr(date_val, 'isoformat'):
                        date_str = date_val.isoformat()
                    else:
                        date_str = pd.Timestamp(date_val).isoformat()
                    
                    price = float(row['price_inr']) if row['price_inr'] is not None else gold["price"]
                    gold_history_records.append({
                        "date": date_str,
                        "price_inr": price
                    })
                logger.info(f"✅ Converted {len(gold_history_records)} gold history records")
            except Exception as e:
                logger.error(f"Error converting gold history: {e}", exc_info=True)
                logger.info(f"Gold history info - Columns: {gold_history.columns.tolist()}, Shape: {gold_history.shape}")
                logger.info(f"Gold history dtypes:\n{gold_history.dtypes}")
                raise
        
        silver_history_records = []
        if not silver_history.empty:
            try:
                for idx, row in silver_history.iterrows():
                    # Ensure proper datetime handling
                    date_val = row['date']
                    if hasattr(date_val, 'isoformat'):
                        date_str = date_val.isoformat()
                    else:
                        date_str = pd.Timestamp(date_val).isoformat()
                    
                    price = float(row['price_inr']) if row['price_inr'] is not None else silver["price"]
                    silver_history_records.append({
                        "date": date_str,
                        "price_inr": price
                    })
                logger.info(f"✅ Converted {len(silver_history_records)} silver history records")
            except Exception as e:
                logger.error(f"Error converting silver history: {e}", exc_info=True)
                logger.info(f"Silver history info - Columns: {silver_history.columns.tolist()}, Shape: {silver_history.shape}")
                logger.info(f"Silver history dtypes:\n{silver_history.dtypes}")
                raise

        logger.info(f"Gold tomorrow: ₹{gold_tomorrow}, Silver tomorrow: ₹{silver_tomorrow}")
        logger.info(f"Final dashboard - Gold history: {len(gold_history_records)} records, Silver history: {len(silver_history_records)} records")

        # Build response
        try:
            response_data = {
                "gold": {
                    "price": gold["price"],
                    "unit": gold["unit"],
                    "prediction": gold_prediction["direction"],
                    "confidence": gold_prediction["confidence"],
                    "tomorrow_price": gold_tomorrow,
                    "history": gold_history_records,
                    "ai_analysis": gold_ai,
                    "prediction_drivers": gold_prediction.get("drivers", [])
                },
                "silver": {
                    "price": silver["price"],
                    "unit": silver["unit"],
                    "prediction": silver_prediction["direction"],
                    "confidence": silver_prediction["confidence"],
                    "tomorrow_price": silver_tomorrow,
                    "history": silver_history_records,
                    "ai_analysis": silver_ai,
                    "prediction_drivers": silver_prediction.get("drivers", [])
                },
                "nifty": nifty,
                "sensex": sensex,
                "market_sentiment": sentiment,
                "ai_insights": ai_insights,
                "top_news": [
                    {
                        "title": n.get("title"),
                        "source": n.get("source"),
                        "link": n.get("link"),
                        "published": str(n.get("published"))
                    }
                    for n in all_news[:10]
                ],
                "top_stocks": stock_recommendations.get_top_stock_picks(),
                "top_mutual_funds": stock_recommendations.get_top_mutual_funds(),
                "last_updated": pd.Timestamp.now().isoformat()
            }
            logger.info("✅ Dashboard response built successfully")
            logger.info(f"Response includes: Gold history={len(response_data['gold']['history'])}, Silver history={len(response_data['silver']['history'])}")
            return response_data
        except Exception as e:
            logger.error(f"❌ Error building response: {e}", exc_info=True)
            raise

    except Exception as e:
        logger.error(f"Dashboard Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug/history")
async def debug_history():
    """Debug endpoint to check history generation"""
    try:
        # Fetch gold price
        gold_price = await gold_service.fetch_current_gold_price()
        
        # Fetch history with current price
        gold_history = await gold_service.fetch_gold_history(10, current_price=gold_price["price"])
        
        # Check what we have
        history_dict = gold_history.to_dict('records')
        
        return {
            "current_price": gold_price["price"],
            "history_shape": str(gold_history.shape),
            "history_columns": gold_history.columns.tolist(),
            "sample_records": history_dict[:3] if history_dict else [],
            "total_records": len(history_dict),
            "first_date": str(gold_history.iloc[0]['date']) if len(gold_history) > 0 else None,
            "last_date": str(gold_history.iloc[-1]['date']) if len(gold_history) > 0 else None,
        }
    except Exception as e:
        logger.error(f"Debug error: {e}", exc_info=True)
        return {"error": str(e)}


@app.get("/debug/dashboard-simple")
async def debug_dashboard_simple():
    """Simplified dashboard debug - returns only essential data"""
    try:
        logger.info("Debug dashboard → fetching data")

        # Get prices
        gold = await gold_service.fetch_current_gold_price()
        silver = await silver_service.fetch_current_silver_price()
        
        logger.info(f"Prices fetched - Gold: {gold['price']}, Silver: {silver['price']}")
        
        # Get history
        gold_history = await gold_service.fetch_gold_history(30, current_price=gold["price"])
        silver_history = await silver_service.fetch_silver_history(30, current_price=silver["price"])
        
        logger.info(f"History fetched - Gold shape: {gold_history.shape}, Silver shape: {silver_history.shape}")
        
        # Convert history
        gold_history_records = []
        if not gold_history.empty:
            for idx, row in gold_history.iterrows():
                date_val = row['date']
                if hasattr(date_val, 'isoformat'):
                    date_str = date_val.isoformat()
                else:
                    date_str = pd.Timestamp(date_val).isoformat()
                gold_history_records.append({
                    "date": date_str,
                    "price_inr": float(row['price_inr'])
                })
        
        logger.info(f"Converted {len(gold_history_records)} gold records")
        
        return {
            "status": "success",
            "gold": {
                "price": gold["price"],
                "history_count": len(gold_history_records),
                "history_sample": gold_history_records[:2]
            },
            "silver": {
                "price": silver["price"],
                "history_count": len(silver_history)
            }
        }
    except Exception as e:
        logger.error(f"Debug dashboard error: {e}", exc_info=True)
        return {"status": "error", "error": str(e), "error_type": type(e).__name__}


# ==================================================================
# GOLD ANALYSIS
# ==================================================================
@app.get("/gold/analysis", response_model=PredictionResponse)
async def analyze_gold():
    try:
        logger.info("Gold Analysis Requested")

        history = await gold_service.fetch_gold_history(90)
        indicators = gold_service.compute_indicators(history)

        news = await news_service.fetch_gold_news_india(limit=100)
        impact = news_service.get_news_impact_score(news, "gold")

        result = predict_trend_with_news(indicators, impact)

        ai = ai_service.analyze_with_ai(
            "Gold (India)",
            indicators["latest_price"],
            indicators,
            impact["sentiment"]
        )

        return build_prediction_response(
            asset="Gold (INR per 10g)",
            indicators=indicators,
            prediction=result,
            ai=ai,
            news_impact=impact,
            news_articles=news
        )

    except Exception as e:
        logger.error(f"Gold Analysis Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================================
# SILVER ANALYSIS
# ==================================================================
@app.get("/silver/analysis", response_model=PredictionResponse)
async def analyze_silver():
    try:
        logger.info("Silver Analysis Requested")

        history = await silver_service.fetch_silver_history(90)
        indicators = silver_service.compute_indicators(history)

        news = await news_service.fetch_multi_source_news("silver", 48, 100)
        impact = news_service.get_news_impact_score(news, "gold")

        result = predict_trend_with_news(indicators, impact)

        ai = ai_service.analyze_with_ai(
            "Silver (India)",
            indicators["latest_price"],
            indicators,
            impact["sentiment"]
        )

        return build_prediction_response(
            asset="Silver (INR per kg)",
            indicators=indicators,
            prediction=result,
            ai=ai,
            news_impact=impact,
            news_articles=news
        )

    except Exception as e:
        logger.error(f"Silver Analysis Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================================
# STOCK ANALYSIS
# ==================================================================
@app.get("/stock/{symbol}/analysis", response_model=PredictionResponse)
async def analyze_stock(symbol: str):
    try:
        logger.info(f"Stock Analysis Requested → {symbol}")

        history = await stock_service.fetch_stock_history(symbol, 90)
        indicators = stock_service.compute_indicators(history)

        news = await news_service.fetch_stock_news_india(symbol, 100)
        impact = news_service.get_news_impact_score(news, "stock")

        result = predict_trend_with_news(indicators, impact)

        ai = ai_service.analyze_with_ai(
            f"{symbol.upper()} (NSE)",
            indicators["latest_price"],
            indicators,
            impact["sentiment"]
        )

        return build_prediction_response(
            asset=f"{symbol.upper()} (NSE)",
            indicators=indicators,
            prediction=result,
            ai=ai,
            news_impact=impact,
            news_articles=news
        )

    except Exception as e:
        logger.error(f"Stock Analysis Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def build_prediction_response(asset, indicators, prediction, ai, news_impact, news_articles):
    return {
        "asset": asset,
        "current_price": indicators["latest_price"],
        "prediction": ai["prediction"],
        "confidence": ai["confidence"],
        "trend_score": prediction["trend_score"],
        "technical_score": prediction["technical_contribution"],
        "news_score": prediction["news_contribution"],
        "indicators": indicators,
        "news_analysis": {
            "sentiment": news_impact["sentiment"],
            "impact_score": news_impact["impact_score"],
            "recommendation": news_impact["recommendation"]
        },
        "ai_analysis": ai,
        "key_drivers": ai.get("reasoning", prediction["drivers"]),
        "critical_events": news_impact["events"][:5],
        "top_headlines": [
            {
                "title": n.get("title"),
                "source": n.get("source"),
                "link": n.get("link"),
                "published": str(n.get("published"))
            }
            for n in news_articles[:10]
        ]
    }


# ==================================================================
# CHATBOT
# ==================================================================
@app.post("/chatbot", response_model=ChatbotResponse)
async def chatbot(req: ChatbotRequest):
    try:
        logger.info(f"Chatbot Query: {req.question[:50]}")

        try:
            gold = await gold_service.fetch_current_gold_price()
            silver = await silver_service.fetch_current_silver_price()
            nifty = await stock_service.fetch_current_price("^NSEI")
            sensex = await stock_service.fetch_current_price("^BSESN")

            ctx = {
                "gold_price": gold["price"],
                "silver_price": silver["price"],
                "nifty": nifty["price"] if nifty else "N/A",
                "sensex": sensex["price"] if sensex else "N/A"
            }
        except:
            ctx = None

        result = await chatbot_service.chatbot_response(req.question, ctx)

        return {
            "question": req.question,
            "answer": result["answer"],
            "sources": result["sources"],
            "timestamp": result["timestamp"]
        }

    except Exception as e:
        logger.error(f"Chatbot Error: {e}")
        return {
            "question": req.question,
            "answer": f"I cannot answer right now. Error: {str(e)}",
            "sources": [],
            "timestamp": pd.Timestamp.now().isoformat()
        }


# ==================================================================
# MARKET OVERVIEW
# ==================================================================
@app.get("/market/overview", response_model=MarketOverviewResponse)
async def market_overview():
    try:
        logger.info("Market Overview Requested")

        nifty = await stock_service.fetch_current_price("^NSEI")
        sensex = await stock_service.fetch_current_price("^BSESN")
        gold = await gold_service.fetch_current_gold_price()

        news = await news_service.fetch_india_business_news(50)
        sentiment = news_service.compute_sentiment(news)

        return {
            "nifty": nifty,
            "sensex": sensex,
            "gold_inr": gold,
            "market_sentiment": sentiment,
            "top_headlines": [
                {
                    "title": n.get("title"),
                    "source": n.get("source"),
                    "link": n.get("link"),
                    "published": str(n.get("published"))
                }
                for n in news[:15]
            ],
            "last_updated": pd.Timestamp.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Market Overview Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================================
# BACKTEST
# ==================================================================
@app.get("/backtest/{asset_type}")
async def backtest(asset_type: str, days: int = Query(30, ge=7, le=90)):
    try:
        results = await run_backtest(asset_type, days)

        return {
            "asset": asset_type,
            "backtest_period_days": days,
            "accuracy": results.get("accuracy", 0),
            "total_predictions": results.get("total", 0),
            "correct_predictions": results.get("correct", 0),
            "profit_loss": results.get("profit_loss", 0),
            "daily_results": results.get("daily_results", [])
        }

    except Exception as e:
        logger.error(f"Backtest Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
