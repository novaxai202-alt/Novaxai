# NovaX AI Chatbot - Backend

FastAPI backend for NovaX AI Chatbot with Google Gemini integration, real-time search, and Firebase authentication.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your API keys to .env

# Run server
uvicorn main:app --reload --port 8000
```

## 📋 Requirements

- Python 3.8+
- Google Gemini API key
- Firebase service account
- Google Search API (optional)

## 🔧 Environment Variables

```bash
GEMINI_API_KEY=your_gemini_api_key_here
FIREBASE_SERVICE_ACCOUNT=path_to_firebase_service_account.json
GOOGLE_SEARCH_API_KEY=your_google_search_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

## 🌟 Features

- ✅ Google Gemini Pro AI integration
- ✅ Firebase authentication
- ✅ Real-time web search
- ✅ Image generation with Hugging Face
- ✅ Multi-timezone support
- ✅ Enhanced AI personality system
- ✅ Structured reasoning responses
- ✅ Google Drive integration
- ✅ Chat history and memory management

## 🛠 API Endpoints

- `GET /health` - Health check
- `GET /api/realtime` - Current date/time info
- `POST /api/search` - Real-time web search
- `POST /chat` - AI chat with enhanced features
- `GET /agents` - Available AI agents

## 📄 License

MIT License