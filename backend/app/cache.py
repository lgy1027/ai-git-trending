"""
Simple in-memory cache implementation.
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Optional
from app.database import ProjectDatabase
from config.settings import RATE_LIMIT_COPY, RATE_LIMIT_EXPORT


class SimpleCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self):
        self._cache = {}

    def get(self, key: str) -> Optional[dict]:
        """Get value from cache."""
        if key in self._cache:
            item = self._cache[key]
            if item['expires_at'] > datetime.now():
                return item['value']
            else:
                # Clean up expired item
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (in seconds)."""
        self._cache[key] = {
            'value': value,
            'expires_at': datetime.now() + timedelta(seconds=ttl)
        }

    def clear(self):
        """Clear all cache."""
        self._cache = {}


class IPRateLimiter:
    """IP-based rate limiter for copy/export operations (database-backed, permanent)."""

    def __init__(self):
        self._db = ProjectDatabase()
        self._limits = {
            'copy': RATE_LIMIT_COPY,
            'export': RATE_LIMIT_EXPORT
        }

    def get_limit(self, action: str) -> int:
        """获取指定操作的限制数量"""
        return self._limits.get(action, 5)

    def check_limit(self, action: str, ip: str) -> tuple[bool, int]:
        """
        检查是否超过限制（永久限制）
        返回: (是否允许, 剩余次数)
        """
        max_count = self.get_limit(action)
        current_count = self._db.get_rate_limit_count(ip, action)
        remaining = max_count - current_count
        return current_count < max_count, remaining

    def increment(self, action: str, ip: str):
        """增加一次计数"""
        max_count = self.get_limit(action)
        self._db.increment_rate_limit(ip, action, max_count)

    def get_remaining(self, action: str, ip: str) -> int:
        """获取剩余次数"""
        max_count = self.get_limit(action)
        current_count = self._db.get_rate_limit_count(ip, action)
        return max(0, max_count - current_count)


# Global cache instance
_cache = SimpleCache()
_rate_limiter = IPRateLimiter()


def get_cache():
    """Get the global cache instance."""
    return _cache


def get_rate_limiter():
    """Get the global rate limiter instance."""
    return _rate_limiter


def generate_cache_key(*args, **kwargs) -> str:
    """Generate a cache key from args and kwargs."""
    key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()
