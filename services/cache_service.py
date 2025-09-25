import json
import time
from typing import Any, Dict, Optional
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class CacheService:
    """
    Advanced in-memory caching service with TTL support
    Optimized for the 5-minute cache requirement
    """
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes = 300 seconds
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        logger.info(f"🗄️ Cache service initialized with {default_ttl}s TTL")
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry has expired"""
        current_time = time.time()
        return current_time > cache_entry["expires_at"]
    
    def _cleanup_expired(self):
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self._cache.items()
            if current_time > value["expires_at"]
        ]
        
        for key in expired_keys:
            del self._cache[key]
            logger.debug(f"🧹 Removed expired cache entry: {key}")
        
        if expired_keys:
            logger.info(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache if exists and not expired
        """
        async with self._lock:
            # Clean up expired entries
            self._cleanup_expired()
            
            if key not in self._cache:
                logger.debug(f"❌ Cache miss: {key}")
                return None
            
            cache_entry = self._cache[key]
            
            if self._is_expired(cache_entry):
                del self._cache[key]
                logger.debug(f"⏰ Cache expired and removed: {key}")
                return None
            
            # Update access stats
            cache_entry["access_count"] += 1
            cache_entry["last_accessed"] = time.time()
            
            logger.debug(f"✅ Cache hit: {key} (accessed {cache_entry['access_count']} times)")
            return cache_entry["data"]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store value in cache with TTL
        """
        if ttl is None:
            ttl = self.default_ttl
        
        current_time = time.time()
        expires_at = current_time + ttl
        
        async with self._lock:
            self._cache[key] = {
                "data": value,
                "created_at": current_time,
                "expires_at": expires_at,
                "access_count": 0,
                "last_accessed": None,
                "ttl": ttl
            }
            
            logger.debug(f"💾 Cached: {key} (TTL: {ttl}s, expires: {datetime.fromtimestamp(expires_at)})")
    
    async def delete(self, key: str) -> bool:
        """
        Delete specific key from cache
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"🗑️ Deleted cache entry: {key}")
                return True
            return False
    
    async def clear(self) -> None:
        """
        Clear all cache entries
        """
        async with self._lock:
            cache_size = len(self._cache)
            self._cache.clear()
            logger.info(f"🧹 Cleared entire cache ({cache_size} entries)")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        """
        async with self._lock:
            self._cleanup_expired()
            
            total_entries = len(self._cache)
            current_time = time.time()
            
            stats = {
                "total_entries": total_entries,
                "default_ttl": self.default_ttl,
                "entries": {}
            }
            
            for key, entry in self._cache.items():
                remaining_ttl = max(0, entry["expires_at"] - current_time)
                stats["entries"][key] = {
                    "created_at": datetime.fromtimestamp(entry["created_at"]).isoformat(),
                    "expires_at": datetime.fromtimestamp(entry["expires_at"]).isoformat(),
                    "remaining_ttl": round(remaining_ttl, 2),
                    "access_count": entry["access_count"],
                    "last_accessed": datetime.fromtimestamp(entry["last_accessed"]).isoformat() if entry["last_accessed"] else None,
                    "data_size": len(str(entry["data"]))  # Rough size estimate
                }
            
            return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check for cache service
        """
        async with self._lock:
            self._cleanup_expired()
            
            return {
                "status": "healthy",
                "active_entries": len(self._cache),
                "default_ttl": self.default_ttl,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_current_time(self) -> str:
        """Get current timestamp"""
        return datetime.now().isoformat()
    
    async def close(self):
        """Cleanup method for graceful shutdown"""
        await self.clear()
        logger.info("🛑 Cache service closed")