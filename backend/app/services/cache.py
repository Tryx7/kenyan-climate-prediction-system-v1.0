import os
import json
import redis.asyncio as redis
from typing import Optional, Any

class CacheService:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.ttl = int(os.getenv("CACHE_TTL", "3600"))
        self._redis = None

    async def _get_redis(self):
        if self._redis is None:
            self._redis = await redis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def get(self, key: str) -> Optional[Any]:
        try:
            r = await self._get_redis()
            data = await r.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        try:
            r = await self._get_redis()
            await r.setex(key, ttl or self.ttl, json.dumps(value, default=str))
        except Exception:
            pass

    async def delete(self, key: str):
        try:
            r = await self._get_redis()
            await r.delete(key)
        except Exception:
            pass

    async def clear_pattern(self, pattern: str):
        try:
            r = await self._get_redis()
            keys = await r.keys(pattern)
            if keys:
                await r.delete(*keys)
        except Exception:
            pass

# Global cache instance
_cache_instance = None

def get_cache():
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheService()
    return _cache_instance
