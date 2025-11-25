#!/usr/bin/env python3
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append('.')

from database import database
import firebase_admin
from firebase_admin import credentials

async def test_database():
    print("🔥 Testing Firebase Database Connection...")
    
    # Test Firebase initialization
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(os.getenv("FIREBASE_SERVICE_ACCOUNT"))
            firebase_admin.initialize_app(cred)
        print("✅ Firebase initialized successfully")
    except Exception as e:
        print(f"❌ Firebase initialization error: {e}")
        return
    
    # Test database connection
    db = database.get_db()
    if db:
        print("✅ Database connection established")
    else:
        print("❌ Database connection failed")
        return
    
    # Test creating a chat session
    try:
        print("\n📝 Testing chat session creation...")
        user_id = "test_user_123"
        chat_id = await database.create_chat_session(user_id, "Test Chat")
        print(f"✅ Chat session created: {chat_id}")
        
        # Test saving a message
        print("\n💬 Testing message saving...")
        await database.save_message(
            user_id=user_id,
            chat_id=chat_id,
            message="Hello, this is a test message",
            response="This is a test response from NovaX AI",
            agent_type="NovaX Assistant"
        )
        print("✅ Message saved successfully")
        
        # Test retrieving messages
        print("\n📖 Testing message retrieval...")
        messages = await database.get_chat_messages(chat_id)
        print(f"✅ Retrieved {len(messages)} messages")
        
        if messages:
            for msg in messages:
                print(f"   - Message: {msg['message'][:50]}...")
                print(f"   - Response: {msg['response'][:50]}...")
        
        # Test retrieving user chats
        print("\n📂 Testing chat history retrieval...")
        chats = await database.get_user_chats(user_id)
        print(f"✅ Retrieved {len(chats)} chats for user")
        
        if chats:
            for chat in chats:
                print(f"   - Chat: {chat['title']} (ID: {chat['id']})")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        await database.delete_chat(chat_id)
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Database operation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database())