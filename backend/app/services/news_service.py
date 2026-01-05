import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from collections import Counter
import re
import logging
import pandas as pd

logger = logging.getLogger(__name__)

# RSS feeds configuration
RSS_FEEDS = {
    'gold': [
        'https://news.google.com/rss/search?q=gold+price+india&hl=en-IN&gl=IN&ceid=IN:en',
        'https://news.google.com/rss/search?q=gold+import+india&hl=en-IN&gl=IN&ceid=IN:en',
    ],
    'stock_market': [
        'https://news.google.com/rss/search?q=india+stock+market+nifty+sensex&hl=en-IN&gl=IN&ceid=IN:en',
        'https://news.google.com/rss/search?q=india+shares+market&hl=en-IN&gl=IN&ceid=IN:en',
    ],
    'rbi_policy': [
        'https://news.google.com/rss/search?q=RBI+monetary+policy+india&hl=en-IN&gl=IN&ceid=IN:en',
        'https://news.google.com/rss/search?q=reserve+bank+india+interest+rate&hl=en-IN&gl=IN&ceid=IN:en',
    ],
    'rupee': [
        'https://news.google.com/rss/search?q=rupee+dollar+exchange+rate&hl=en-IN&gl=IN&ceid=IN:en',
    ],
    'business': [
        'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pKVGlnQVAB?hl=en-IN&gl=IN&ceid=IN%3Aen',
    ]
}

async def fetch_multi_source_news(topic: str, hours: int = 48, limit: int = 50):
    """Aggregate news from multiple RSS sources"""
    all_articles = []
    feeds = RSS_FEEDS.get(topic, RSS_FEEDS['business'])
    
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:limit]:
                # Parse published date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                else:
                    pub_date = datetime.now()
                
                # Filter by recency
                if (datetime.now() - pub_date).total_seconds() / 3600 > hours:
                    continue
                
                # Extract source from link
                source = extract_source_name(entry.link)
                
                all_articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': pub_date,
                    'source': source,
                    'content': entry.get('summary', ''),
                })
                
        except Exception as e:
            logger.warning(f"Error fetching from {feed_url}: {e}")
            continue
    
    logger.info(f"Fetched {len(all_articles)} articles for topic: {topic}")
    return all_articles

def extract_source_name(url: str):
    """Extract news source from URL"""
    domain_map = {
        'economictimes': 'Economic Times',
        'livemint': 'Mint',
        'moneycontrol': 'Moneycontrol',
        'business-standard': 'Business Standard',
        'reuters': 'Reuters',
        'bloomberg': 'Bloomberg',
        'thehindu': 'The Hindu',
        'ndtv': 'NDTV',
        'hindustantimes': 'Hindustan Times',
        'financialexpress': 'Financial Express',
    }
    
    url_lower = url.lower()
    for key, name in domain_map.items():
        if key in url_lower:
            return name
    
    return 'News Source'

def compute_sentiment(articles: list):
    """Enhanced sentiment analysis with financial keywords"""
    if not articles:
        return {
            'overall_sentiment': 0,
            'confidence': 0,
            'label': 'neutral',
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'article_count': 0
        }
    
    # Financial sentiment keywords with weights
    positive_keywords = {
        'surge': 3, 'soar': 3, 'rally': 3, 'boom': 3, 'breakthrough': 3,
        'gain': 2, 'rise': 2, 'up': 1, 'high': 2, 'bull': 2, 'strong': 2,
        'growth': 2, 'profit': 2, 'beat': 2, 'outperform': 3, 'upgrade': 2,
        'positive': 1, 'optimistic': 2, 'recover': 2, 'rebound': 2, 'boost': 2
    }
    
    negative_keywords = {
        'crash': 3, 'plunge': 3, 'collapse': 3, 'slump': 3, 'crisis': 3,
        'fall': 2, 'drop': 2, 'down': 1, 'low': 2, 'bear': 2, 'weak': 2,
        'loss': 2, 'miss': 2, 'underperform': 3, 'downgrade': 2, 'sell': 1,
        'negative': 1, 'concern': 2, 'worry': 2, 'risk': 1, 'decline': 2,
        'tumble': 3, 'sink': 2
    }
    
    sentiment_scores = []
    
    for article in articles:
        text = (article.get('title', '') + ' ' + article.get('content', '')).lower()
        
        pos_score = sum(weight for word, weight in positive_keywords.items() if word in text)
        neg_score = sum(weight for word, weight in negative_keywords.items() if word in text)
        
        # Normalize
        article_sentiment = (pos_score - neg_score) / max(1, pos_score + neg_score)
        sentiment_scores.append(article_sentiment)
    
    # Overall metrics
    overall_sentiment = sum(sentiment_scores) / len(sentiment_scores)
    
    # Label
    if overall_sentiment > 0.15:
        label = 'positive'
    elif overall_sentiment < -0.15:
        label = 'negative'
    else:
        label = 'neutral'
    
    # Counts
    positive_count = sum(1 for s in sentiment_scores if s > 0.15)
    negative_count = sum(1 for s in sentiment_scores if s < -0.15)
    neutral_count = len(sentiment_scores) - positive_count - negative_count
    
    # Confidence (based on agreement)
    sentiment_std = pd.Series(sentiment_scores).std()
    confidence = max(0, min(100, (1 - sentiment_std * 2) * 100))
    
    return {
        'overall_sentiment': round(overall_sentiment, 3),
        'confidence': round(confidence, 1),
        'label': label,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'article_count': len(articles)
    }

def detect_market_events(articles: list):
    """Detect specific market-moving events"""
    events_detected = []
    
    event_patterns = {
        'rbi_policy': r'rbi.*?(rate|policy|repo|monetary)',
        'budget': r'budget.*?(202\d|announcement|speech)',
        'earnings': r'(earnings|quarterly results|q[1-4] results)',
        'merger': r'(merger|acquisition|m&a|takeover)',
        'ipo': r'(ipo|initial public offering|listing)',
        'inflation': r'inflation.*?(\d+\.?\d*)\s*%',
        'gdp': r'gdp.*?growth',
        'rupee': r'rupee.*?(dollar|falls|strengthens|weakens)',
        'import_duty': r'import duty.*?(gold|increase|decrease)',
    }
    
    for article in articles:
        text = (article.get('title', '') + ' ' + article.get('content', '')).lower()
        
        for event_type, pattern in event_patterns.items():
            if re.search(pattern, text):
                events_detected.append({
                    'type': event_type.replace('_', ' ').title(),
                    'source': article.get('source'),
                    'title': article.get('title'),
                    'link': article.get('link'),
                    'published': article.get('published')
                })
                break  # One event per article
    
    return events_detected

def get_news_impact_score(articles: list, asset_type: str = 'stock'):
    """Calculate comprehensive news impact score"""
    sentiment = compute_sentiment(articles)
    events = detect_market_events(articles)
    
    # Base score from sentiment
    impact_score = sentiment['overall_sentiment']
    
    # Amplify based on critical events
    critical_event_types = ['rbi_policy', 'Budget', 'Inflation', 'Import Duty']
    critical_events = [e for e in events if any(et in e['type'] for et in critical_event_types)]
    
    if critical_events:
        impact_score *= (1 + len(critical_events) * 0.25)
    
    # Asset-specific adjustments
    if asset_type == 'gold':
        gold_sensitive = ['Inflation', 'Rupee', 'Rbi Policy', 'Import Duty']
        gold_events = [e for e in events if any(gs in e['type'] for gs in gold_sensitive)]
        if gold_events:
            impact_score *= (1 + len(gold_events) * 0.3)
    
    # Confidence adjustment
    confidence_multiplier = sentiment['confidence'] / 100
    final_score = impact_score * confidence_multiplier
    
    # Recommendation strength
    abs_score = abs(final_score)
    if abs_score > 0.5:
        recommendation = 'Strong'
    elif abs_score > 0.25:
        recommendation = 'Moderate'
    else:
        recommendation = 'Weak'
    
    return {
        'impact_score': round(final_score, 3),
        'sentiment': sentiment,
        'events': events,
        'recommendation': recommendation,
        'critical_events_count': len(critical_events)
    }

# Wrapper functions
async def fetch_gold_news_india(limit: int = 100):
    """Fetch gold-specific news for India"""
    articles = await fetch_multi_source_news('gold', hours=48, limit=limit)
    
    # Also add RBI and rupee news (affects gold)
    rbi_articles = await fetch_multi_source_news('rbi_policy', hours=72, limit=20)
    rupee_articles = await fetch_multi_source_news('rupee', hours=48, limit=20)
    
    return articles + rbi_articles + rupee_articles

async def fetch_stock_news_india(symbol: str, limit: int = 100):
    """Fetch stock market and symbol-specific news"""
    # General market news
    market_articles = await fetch_multi_source_news('stock_market', hours=24, limit=limit//2)
    
    # Symbol-specific news
    symbol_clean = symbol.replace('.NS', '').replace('.BO', '')
    symbol_feed = f"https://news.google.com/rss/search?q={symbol_clean}+stock+share+india&hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        feed = feedparser.parse(symbol_feed)
        for entry in feed.entries[:limit//2]:
            market_articles.append({
                'title': entry.title,
                'link': entry.link,
                'published': datetime.now(),
                'source': extract_source_name(entry.link),
                'content': entry.get('summary', '')
            })
    except Exception as e:
        logger.warning(f"Error fetching symbol-specific news: {e}")
    
    return market_articles

async def fetch_india_business_news(limit: int = 50):
    """Fetch general India business news"""
    return await fetch_multi_source_news('business', hours=24, limit=limit)
