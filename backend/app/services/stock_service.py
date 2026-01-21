import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import time
from typing import Dict, Any
from . import stock_scraper

logger = logging.getLogger(__name__)

# Rate limiting
last_request_time = 0
MIN_REQUEST_INTERVAL = 2  # seconds between requests

def rate_limited_request(url, params=None, max_retries=3):
    """Make rate-limited request with retries"""
    global last_request_time
    
    for attempt in range(max_retries):
        try:
            # Wait to respect rate limit
            elapsed = time.time() - last_request_time
            if elapsed < MIN_REQUEST_INTERVAL:
                time.sleep(MIN_REQUEST_INTERVAL - elapsed)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            last_request_time = time.time()
            
            if response.status_code == 429:
                wait_time = (attempt + 1) * 5
                logger.warning(f"Rate limited. Waiting {wait_time}s before retry {attempt+1}/{max_retries}")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                logger.warning(f"Rate limit hit. Retry {attempt+1}/{max_retries} after {wait_time}s")
                time.sleep(wait_time)
                continue
            else:
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Request failed: {e}. Retry {attempt+1}/{max_retries}")
                time.sleep(2)
                continue
            else:
                raise
    
    raise Exception("Max retries exceeded")

async def fetch_stock_history(symbol: str, days: int = 90):
    """Fetch stock price history with rate limiting"""
    try:
        # Add .NS suffix for NSE if not present
        if not symbol.endswith('.NS') and not symbol.endswith('.BO') and not symbol.startswith('^'):
            symbol = f"{symbol}.NS"
        
        # Yahoo Finance API
        period2 = int(datetime.now().timestamp())
        period1 = int((datetime.now() - timedelta(days=days)).timestamp())
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {
            'period1': period1,
            'period2': period2,
            'interval': '1d'
        }
        
        response = rate_limited_request(url, params)
        data = response.json()
        
        # Extract price data
        result = data['chart']['result'][0]
        timestamps = result['timestamp']
        quotes = result['indicators']['quote'][0]
        
        df = pd.DataFrame({
            'date': pd.to_datetime(timestamps, unit='s'),
            'open': quotes['open'],
            'high': quotes['high'],
            'low': quotes['low'],
            'close': quotes['close'],
            'volume': quotes['volume']
        })
        
        df = df.dropna()
        df = df.sort_values('date')
        
        logger.info(f"Fetched {len(df)} days of data for {symbol}")
        return df
        
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        return pd.DataFrame()

async def fetch_current_price(symbol: str):
    """Get current stock/index price with rate limiting"""
    try:
        # Handle Nifty and Sensex specially with Indian exchange APIs
        if symbol == "^NSEI":  # Nifty
            indices_data = await stock_scraper.scrape_nifty_sensex_data()
            return indices_data.get("nifty")
        elif symbol == "^BSESN":  # Sensex
            indices_data = await stock_scraper.scrape_nifty_sensex_data()
            return indices_data.get("sensex")
        
        # For other stocks, use the existing method
        if not symbol.startswith('^') and not symbol.endswith('.NS'):
            symbol = f"{symbol}.NS"
        
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        params = {'interval': '1d', 'range': '1d'}
        
        response = rate_limited_request(url, params)
        data = response.json()
        
        result = data['chart']['result'][0]
        meta = result['meta']
        
        return {
            "symbol": symbol,
            "price": meta.get('regularMarketPrice'),
            "change": meta.get('regularMarketPrice', 0) - meta.get('chartPreviousClose', 0),
            "change_percent": ((meta.get('regularMarketPrice', 0) / meta.get('chartPreviousClose', 1)) - 1) * 100,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching current price for {symbol}: {e}")
        return None

def compute_indicators(df: pd.DataFrame):
    """Compute technical indicators for stocks - FIXED VERSION"""
    if df.empty:
        return {
            "latest_price": 0,
            "ma_5": None,
            "ma_20": None,
            "ma_50": None,
            "volatility": 0.02,
            "rsi": 50,
            "recent_return_5d": 0,
            "recent_return_20d": 0,
            "price_change_pct": 0
        }
    
    # Create copy to avoid warnings
    df = df.copy()
    
    # Use close price
    df['price'] = df['close']
    
    # Moving averages
    df['ma_5'] = df['price'].rolling(5).mean()
    df['ma_20'] = df['price'].rolling(20).mean()
    df['ma_50'] = df['price'].rolling(50).mean()
    
    # Returns and volatility
    df['returns'] = df['price'].pct_change()
    df['volatility'] = df['returns'].rolling(20).std()
    
    # RSI
    delta = df['price'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # MACD
    df['ema_12'] = df['price'].ewm(span=12).mean()
    df['ema_26'] = df['price'].ewm(span=26).mean()
    df['macd'] = df['ema_12'] - df['ema_26']
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    
    # Bollinger Bands
    df['bb_middle'] = df['price'].rolling(20).mean()
    df['bb_std'] = df['price'].rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + (2 * df['bb_std'])
    df['bb_lower'] = df['bb_middle'] - (2 * df['bb_std'])
    
    latest = df.iloc[-1]
    
    return {
        "latest_price": float(latest['price']),
        "ma_5": float(latest['ma_5']) if pd.notna(latest['ma_5']) else None,
        "ma_20": float(latest['ma_20']) if pd.notna(latest['ma_20']) else None,
        "ma_50": float(latest['ma_50']) if pd.notna(latest['ma_50']) else None,
        "volatility": float(latest['volatility']) if pd.notna(latest['volatility']) else 0.02,
        "rsi": float(latest['rsi']) if pd.notna(latest['rsi']) else 50,
        "macd": float(latest['macd']) if pd.notna(latest['macd']) else None,
        "macd_signal": float(latest['macd_signal']) if pd.notna(latest['macd_signal']) else None,
        "bb_upper": float(latest['bb_upper']) if pd.notna(latest['bb_upper']) else None,
        "bb_lower": float(latest['bb_lower']) if pd.notna(latest['bb_lower']) else None,
        "recent_return_5d": float(df['returns'].tail(5).mean()) if len(df) >= 5 else 0,
        "recent_return_20d": float(df['returns'].tail(20).mean()) if len(df) >= 20 else 0,
        "price_change_pct": float((latest['price'] / df.iloc[0]['price'] - 1) * 100),
        "volume": int(latest['volume']) if pd.notna(latest['volume']) else None
    }
