import requests
import json
from datetime import datetime

def test_dashboard():
    """Test dashboard endpoint and display results"""
    print("="*70)
    print("Testing AI-Powered Market Dashboard")
    print("="*70)
    
    try:
        response = requests.get('http://localhost:8000/dashboard', timeout=60)
        
        print(f"\n✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n" + "="*70)
            print("📊 MARKET SNAPSHOT")
            print("="*70)
            
            # Gold
            gold = data.get('gold', {})
            print(f"\n🥇 GOLD:")
            print(f"   Price: ₹{gold.get('price', 0):,.2f} {gold.get('unit', '')}")
            print(f"   AI Prediction: {gold.get('prediction', 'N/A')} ({gold.get('confidence', 0):.1f}% confidence)")
            
            # Silver
            silver = data.get('silver', {})
            print(f"\n🥈 SILVER:")
            print(f"   Price: ₹{silver.get('price', 0):,.2f} {silver.get('unit', '')}")
            print(f"   AI Prediction: {silver.get('prediction', 'N/A')} ({silver.get('confidence', 0):.1f}% confidence)")
            
            # Stock Indices
            nifty = data.get('nifty', {})
            if nifty:
                print(f"\n📈 NIFTY 50:")
                print(f"   Price: {nifty.get('price', 0):,.2f}")
                print(f"   Change: {nifty.get('change_percent', 0):+.2f}%")
            
            sensex = data.get('sensex', {})
            if sensex:
                print(f"\n📈 SENSEX:")
                print(f"   Price: {sensex.get('price', 0):,.2f}")
                print(f"   Change: {sensex.get('change_percent', 0):+.2f}%")
            
            # Market Sentiment
            sentiment = data.get('market_sentiment', {})
            print(f"\n💭 MARKET SENTIMENT:")
            print(f"   Overall: {sentiment.get('label', 'N/A').upper()}")
            print(f"   Score: {sentiment.get('overall_sentiment', 0):+.3f}")
            print(f"   Confidence: {sentiment.get('confidence', 0):.1f}%")
            print(f"   Articles Analyzed: {sentiment.get('article_count', 0)}")
            print(f"   Positive: {sentiment.get('positive_count', 0)} | Negative: {sentiment.get('negative_count', 0)} | Neutral: {sentiment.get('neutral_count', 0)}")
            
            # AI Insights
            ai_insights = data.get('ai_insights', '')
            print(f"\n🤖 AI MARKET INSIGHTS:")
            print(f"   {ai_insights[:300]}...")
            
            # Top News
            news = data.get('top_news', [])
            print(f"\n📰 TOP NEWS HEADLINES ({len(news)} articles):")
            for i, article in enumerate(news[:5], 1):
                print(f"   {i}. {article.get('title', 'N/A')[:70]}...")
                print(f"      Source: {article.get('source', 'N/A')}")
            
            # Last Updated
            last_updated = data.get('last_updated', '')
            print(f"\n🕐 Last Updated: {last_updated}")
            
            print("\n" + "="*70)
            print("✅ Dashboard Test PASSED")
            print("="*70)
            
            return True
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n⏱️ Request timed out (>60s). This is normal for first request.")
        print("Try again - subsequent requests will be faster due to caching.")
        return False
        
    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        return False

def test_chatbot():
    """Test chatbot endpoint"""
    print("\n" + "="*70)
    print("Testing AI Chatbot")
    print("="*70)
    
    questions = [
        "What is the current gold price in India?",
        "Should I buy TCS stock?",
        "What's happening with silver prices?"
    ]
    
    for i, question in enumerate(questions[:1], 1):  # Test first question only
        print(f"\n💬 Question {i}: {question}")
        
        try:
            response = requests.post(
                'http://localhost:8000/chatbot',
                json={"question": question},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n🤖 Answer:")
                print(f"   {data.get('answer', 'N/A')[:400]}...")
                
                sources = data.get('sources', [])
                if sources:
                    print(f"\n📚 Sources ({len(sources)}):")
                    for j, source in enumerate(sources, 1):
                        print(f"   {j}. {source.get('title', 'N/A')}")
                        print(f"      URL: {source.get('url', 'N/A')}")
                
                print("\n✅ Chatbot test PASSED")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Chatbot test FAILED: {e}")

if __name__ == "__main__":
    print("\n🚀 Starting API Tests...\n")
    
    # Test 1: Dashboard
    dashboard_ok = test_dashboard()
    
    # Test 2: Chatbot (if dashboard works)
    if dashboard_ok:
        test_chatbot()
    
    print("\n" + "="*70)
    print("🎯 All Tests Complete!")
    print("="*70)
    print("\nNext Steps:")
    print("1. If tests passed → Ready for React frontend!")
    print("2. If errors → Check logs in uvicorn terminal")
    print("3. First request is slow (30-60s) - subsequent requests are cached (<5s)")
    print("\n" + "="*70)
