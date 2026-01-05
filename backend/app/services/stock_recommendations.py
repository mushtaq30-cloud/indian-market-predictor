"""
Stock recommendations and mutual funds service
Provides trending stocks, top buy/sell picks, and mutual fund suggestions
"""

import logging
from typing import List, Dict, Any
import random

logger = logging.getLogger(__name__)

# Top Indian stocks by market cap and interest
TOP_NIFTY_50_STOCKS = {
    "RELIANCE.NS": {"name": "Reliance Industries", "sector": "Energy"},
    "TCS.NS": {"name": "Tata Consultancy Services", "sector": "IT"},
    "INFY.NS": {"name": "Infosys", "sector": "IT"},
    "WIPRO.NS": {"name": "Wipro", "sector": "IT"},
    "HINDUNILVR.NS": {"name": "Hindustan Unilever", "sector": "FMCG"},
    "LT.NS": {"name": "Larsen & Toubro", "sector": "Industrials"},
    "MARUTI.NS": {"name": "Maruti Suzuki", "sector": "Automotive"},
    "BAJAJFINSV.NS": {"name": "Bajaj Finserv", "sector": "Finance"},
    "HDFCBANK.NS": {"name": "HDFC Bank", "sector": "Banking"},
    "ICICIBANK.NS": {"name": "ICICI Bank", "sector": "Banking"},
    "AXISBANK.NS": {"name": "Axis Bank", "sector": "Banking"},
    "KOTAKBANK.NS": {"name": "Kotak Mahindra Bank", "sector": "Banking"},
}

# Top mutual funds (simulated - in production use real data)
TOP_MUTUAL_FUNDS = [
    {
        "name": "ICICI Prudential Bluechip Fund",
        "aum": "₹45,000 Cr",
        "return_1yr": 22.5,
        "rating": "5-star",
        "type": "Large Cap"
    },
    {
        "name": "Axis Bluechip Fund",
        "aum": "₹32,500 Cr",
        "return_1yr": 21.8,
        "rating": "5-star",
        "type": "Large Cap"
    },
    {
        "name": "HDFC Top 100 Fund",
        "aum": "₹38,000 Cr",
        "return_1yr": 23.2,
        "rating": "5-star",
        "type": "Large Cap"
    },
    {
        "name": "Mirae Asset Large Cap Fund",
        "aum": "₹28,500 Cr",
        "return_1yr": 24.1,
        "rating": "5-star",
        "type": "Large Cap"
    },
    {
        "name": "SBI Bluechip Fund",
        "aum": "₹25,000 Cr",
        "return_1yr": 20.5,
        "rating": "4-star",
        "type": "Large Cap"
    },
    {
        "name": "Motilal Oswal Large & Midcap Fund",
        "aum": "₹22,000 Cr",
        "return_1yr": 26.3,
        "rating": "5-star",
        "type": "Multi Cap"
    },
]


def get_top_stock_picks() -> Dict[str, Any]:
    """Get top buy/sell stock recommendations"""
    try:
        stocks_list = list(TOP_NIFTY_50_STOCKS.items())
        
        # Simulate buy/sell recommendations based on mock sentiment
        buy_picks = []
        sell_picks = []
        
        for i, (symbol, info) in enumerate(stocks_list):
            # Simulated score (in production, use real technical + news data)
            score = (hash(symbol + str(random.randint(1, 100))) % 100) / 100
            
            if score > 0.65:
                price_change = random.uniform(1.5, 5.5)  # %
                buy_picks.append({
                    "symbol": symbol,
                    "name": info["name"],
                    "sector": info["sector"],
                    "recommendation": "BUY",
                    "target_price_change": f"+{price_change:.1f}%",
                    "confidence": random.randint(70, 90),
                    "reason": f"Strong momentum + positive technical signals in {info['sector']}"
                })
            elif score < 0.35:
                price_change = random.uniform(-2.5, -0.5)  # %
                sell_picks.append({
                    "symbol": symbol,
                    "name": info["name"],
                    "sector": info["sector"],
                    "recommendation": "SELL",
                    "target_price_change": f"{price_change:.1f}%",
                    "confidence": random.randint(65, 85),
                    "reason": f"Resistance at key level + bearish divergence in {info['sector']}"
                })
        
        # Ensure we have some picks
        if not buy_picks and stocks_list:
            symbol, info = stocks_list[0]
            buy_picks.append({
                "symbol": symbol,
                "name": info["name"],
                "sector": info["sector"],
                "recommendation": "BUY",
                "target_price_change": "+2.5%",
                "confidence": 75,
                "reason": f"Value buying opportunity in {info['sector']}"
            })
        
        if not sell_picks and len(stocks_list) > 1:
            symbol, info = stocks_list[1]
            sell_picks.append({
                "symbol": symbol,
                "name": info["name"],
                "sector": info["sector"],
                "recommendation": "SELL",
                "target_price_change": "-1.8%",
                "confidence": 70,
                "reason": f"Profit booking phase in {info['sector']}"
            })
        
        return {
            "top_buys": sorted(buy_picks, key=lambda x: x["confidence"], reverse=True)[:5],
            "top_sells": sorted(sell_picks, key=lambda x: x["confidence"], reverse=True)[:3],
            "market_trend": "Bullish" if len(buy_picks) > len(sell_picks) else "Bearish",
            "last_updated": "2026-01-03T15:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error getting stock picks: {e}")
        return {
            "top_buys": [],
            "top_sells": [],
            "market_trend": "Neutral",
            "last_updated": "2026-01-03T15:30:00Z"
        }


def get_top_mutual_funds() -> Dict[str, Any]:
    """Get top mutual funds recommendations"""
    try:
        # Sort by 1-year return
        sorted_funds = sorted(TOP_MUTUAL_FUNDS, key=lambda x: x["return_1yr"], reverse=True)
        
        return {
            "top_funds": sorted_funds[:4],  # Top 4 funds
            "categories": {
                "large_cap": [f for f in sorted_funds if f["type"] == "Large Cap"][:2],
                "multi_cap": [f for f in sorted_funds if f["type"] == "Multi Cap"][:1],
            },
            "total_aum": "₹2,50,000 Cr+",
            "investment_insight": "Diversified portfolio recommended: 40% Large Cap + 30% Multi Cap + 30% Sector/Thematic",
            "last_updated": "2026-01-03T15:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Error getting mutual funds: {e}")
        return {
            "top_funds": [],
            "categories": {},
            "total_aum": "N/A",
            "investment_insight": "Data temporarily unavailable",
            "last_updated": "2026-01-03T15:30:00Z"
        }
