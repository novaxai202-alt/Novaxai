#!/usr/bin/env python3
import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append('.')

from main import app
from fastapi.testclient import TestClient

def test_complete_flow():
    print("🚀 Testing Complete NovaX AI Flow...")
    
    client = TestClient(app)
    
    # Test health endpoint
    print("\n🏥 Testing health endpoint...")
    response = client.get("/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health check passed")
        print(f"   Service: {data['service']}")
        print(f"   Current time: {data['current_time']}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
    
    # Test real-time info endpoint
    print("\n⏰ Testing real-time info endpoint...")
    response = client.get("/api/realtime")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Real-time info retrieved")
        print(f"   Current UTC: {data['datetime']['current_utc']}")
        print(f"   Timezones: {len(data['datetime']['timezones'])} zones")
    else:
        print(f"❌ Real-time info failed: {response.status_code}")
    
    # Test search endpoint
    print("\n🔍 Testing search endpoint...")
    search_payload = {
        "query": "latest AI news today",
        "num_results": 3,
        "include_datetime": True
    }
    response = client.post("/api/search", json=search_payload)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Search completed")
        print(f"   Query: {data['query']}")
        print(f"   Results: {len(data['results'])}")
        print(f"   Source: {data['source']}")
        if data['results']:
            print(f"   First result: {data['results'][0]['title'][:60]}...")
    else:
        print(f"❌ Search failed: {response.status_code}")
    
    # Test chat endpoint with real-time query
    print("\n💬 Testing chat with real-time query...")
    chat_payload = {
        "message": "What's the latest AI news today?",
        "token": "demo_token"  # Using demo mode
    }
    response = client.post("/chat", json=chat_payload)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat response received")
        print(f"   Agent: {data['agent_type']}")
        print(f"   Response length: {len(data['response'])} chars")
        print(f"   Suggestions: {len(data['suggestions'])}")
        print(f"   Chat ID: {data['chat_id']}")
        
        # Show first 200 chars of response
        print(f"   Preview: {data['response'][:200]}...")
        
        # Test retrieving the saved message
        chat_id = data['chat_id']
        print(f"\n📖 Testing message retrieval for chat {chat_id}...")
        response = client.get(f"/api/chat/{chat_id}/messages")
        if response.status_code == 200:
            messages = response.json()['messages']
            print(f"✅ Retrieved {len(messages)} messages")
            if messages:
                print(f"   Message: {messages[0]['message'][:50]}...")
                print(f"   Response: {messages[0]['response'][:50]}...")
        else:
            print(f"❌ Message retrieval failed: {response.status_code}")
            
    else:
        print(f"❌ Chat failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test agents endpoint
    print("\n🤖 Testing agents endpoint...")
    response = client.get("/agents")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Agents retrieved: {len(data['agents'])}")
        for agent in data['agents'][:3]:
            print(f"   - {agent['name']}: {agent['description']}")
    else:
        print(f"❌ Agents failed: {response.status_code}")

if __name__ == "__main__":
    test_complete_flow()