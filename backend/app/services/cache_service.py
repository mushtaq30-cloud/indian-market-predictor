import json
import time
from typing import Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    """
    Simple in-memory cache with expiration
    For production, use Redis or Memcached
    """
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key not in self._cache:
            return None
        
        # Check expiration
        if key in self._expiry and time.time() > self._expiry[key]:
            # Expired, remove from cache
            del self._cache[key]
            del self._expiry[key]
            logger.debug(f"Cache expired for key: {key}")
            return None
        
        logger.debug(f"Cache hit for key: {key}")
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl_seconds: int = 900):
        """
        Set cache value with TTL (time to live)
        Default: 900 seconds (15 minutes)
        """
        self._cache[key] = value
        self._expiry[key] = time.time() + ttl_seconds
        logger.debug(f"Cache set for key: {key} (TTL: {ttl_seconds}s)")
    
    def delete(self, key: str):
        """Delete cache entry"""
        if key in self._cache:
            del self._cache[key]
        if key in self._expiry:
            del self._expiry[key]
        logger.debug(f"Cache deleted for key: {key}")
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._expiry.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self):
        """Remove all expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self._expiry.items() 
            if current_time > expiry
        ]
        
        for key in expired_keys:
            self.delete(key)
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

# Global cache instance
cache = SimpleCache()

def get_cached_data(key: str) -> Optional[Any]:
    """Helper function to get cached data"""
    return cache.get(key)

def set_cached_data(key: str, value: Any, ttl_seconds: int = 900):
    """Helper function to set cached data"""
    cache.set(key, value, ttl_seconds)

def invalidate_cache(pattern: str = None):
    """
    Invalidate cache entries
    If pattern provided, only delete matching keys
    """
    if pattern:
        keys_to_delete = [
            key for key in cache._cache.keys() 
            if pattern in key
        ]
        for key in keys_to_delete:
            cache.delete(key)
        logger.info(f"Invalidated {len(keys_to_delete)} cache entries matching '{pattern}'")
    else:
        cache.clear()

# Cache key generators
def generate_gold_cache_key(days: int) -> str:
    """Generate cache key for gold data"""
    date_str = datetime.now().strftime("%Y-%m-%d-%H")
    return f"gold_history_{days}_{date_str}"

def generate_stock_cache_key(symbol: str, days: int) -> str:
    """Generate cache key for stock data"""
    date_str = datetime.now().strftime("%Y-%m-%d-%H")
    return f"stock_{symbol}_{days}_{date_str}"

def generate_news_cache_key(topic: str, hours: int) -> str:
    """Generate cache key for news data"""
    # Cache news for shorter duration (30 mins)
    time_str = datetime.now().strftime("%Y-%m-%d-%H-%M")[:16]  # Up to hour-minute
    return f"news_{topic}_{hours}_{time_str}"

def generate_analysis_cache_key(asset: str) -> str:
    """Generate cache key for analysis results"""
    time_str = datetime.now().strftime("%Y-%m-%d-%H-%M")[:16]
    return f"analysis_{asset}_{time_str}"

# Decorator for caching function results
def cached(ttl_seconds: int = 900):
    """
    Decorator to cache function results
    Usage:
        @cached(ttl_seconds=600)
        async def my_function(param):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and args
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Returning cached result for {func.__name__}")
                return cached_result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator

# Background task to cleanup expired cache periodically
def start_cache_cleanup_task():
    """
    Start background task to cleanup expired cache entries
    Call this from main.py on startup
    """
    import asyncio
    
    async def cleanup_loop():
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            cache.cleanup_expired()
    
    return cleanup_loop()