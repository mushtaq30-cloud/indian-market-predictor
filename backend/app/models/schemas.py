from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class PredictionResponse(BaseModel):
    asset: str
    current_price: float
    prediction: str
    confidence: float
    trend_score: float
    technical_score: float
    news_score: float
    indicators: Dict[str, Any]
    news_analysis: Dict[str, Any]
    ai_analysis: Optional[Dict[str, Any]] = None
    key_drivers: List[str]
    critical_events: List[Dict[str, Any]]
    top_headlines: List[Dict[str, str]]

class MarketOverviewResponse(BaseModel):
    nifty: Optional[Dict[str, Any]]
    sensex: Optional[Dict[str, Any]]
    gold_inr: Dict[str, Any]
    market_sentiment: Dict[str, Any]
    top_headlines: List[Dict[str, str]]
    last_updated: str

class ChatbotRequest(BaseModel):
    question: str

class ChatbotResponse(BaseModel):
    question: str
    answer: str
    sources: List[Dict[str, str]]
    timestamp: str

class HistoryRecord(BaseModel):
    date: str
    price_inr: float

class AssetCard(BaseModel):
    price: float
    unit: str
    prediction: str
    confidence: float
    tomorrow_price: float
    history: List[HistoryRecord]
    ai_analysis: Optional[Dict[str, Any]] = None
    prediction_drivers: List[str] = []

class DashboardResponse(BaseModel):
    gold: AssetCard
    silver: AssetCard
    nifty: Optional[Dict[str, Any]]
    sensex: Optional[Dict[str, Any]]
    market_sentiment: Dict[str, Any]
    ai_insights: str
    top_news: List[Dict[str, str]]
    top_stocks: Optional[Dict[str, Any]] = None
    top_mutual_funds: Optional[Dict[str, Any]] = None
    last_updated: str
