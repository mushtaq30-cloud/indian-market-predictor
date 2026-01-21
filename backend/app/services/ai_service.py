from ..config import settings
import logging
import json
from typing import List, Dict, Any
import requests

logger = logging.getLogger(__name__)

# Initialize clients based on provider
def get_ai_client():
    """Get appropriate AI client based on config"""
    if settings.AI_PROVIDER == "groq" and settings.GROQ_API_KEY:
        try:
            from groq import Groq
            return Groq(api_key=settings.GROQ_API_KEY), "groq"
        except TypeError as e:
            if "proxies" in str(e):
                logger.warning("Groq client proxy issue detected. Using fallback AI provider.")
                # Try using Gemini as fallback if Groq fails
                if settings.GEMINI_API_KEY:
                    import google.generativeai as genai
                    genai.configure(api_key=settings.GEMINI_API_KEY)
                    return genai, "gemini"
                else:
                    return None, "fallback"
            else:
                raise
    
    elif settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai, "gemini"
    
    elif settings.AI_PROVIDER == "huggingface" and settings.HUGGINGFACE_API_KEY:
        return None, "huggingface"  # Use API directly
    
    else:
        logger.warning("No AI provider configured. Using fallback.")
        return None, "fallback"

def call_groq(prompt: str, system_prompt: str) -> str:
    """Call Groq API"""
    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    # Ensure the message contains "json" when using json_object response format
    prompt_with_json = prompt if "json" in prompt.lower() else prompt + "\n\nRespond with valid JSON only."
    
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_with_json}
        ],
        temperature=0.3,
        max_tokens=2000,
        response_format={"type": "json_object"}
    )
    
    return response.choices[0].message.content

def call_gemini(prompt: str, system_prompt: str) -> str:
    """Call Google Gemini API"""
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)
    
    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        system_instruction=system_prompt
    )
    
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 2000,
        }
    )
    
    return response.text

def call_huggingface(prompt: str, system_prompt: str) -> str:
    """Call Hugging Face Inference API"""
    url = f"https://api-inference.huggingface.co/models/{settings.HUGGINGFACE_MODEL}"
    headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
    
    full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
    
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 2000,
            "temperature": 0.3,
            "return_full_text": False
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    result = response.json()
    if isinstance(result, list) and len(result) > 0:
        return result[0].get('generated_text', '')
    return str(result)

def analyze_with_ai(
    asset_name: str,
    current_price: float,
    indicators: Dict[str, Any],
    news_summary: Dict[str, Any],
    historical_data: str = ""
) -> Dict[str, Any]:
    """
    Use AI to provide intelligent analysis - COMPLETELY FREE
    """
    client, provider = get_ai_client()
    
    if provider == "fallback":
        logger.warning("No AI provider configured. Using rule-based fallback.")
        return fallback_analysis(asset_name, current_price, indicators, news_summary)
    
    try:
        system_prompt = "You are a financial analyst expert. Always respond with valid JSON only, no markdown or extra text."
        
        prompt = f"""You are an expert financial analyst specializing in Indian markets. Fetch the data from Internet and compare and analyze the following data and provide detailed insights:

**Asset:** {asset_name}
**Current Price:** ₹{current_price:,.2f}

**Technical Indicators:**
- 20-day MA: ₹{indicators.get('ma_20', 'N/A')}
- 50-day MA: ₹{indicators.get('ma_50', 'N/A')}
- RSI: {indicators.get('rsi', 'N/A')}
- Volatility: {indicators.get('volatility', 0)*100:.2f}%
- Recent 20-day return: {indicators.get('recent_return_20d', 0)*100:.2f}%

**News Sentiment:**
- Overall Sentiment: {news_summary.get('label', 'neutral').upper()}
- Sentiment Score: {news_summary.get('overall_sentiment', 0)}
- Positive Articles: {news_summary.get('positive_count', 0)}
- Negative Articles: {news_summary.get('negative_count', 0)}
- Total Articles: {news_summary.get('article_count', 0)}

**Events:** {json.dumps(news_summary.get('event_summary', [])[:3], indent=2)}

Provide analysis as JSON:
{{
  "prediction": "BULLISH/BEARISH/NEUTRAL",
  "confidence": 75,
  "reasoning": ["reason1", "reason2", "reason3"],
  "risks": ["risk1", "risk2", "risk3"],
  "opportunities": ["opp1", "opp2"],
  "time_horizon": "1-7 days outlook",
  "recommendation": {{
    "action": "BUY/SELL/HOLD",
    "position_size": "5-10% of portfolio",
    "stop_loss": "price level",
    "target_price": "price level"
  }},
  "summary": "2-3 sentence summary"
}}

Focus on Indian market factors: RBI policy, rupee movement, local news."""

        # Call appropriate provider
        if provider == "groq":
            ai_response = call_groq(prompt, system_prompt)
        elif provider == "gemini":
            ai_response = call_gemini(prompt, system_prompt)
        elif provider == "huggingface":
            ai_response = call_huggingface(prompt, system_prompt)
        else:
            # Defensive guard: if a new/unknown provider is ever introduced
            raise ValueError(f"Unknown AI provider: {provider}")
        
        # Parse response
        try:
            # Clean response (remove markdown if present)
            clean_response = ai_response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            analysis = json.loads(clean_response)
            logger.info(f"AI Analysis ({provider}) complete: {analysis.get('prediction')}")
            return analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}. Response: {ai_response[:200]}")
            return fallback_analysis(asset_name, current_price, indicators, news_summary)
    
    except Exception as e:
        logger.error(f"AI analysis error: {e}")
        return fallback_analysis(asset_name, current_price, indicators, news_summary)

def fallback_analysis(asset_name, current_price, indicators, news_summary):
    """Rule-based fallback when AI unavailable"""
    
    # Calculate prediction based on indicators
    ma_20 = indicators.get('ma_20', current_price)
    rsi = indicators.get('rsi', 50)
    recent_return = indicators.get('recent_return_20d', 0)
    sentiment_score = news_summary.get('overall_sentiment', 0)
    
    # Simple scoring
    score = 0
    reasoning = []
    
    # Technical signals
    if current_price > ma_20:
        score += 1
        reasoning.append("Price above 20-day MA (bullish)")
    else:
        score -= 1
        reasoning.append("Price below 20-day MA (bearish)")
    
    if rsi < 30:
        score += 1
        reasoning.append("RSI oversold - potential bounce")
    elif rsi > 70:
        score -= 1
        reasoning.append("RSI overbought - potential correction")
    
    if recent_return > 0.01:
        score += 1
        reasoning.append("Positive momentum (20-day return)")
    elif recent_return < -0.01:
        score -= 1
        reasoning.append("Negative momentum")
    
    # News sentiment
    if sentiment_score > 0.2:
        score += 2
        reasoning.append("Strong positive news sentiment")
    elif sentiment_score < -0.2:
        score -= 2
        reasoning.append("Strong negative news sentiment")
    
    # Determine prediction
    if score >= 1:  # Lower threshold for bullish
        prediction = "BULLISH"
        confidence = min(95, max(65, 65 + abs(score) * 8))  # Increased from 60 + abs(score) * 5
        action = "BUY"
    elif score <= -1:  # Lower threshold for bearish
        prediction = "BEARISH"
        confidence = min(95, max(65, 65 + abs(score) * 8))  # Increased
        action = "SELL"
    else:
        prediction = "NEUTRAL"
        # Calculate confidence even for neutral based on signal strength
        # Use more varied confidence values based on how close to zero
        import random
        # Base confidence of 50-65% for neutral with some randomness
        base_confidence = 55 + abs(score) * 5
        # Add some randomness to avoid all stocks having the same confidence
        random_variation = random.randint(-8, 8)
        confidence = min(75, max(45, int(base_confidence + random_variation)))
        action = "HOLD"
    
    return {
        "prediction": prediction,
        "confidence": confidence,
        "reasoning": reasoning[:3],
        "risks": ["Market volatility", "External events", "Policy changes"],
        "opportunities": ["Trend continuation", "Mean reversion"],
        "time_horizon": "Short-term (1-7 days)",
        "recommendation": {
            "action": action,
            "position_size": "5-10% of portfolio",
            "stop_loss": f"₹{current_price * 0.95:.2f}",
            "target_price": f"₹{current_price * 1.05:.2f}"
        },
        "summary": f"Based on technical indicators and sentiment, outlook is {prediction.lower()} with {confidence}% confidence."
    }

def generate_market_insights(gold_data, silver_data, stock_indices, news_headlines):
    """Generate market insights - FREE version"""
    client, provider = get_ai_client()
    
    # Strong input normalization
    def _as_price_dict(value):
        if isinstance(value, dict):
            return {
                "price": value.get("price", 0),
                "change_percent": value.get("change_percent", value.get("change", 0))
            }
        if isinstance(value, (int, float)):
            return {"price": float(value), "change_percent": 0}
        return {"price": 0, "change_percent": 0}

    def _as_dict_list(seq):
        """Keep mapping-like headline objects (dict or any Mapping with .get)."""
        from collections.abc import Mapping
        if not seq:
            return []
        if not isinstance(seq, list):
            return []
        normalized = []
        for item in seq:
            if isinstance(item, Mapping):
                normalized.append(dict(item))
            elif hasattr(item, "get"):
                # Preserve objects that duck-type like dicts
                normalized.append(item)
        return normalized

    gold_data = _as_price_dict(gold_data)
    silver_data = _as_price_dict(silver_data)
    stock_indices = stock_indices or {}
    news_headlines = _as_dict_list(news_headlines)
    
    # Ensure indices have default values
    nifty_data = _as_price_dict(stock_indices.get('nifty'))
    sensex_data = _as_price_dict(stock_indices.get('sensex'))
    
    if provider == "fallback":
        # Generate more dynamic insights based on actual market data
        import random
        nifty_price = nifty_data.get('price', 0)
        sensex_price = sensex_data.get('price', 0)
        
        # Determine market direction based on indices
        nifty_change = nifty_data.get('change_percent', 0)
        sensex_change = sensex_data.get('change_percent', 0)
        
        # Generate insights based on market conditions
        if nifty_change > 0.5 or sensex_change > 0.5:
            market_direction = "bullish"
            drivers = ["Positive global cues", "Strong banking stocks", "Foreign institutional investor flows"]
        elif nifty_change < -0.5 or sensex_change < -0.5:
            market_direction = "bearish"
            drivers = ["Global headwinds", "Rising inflation concerns", "Profit booking"]
        else:
            market_direction = "mixed"
            drivers = ["Mixed global cues", "Sector rotation", "Waiting for policy updates"]
        
        # Generate dynamic content
        watch_items = ["RBI policy", "Crude oil prices", "USD-INR movement", "Corporate earnings"]
        random_watch = random.sample(watch_items, 2)
        
        return f"""Indian markets showing {market_direction} signals today. 
NIFTY at {nifty_price} ({nifty_change:+.2f}%), SENSEX at {sensex_price} ({sensex_change:+.2f}%). 
Key drivers: {', '.join(drivers[:2])}. Watch: {', '.join(random_watch)}. 
Gold: ₹{gold_data.get('price', 0)}/10g, Silver: ₹{silver_data.get('price', 0)}/kg."""
    
    try:
        system_prompt = "You are a financial market analyst. Be concise and actionable."
        
        # Safely extract headlines, filtering out None values
        safe_headlines = [h for h in news_headlines[:5] if hasattr(h, 'get')]
        headline_titles = [h.get('title', '')[:50] for h in safe_headlines]
        
        prompt = f"""Analyze Indian market briefly (3-4 sentences):

**Gold:** ₹{gold_data.get('price', 0)}/10g
**Silver:** ₹{silver_data.get('price', 0)}/kg
**NIFTY:** {nifty_data.get('price', 0)}
**Sensex:** {sensex_data.get('price', 0)}

**Headlines:** {', '.join(headline_titles)}

Provide: 1) Market direction, 2) Key drivers, 3) What to watch, 4) Sentiment"""

        if provider == "groq":
            insights = call_groq(prompt, system_prompt)
        elif provider == "gemini":
            insights = call_gemini(prompt, system_prompt)
        elif provider == "huggingface":
            insights = call_huggingface(prompt, system_prompt)
        else:
            # Defensive guard: if a new/unknown provider is ever introduced
            raise ValueError(f"Unknown AI provider: {provider}")
        
        return insights.strip()
        
    except Exception as e:
        logger.error(f"Market insights error: {e}", exc_info=True)
        # Return a dynamic fallback instead of static message
        import random
        nifty_price = nifty_data.get('price', 0)
        sensex_price = sensex_data.get('price', 0)
        
        # Determine market direction based on indices
        nifty_change = nifty_data.get('change_percent', 0)
        sensex_change = sensex_data.get('change_percent', 0)
        
        # Safely extract headlines for fallback
        safe_headlines = [h for h in news_headlines[:5] if hasattr(h, 'get')]
        headline_titles = [h.get('title', '')[:50] for h in safe_headlines]
        
        # Generate insights based on market conditions
        if nifty_change > 0.5 or sensex_change > 0.5:
            market_direction = "bullish"
            drivers = ["Positive global cues", "Strong banking stocks", "Foreign institutional investor flows"]
        elif nifty_change < -0.5 or sensex_change < -0.5:
            market_direction = "bearish"
            drivers = ["Global headwinds", "Rising inflation concerns", "Profit booking"]
        else:
            market_direction = "mixed"
            drivers = ["Mixed global cues", "Sector rotation", "Waiting for policy updates"]
        
        # Generate dynamic content
        watch_items = ["RBI policy", "Crude oil prices", "USD-INR movement", "Corporate earnings"]
        random_watch = random.sample(watch_items, 2)
        
        return f"""Indian markets showing {market_direction} signals today. 
NIFTY at {nifty_price} ({nifty_change:+.2f}%), SENSEX at {sensex_price} ({sensex_change:+.2f}%). 
Key drivers: {', '.join(drivers[:2])}. Watch: {', '.join(random_watch)}. 
Gold: ₹{gold_data.get('price', 0)}/10g, Silver: ₹{silver_data.get('price', 0)}/kg."""
