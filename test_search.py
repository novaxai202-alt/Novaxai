#!/usr/bin/env python3
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append('.')

from search_service import novax_search

async def test_search():
    print("🔍 Testing NovaX Search Service...")
    
    # Check API keys
    google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
    
    print(f"Google API Key: {'✅ Set' if google_api_key else '❌ Missing'}")
    print(f"Search Engine ID: {'✅ Set' if search_engine_id else '❌ Missing'}")
    
    if not google_api_key or not search_engine_id:
        print("❌ Missing required API credentials")
        return
    
    # Test search queries
    test_queries = [
        "latest AI news today",
        "current time",
        "breaking news technology",
        "what's happening today"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        try:
            result = await novax_search.search(query, 3)
            
            print(f"   Source: {result.get('source')}")
            print(f"   Error: {result.get('error', 'None')}")
            print(f"   Results: {len(result.get('results', []))}")
            
            if result.get('results'):
                for i, r in enumerate(result['results'][:2], 1):
                    print(f"   {i}. {r['title'][:60]}...")
                    print(f"      {r['snippet'][:80]}...")
            else:
                print("   No results found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_search())