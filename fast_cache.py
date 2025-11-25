"""
Fast in-memory cache for NovaX AI Platform
Reduces API calls and improves response times
"""

import asyncio
import hashlib
import time
from typing import Dict, Any, Optional
import json

class FastCache:
    """Lightweight in-memory cache with TTL"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.lock = asyncio.Lock()
    
    def _hash_key(self, key: str) -> str:
        """Create hash for cache key"""
        return hashlib.md5(key.encode()).hexdigest()[:16]
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self.lock:
            hashed_key = self._hash_key(key)
            if hashed_key in self.cache:
                entry = self.cache[hashed_key]
                if time.time() < entry['expires']:
                    return entry['value']
                else:
                    del self.cache[hashed_key]
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        async with self.lock:
            hashed_key = self._hash_key(key)
            expires = time.time() + (ttl or self.default_ttl)
            self.cache[hashed_key] = {
                'value': value,
                'expires': expires
            }
    
    async def clear_expired(self) -> None:
        """Remove expired entries"""
        async with self.lock:
            current_time = time.time()
            expired_keys = [
                k for k, v in self.cache.items() 
                if current_time >= v['expires']
            ]
            for key in expired_keys:
                del self.cache[key]
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'memory_usage_kb': len(str(self.cache)) // 1024
        }

# Global cache instances
response_cache = FastCache(default_ttl=300)  # 5 min for responses
search_cache = FastCache(default_ttl=600)    # 10 min for search results
datetime_cache = FastCache(default_ttl=60)   # 1 min for datetime

async def cache_ai_response(prompt: str, response: str) -> None:
    """Cache AI response"""
    await response_cache.set(f"ai:{prompt[:100]}", response)

async def get_cached_response(prompt: str) -> Optional[str]:
    """Get cached AI response"""
    return await response_cache.get(f"ai:{prompt[:100]}")

async def cache_search_results(query: str, results: Dict) -> None:
    """Cache search results"""
    await search_cache.set(f"search:{query}", results)

async def get_cached_search(query: str) -> Optional[Dict]:
    """Get cached search results"""
    return await search_cache.get(f"search:{query}")

# Auto cleanup task
async def cleanup_caches():
    """Periodic cache cleanup"""
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        await response_cache.clear_expired()
        await search_cache.clear_expired()
        await datetime_cache.clear_expired()

# Start cleanup task
asyncio.create_task(cleanup_caches())
