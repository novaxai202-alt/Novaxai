#!/usr/bin/env python3
"""
Test script for NovaX AI real-time features
"""

import asyncio
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health endpoint with real-time info"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check Passed")
            print(f"   Service: {data['service']}")
            print(f"   Current Time: {data['current_time']}")
            print(f"   Features: {', '.join(data['features'])}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_realtime_endpoint():
    """Test the real-time information endpoint"""
    print("\n🕐 Testing Real-time Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/realtime")
        if response.status_code == 200:
            data = response.json()
            print("✅ Real-time Info Retrieved")
            print(f"   Current Date: {data['datetime']['current_date']}")
            print(f"   UTC Time: {data['datetime']['current_time_utc']}")
            print(f"   Unix Timestamp: {data['datetime']['unix_timestamp']}")
            print("   Timezones:")
            for tz, time_str in data['datetime']['timezones'].items():
                print(f"     {tz}: {time_str}")
        else:
            print(f"❌ Real-time endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Real-time endpoint error: {e}")

def test_search_endpoint():
    """Test the enhanced search endpoint"""
    print("\n🔍 Testing Enhanced Search Endpoint...")
    try:
        search_data = {
            "query": "latest AI news today",
            "num_results": 3,
            "include_datetime": True
        }
        response = requests.post(f"{BASE_URL}/api/search", json=search_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Search Completed")
            print(f"   Query: {data['query']}")
            print(f"   Results Found: {len(data['results'])}")
            print(f"   Source: {data['source']}")
            if data.get('realtime_context'):
                print(f"   Search Time: {data['realtime_context']['current_utc']}")
            
            # Show first result
            if data['results']:
                result = data['results'][0]
                print(f"\n   First Result:")
                print(f"     Title: {result['title'][:80]}...")
                print(f"     Source: {result['source']}")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Search error: {e}")

def test_chat_with_realtime():
    """Test chat endpoint with real-time queries"""
    print("\n💬 Testing Chat with Real-time Queries...")
    
    # Test queries that should trigger NovaX Explorer
    test_queries = [
        "What time is it now?",
        "What's today's date?",
        "Search for latest tech news",
        "What's happening in AI today?"
    ]
    
    for query in test_queries:
        print(f"\n   Testing: '{query}'")
        try:
            chat_data = {
                "message": query,
                "token": "demo_token"  # Using demo mode
            }
            response = requests.post(f"{BASE_URL}/chat", json=chat_data)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Agent: {data['agent_type']}")
                print(f"   📝 Response: {data['response'][:100]}...")
                if data.get('suggestions'):
                    print(f"   💡 Suggestions: {', '.join(data['suggestions'])}")
            else:
                print(f"   ❌ Chat failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Chat error: {e}")

def main():
    """Run all tests"""
    print("🚀 NovaX AI Real-time Features Test Suite")
    print("=" * 50)
    
    test_health_endpoint()
    test_realtime_endpoint()
    test_search_endpoint()
    test_chat_with_realtime()
    
    print("\n" + "=" * 50)
    print("✨ Test Suite Completed!")
    print("\nTo start the server, run:")
    print("cd backend && uvicorn main:app --reload --port 8000")

if __name__ == "__main__":
    main()