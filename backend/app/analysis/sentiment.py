import re
from typing import List, Dict, Any
from collections import Counter
import logging

logger = logging.getLogger(__name__)

# Enhanced financial sentiment lexicon
POSITIVE_KEYWORDS = {
    # Strong positive (weight 3)
    'surge': 3, 'soar': 3, 'rally': 3, 'boom': 3, 'skyrocket': 3,
    'breakthrough': 3, 'record high': 3, 'all-time high': 3, 'stellar': 3,
    'bullish': 3, 'outperform': 3, 'exceptional': 3,
    
    # Moderate positive (weight 2)
    'gain': 2, 'rise': 2, 'advance': 2, 'climb': 2, 'improve': 2,
    'growth': 2, 'profit': 2, 'beat': 2, 'upgrade': 2, 'strong': 2,
    'optimistic': 2, 'recover': 2, 'rebound': 2, 'boost': 2, 'jump': 2,
    'expand': 2, 'positive': 2,
    
    # Mild positive (weight 1)
    'up': 1, 'high': 1, 'better': 1, 'good': 1, 'hopeful': 1,
    'momentum': 1, 'stabilize': 1, 'increase': 1
}

NEGATIVE_KEYWORDS = {
    # Strong negative (weight 3)
    'crash': 3, 'plunge': 3, 'collapse': 3, 'slump': 3, 'crisis': 3,
    'plummet': 3, 'tumble': 3, 'nosedive': 3, 'bearish': 3,
    'catastrophic': 3, 'disaster': 3,
    
    # Moderate negative (weight 2)
    'fall': 2, 'drop': 2, 'decline': 2, 'decrease': 2, 'loss': 2,
    'miss': 2, 'underperform': 2, 'downgrade': 2, 'weak': 2,
    'concern': 2, 'worry': 2, 'pressure': 2, 'sink': 2, 'slide': 2,
    'negative': 2, 'disappointing': 2,
    
    # Mild negative (weight 1)
    'down': 1, 'low': 1, 'below': 1, 'risk': 1, 'caution': 1,
    'uncertainty': 1, 'volatile': 1, 'struggle': 1
}

# Market event keywords (can amplify sentiment)
CRITICAL_EVENTS = {
    'rbi rate hike': -2,
    'rbi rate cut': 2,
    'interest rate increase': -2,
    'interest rate cut': 2,
    'inflation surge': -2,
    'inflation eases': 2,
    'budget allocation': 1,
    'tax increase': -2,
    'tax cut': 2,
    'import duty hike': -1,
    'import duty cut': 1,
    'gdp growth': 2,
    'gdp contraction': -2,
    'rupee strengthens': 1,
    'rupee weakens': -1,
    'rupee falls': -1,
    'policy support': 2,
    'regulatory concern': -1,
}

def analyze_text_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment of a single text (headline/article)
    Returns sentiment score (-1 to 1), polarity, and strength
    """
    text_lower = text.lower()
    
    # Check for critical events first (highest priority)
    event_score = 0
    detected_events = []
    for event, score in CRITICAL_EVENTS.items():
        if event in text_lower:
            event_score += score
            detected_events.append(event)
    
    # Calculate keyword sentiment
    pos_score = sum(weight for word, weight in POSITIVE_KEYWORDS.items() if word in text_lower)
    neg_score = sum(weight for word, weight in NEGATIVE_KEYWORDS.items() if word in text_lower)
    
    # Combine scores (events weighted higher)
    total_score = (pos_score - neg_score) + (event_score * 1.5)
    
    # Normalize to -1 to 1 scale
    max_possible = 20  # Approximate maximum score
    normalized_score = max(-1, min(1, total_score / max_possible))
    
    # Determine polarity
    if normalized_score > 0.2:
        polarity = 'positive'
    elif normalized_score < -0.2:
        polarity = 'negative'
    else:
        polarity = 'neutral'
    
    # Strength (0-100)
    strength = min(100, abs(normalized_score) * 100)
    
    return {
        'score': round(normalized_score, 3),
        'polarity': polarity,
        'strength': round(strength, 1),
        'positive_score': pos_score,
        'negative_score': neg_score,
        'event_score': event_score,
        'detected_events': detected_events
    }

def analyze_articles_sentiment(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze sentiment across multiple articles
    Returns aggregated sentiment with statistics
    """
    if not articles:
        return {
            'overall_score': 0,
            'overall_polarity': 'neutral',
            'confidence': 0,
            'article_count': 0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'source_breakdown': {},
            'event_summary': [],
            'top_positive': [],
            'top_negative': []
        }
    
    article_sentiments = []
    all_events = []
    source_sentiments = {}
    
    for article in articles:
        text = article.get('title', '') + ' ' + article.get('content', '')
        sentiment = analyze_text_sentiment(text)
        
        article['sentiment'] = sentiment
        article_sentiments.append(sentiment['score'])
        all_events.extend(sentiment['detected_events'])
        
        # Track by source
        source = article.get('source', 'Unknown')
        if source not in source_sentiments:
            source_sentiments[source] = []
        source_sentiments[source].append(sentiment['score'])
    
    # Calculate overall metrics
    import numpy as np
    scores_array = np.array(article_sentiments)
    overall_score = float(np.mean(scores_array))
    score_std = float(np.std(scores_array))
    
    # Overall polarity
    if overall_score > 0.15:
        overall_polarity = 'positive'
    elif overall_score < -0.15:
        overall_polarity = 'negative'
    else:
        overall_polarity = 'neutral'
    
    # Confidence (based on agreement between articles)
    # Lower std dev = higher agreement = higher confidence
    confidence = max(0, min(100, (1 - score_std * 2) * 100))
    
    # Count distribution
    positive_count = sum(1 for s in article_sentiments if s > 0.15)
    negative_count = sum(1 for s in article_sentiments if s < -0.15)
    neutral_count = len(article_sentiments) - positive_count - negative_count
    
    # Source breakdown
    source_breakdown = {}
    for source, scores in source_sentiments.items():
        avg_score = sum(scores) / len(scores)
        source_breakdown[source] = {
            'avg_sentiment': round(avg_score, 3),
            'article_count': len(scores),
            'polarity': 'positive' if avg_score > 0.15 else 'negative' if avg_score < -0.15 else 'neutral'
        }
    
    # Event summary
    event_summary = [
        {'event': event, 'count': count}
        for event, count in Counter(all_events).most_common(10)
    ]
    
    # Top positive and negative articles
    sorted_articles = sorted(
        articles,
        key=lambda x: x.get('sentiment', {}).get('score', 0),
        reverse=True
    )
    
    top_positive = [
        {
            'title': a.get('title'),
            'source': a.get('source'),
            'score': a.get('sentiment', {}).get('score'),
            'link': a.get('link')
        }
        for a in sorted_articles[:3] if a.get('sentiment', {}).get('score', 0) > 0
    ]
    
    top_negative = [
        {
            'title': a.get('title'),
            'source': a.get('source'),
            'score': a.get('sentiment', {}).get('score'),
            'link': a.get('link')
        }
        for a in sorted_articles[-3:] if a.get('sentiment', {}).get('score', 0) < 0
    ]
    top_negative.reverse()
    
    return {
        'overall_score': round(overall_score, 3),
        'overall_polarity': overall_polarity,
        'confidence': round(confidence, 1),
        'article_count': len(articles),
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'source_breakdown': source_breakdown,
        'event_summary': event_summary,
        'top_positive': top_positive,
        'top_negative': top_negative,
        'score_std_dev': round(score_std, 3)
    }

def calculate_sentiment_momentum(current_articles: List[Dict], 
                                 previous_articles: List[Dict]) -> Dict[str, Any]:
    """
    Calculate sentiment change over time (momentum)
    Compares current vs previous sentiment
    """
    current_sentiment = analyze_articles_sentiment(current_articles)
    previous_sentiment = analyze_articles_sentiment(previous_articles)
    
    score_change = current_sentiment['overall_score'] - previous_sentiment['overall_score']
    
    # Determine momentum direction
    if score_change > 0.1:
        momentum = 'improving'
    elif score_change < -0.1:
        momentum = 'deteriorating'
    else:
        momentum = 'stable'
    
    return {
        'current_score': current_sentiment['overall_score'],
        'previous_score': previous_sentiment['overall_score'],
        'score_change': round(score_change, 3),
        'momentum': momentum,
        'momentum_strength': min(100, abs(score_change) * 200)
    }

def extract_key_themes(articles: List[Dict[str, Any]], top_n: int = 5) -> List[str]:
    """
    Extract key themes/topics from articles
    """
    all_text = ' '.join([
        article.get('title', '') + ' ' + article.get('content', '')
        for article in articles
    ]).lower()
    
    # Common financial themes/keywords
    themes = {
        'rate hike': ['rate hike', 'interest rate increase', 'rbi hike'],
        'rate cut': ['rate cut', 'interest rate cut', 'rbi cut'],
        'inflation': ['inflation', 'cpi', 'wpi', 'price rise'],
        'rupee': ['rupee', 'currency', 'exchange rate', 'dollar'],
        'gdp': ['gdp', 'economic growth', 'growth rate'],
        'budget': ['budget', 'fiscal policy', 'allocation'],
        'earnings': ['earnings', 'profit', 'quarterly results'],
        'gold import': ['gold import', 'gold duty'],
        'market volatility': ['volatility', 'volatile', 'uncertainty'],
        'fii/dii': ['fii', 'dii', 'foreign investor', 'domestic investor']
    }
    
    theme_counts = {}
    for theme_name, keywords in themes.items():
        count = sum(all_text.count(keyword) for keyword in keywords)
        if count > 0:
            theme_counts[theme_name] = count
    
    # Return top N themes
    sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    return [theme for theme, count in sorted_themes[:top_n]]

def sentiment_to_prediction_weight(sentiment_score: float, confidence: float) -> float:
    """
    Convert sentiment score to prediction weight
    Used in predictor.py to weight news sentiment
    """
    # Amplify strong sentiments, dampen weak ones
    if abs(sentiment_score) > 0.5:
        amplification = 1.3
    elif abs(sentiment_score) > 0.3:
        amplification = 1.1
    else:
        amplification = 0.9
    
    # Apply confidence multiplier
    confidence_multiplier = confidence / 100
    
    weighted_score = sentiment_score * amplification * confidence_multiplier
    
    # Clamp to -1 to 1
    return max(-1, min(1, weighted_score))
