import asyncio
import random
import time
from typing import List, Dict, Optional
import google.generativeai as genai
from dataclasses import dataclass
import logging

@dataclass
class APIKeyStatus:
    key: str
    last_used: float
    request_count: int
    is_available: bool = True
    cooldown_until: float = 0

class GeminiAPIPool:
    def __init__(self, api_keys: List[str]):
        self.api_keys = api_keys
        self.key_status: Dict[str, APIKeyStatus] = {}
        self.current_index = 0
        self.lock = asyncio.Lock()
        
        # Initialize key status
        for key in api_keys:
            self.key_status[key] = APIKeyStatus(
                key=key,
                last_used=0,
                request_count=0
            )
        
        # Rate limiting settings
        self.max_requests_per_minute = 60
        self.cooldown_duration = 60  # seconds
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def get_available_key(self) -> Optional[str]:
        """Get next available API key with load balancing"""
        async with self.lock:
            current_time = time.time()
            
            # Reset cooldowns
            for status in self.key_status.values():
                if status.cooldown_until < current_time:
                    status.is_available = True
                    status.request_count = 0
            
            # Find available keys
            available_keys = [
                status for status in self.key_status.values() 
                if status.is_available and status.request_count < self.max_requests_per_minute
            ]
            
            if not available_keys:
                # All keys are rate limited, wait for cooldown
                self.logger.warning("All API keys rate limited, waiting...")
                return None
            
            # Round-robin selection with least recently used preference
            available_keys.sort(key=lambda x: (x.request_count, x.last_used))
            selected_key = available_keys[0].key
            
            # Update usage stats
            self.key_status[selected_key].last_used = current_time
            self.key_status[selected_key].request_count += 1
            
            return selected_key
    
    async def mark_key_failed(self, api_key: str, error_type: str = "rate_limit"):
        """Mark key as failed and set cooldown"""
        async with self.lock:
            if api_key in self.key_status:
                status = self.key_status[api_key]
                status.is_available = False
                status.cooldown_until = time.time() + self.cooldown_duration
                self.logger.warning(f"API key marked as failed: {error_type}")
    
    async def generate_content_with_retry(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Generate content with automatic retry across different API keys"""
        for attempt in range(max_retries):
            api_key = await self.get_available_key()
            
            if not api_key:
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # Brief wait before retry
                    continue
                else:
                    raise Exception("All API keys exhausted")
            
            try:
                # Configure Gemini with selected key
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Generate content
                response = model.generate_content(prompt)
                return response.text
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if "quota" in error_msg or "rate" in error_msg:
                    await self.mark_key_failed(api_key, "rate_limit")
                elif "invalid" in error_msg:
                    await self.mark_key_failed(api_key, "invalid_key")
                else:
                    self.logger.error(f"Unexpected error with key: {e}")
                
                if attempt == max_retries - 1:
                    raise e
                
                await asyncio.sleep(0.5)  # Brief delay before retry
        
        return None
    
    async def generate_content_stream_with_retry(self, prompt: str, max_retries: int = 3):
        """Generate streaming content with automatic retry"""
        for attempt in range(max_retries):
            api_key = await self.get_available_key()
            
            if not api_key:
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                else:
                    raise Exception("All API keys exhausted")
            
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                response = model.generate_content(prompt, stream=True)
                return response
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if "quota" in error_msg or "rate" in error_msg:
                    await self.mark_key_failed(api_key, "rate_limit")
                elif "invalid" in error_msg:
                    await self.mark_key_failed(api_key, "invalid_key")
                
                if attempt == max_retries - 1:
                    raise e
                
                await asyncio.sleep(0.5)
        
        return None
    
    def get_pool_status(self) -> Dict:
        """Get current status of all API keys"""
        current_time = time.time()
        status = {
            "total_keys": len(self.api_keys),
            "available_keys": 0,
            "rate_limited_keys": 0,
            "keys": []
        }
        
        for key_status in self.key_status.values():
            key_info = {
                "key_id": key_status.key[-8:],  # Last 8 chars for identification
                "available": key_status.is_available,
                "request_count": key_status.request_count,
                "cooldown_remaining": max(0, key_status.cooldown_until - current_time)
            }
            
            if key_status.is_available:
                status["available_keys"] += 1
            else:
                status["rate_limited_keys"] += 1
            
            status["keys"].append(key_info)
        
        return status

# Global pool instance
gemini_pool: Optional[GeminiAPIPool] = None

def initialize_gemini_pool(api_keys: List[str]):
    """Initialize the global Gemini API pool"""
    global gemini_pool
    gemini_pool = GeminiAPIPool(api_keys)
    return gemini_pool

def get_gemini_pool() -> GeminiAPIPool:
    """Get the global Gemini API pool instance"""
    global gemini_pool
    if gemini_pool is None:
        raise Exception("Gemini pool not initialized")
    return gemini_pool