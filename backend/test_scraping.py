"""
Test script to verify the updated stock scraping functionality
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services import stock_scraper, stock_service, stock_recommendations


async def test_scraping():
    print("Testing updated stock scraping functionality...\n")
    
    # Test 1: Test Nifty and Sensex scraping
    print("1. Testing Nifty and Sensex scraping:")
    try:
        indices_data = await stock_scraper.scrape_nifty_sensex_data()
        print(f"   Nifty: {indices_data.get('nifty', 'N/A')}")
        print(f"   Sensex: {indices_data.get('sensex', 'N/A')}")
        print("   ✅ Nifty/Sensex scraping working\n")
    except Exception as e:
        print(f"   ❌ Error in Nifty/Sensex scraping: {e}\n")
    
    # Test 2: Test trending stocks scraping
    print("2. Testing trending stocks scraping:")
    try:
        trending_stocks = await stock_scraper.get_top_trending_stocks(limit=10)
        print(f"   Retrieved {len(trending_stocks)} trending stocks")
        if trending_stocks:
            for i, stock in enumerate(trending_stocks[:3]):  # Show first 3
                print(f"   {i+1}. {stock.get('name')} ({stock.get('symbol')}): ₹{stock.get('price')} ({stock.get('change_percent', 0):+.2f}%)")
        print("   ✅ Trending stocks scraping working\n")
    except Exception as e:
        print(f"   ❌ Error in trending stocks scraping: {e}\n")
    
    # Test 3: Test stock recommendations with real data
    print("3. Testing stock recommendations with real scraped data:")
    try:
        recommendations = stock_recommendations.get_top_stock_picks()
        print(f"   Top Buys: {len(recommendations.get('top_buys', []))}")
        print(f"   Top Sells: {len(recommendations.get('top_sells', []))}")
        print(f"   Market Trend: {recommendations.get('market_trend', 'N/A')}")
        
        # Display sample recommendations
        top_buys = recommendations.get('top_buys', [])
        if top_buys:
            print("   Sample Buy Recommendations:")
            for i, rec in enumerate(top_buys[:2]):
                print(f"     {i+1}. {rec.get('name')} ({rec.get('symbol')}): {rec.get('recommendation')} - {rec.get('change_percent', 0):+.2f}%")
        
        print("   ✅ Stock recommendations working with real data\n")
    except Exception as e:
        print(f"   ❌ Error in stock recommendations: {e}\n")
    
    # Test 4: Test Nifty/Sensex fetch via stock service
    print("4. Testing Nifty/Sensex fetch via stock service:")
    try:
        nifty = await stock_service.fetch_current_price("^NSEI")
        sensex = await stock_service.fetch_current_price("^BSESN")
        print(f"   Nifty: {nifty}")
        print(f"   Sensex: {sensex}")
        print("   ✅ Stock service Nifty/Sensex fetch working\n")
    except Exception as e:
        print(f"   ❌ Error in stock service Nifty/Sensex fetch: {e}\n")

    print("Testing completed!")


if __name__ == "__main__":
    asyncio.run(test_scraping())