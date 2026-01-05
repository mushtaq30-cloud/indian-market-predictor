import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    CACHE_EXPIRY_MINUTES = int(os.getenv("CACHE_EXPIRY_MINUTES", 15))
    MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", 60))
    
    # AI Configuration - ALL FREE OPTIONS
    AI_PROVIDER = os.getenv("AI_PROVIDER", "groq")  # groq, gemini, huggingface
    
    # Groq (FREE - 30 req/min, no credit card)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    # GROQ_MODEL = "llama-3.1-70b-versatile" # OLD (decommissioned)
    GROQ_MODEL = "llama-3.3-70b-versatile"  # Latest Llama 3.3
    
    # Google Gemini (FREE - 1500 req/day, no credit card)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = "gemini-2.0-flash-exp"
    
    # Hugging Face (FREE - 300 req/hour)
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    
    # Fallback to local processing if no API keys
    USE_LOCAL_FALLBACK = True
    
    # Data sources - ALL FREE
    NSE_API_BASE = "https://query1.finance.yahoo.com/v8/finance/chart"
    
    # Web scraping sources (all free)
    GOLD_SCRAPE_URLS = [
        "https://www.goodreturns.in/gold-rates/",
        "https://www.bankbazaar.com/gold-rate.html"
    ]
    
    SILVER_SCRAPE_URLS = [
        "https://www.goodreturns.in/silver-rates/",
        "https://goldpricez.com/silver-rates/india/gram"
    ]
    
    # News sources (all free RSS)
    RSS_FEEDS = {
        'gold': [
            'https://news.google.com/rss/search?q=gold+price+india&hl=en-IN&gl=IN&ceid=IN:en',
            'https://economictimes.indiatimes.com/commoditysummary/symbol-GOLD.cms?format=rss',
        ],
        'silver': [
            'https://news.google.com/rss/search?q=silver+price+india&hl=en-IN&gl=IN&ceid=IN:en',
        ],
        'stock_market': [
            'https://news.google.com/rss/search?q=india+stock+market+nifty+sensex&hl=en-IN&gl=IN&ceid=IN:en',
            'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
        ],
        'rbi_policy': [
            'https://news.google.com/rss/search?q=RBI+monetary+policy+india&hl=en-IN&gl=IN&ceid=IN:en',
        ],
        'rupee': [
            'https://news.google.com/rss/search?q=rupee+dollar+exchange+rate&hl=en-IN&gl=IN&ceid=IN:en',
        ]
    }

settings = Settings()
