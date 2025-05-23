"""Cache module for storing temporary data."""

import json
import os
import time
from typing import Any, Dict, Optional
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class Cache:
    """Cache class for storing temporary data with expiry."""
    
    def __init__(self, cache_file: Optional[str] = None, max_size: int = 1000):
        """Initialize cache.
        
        Args:
            cache_file: Path to the cache file
            max_size: Maximum number of items in cache
        """
        if max_size <= 0:
            raise ValueError("max_size must be positive")
            
        self.cache_file = cache_file or os.path.join(os.getcwd(), "cache.json")
        self.max_size = max_size
        self._cache: Dict[str, Dict] = OrderedDict()
        self._load_cache()

    def _load_cache(self):
        """Load cache from disk."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    data = json.load(f)
                    self._cache = OrderedDict(data)
            except (json.JSONDecodeError, IOError):
                self._cache = OrderedDict()

    def _save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(dict(self._cache), f)
        except IOError:
            pass

    def set(self, key: str, value: Any, expiry_seconds: Optional[float] = None) -> None:
        """Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to store
            expiry_seconds: Optional expiry time in seconds
        """
        if key is None or value is None:
            raise ValueError("Key and value cannot be None")
            
        if expiry_seconds is not None and expiry_seconds < 0:
            raise ValueError("expiry_seconds must be non-negative")

        # Remove oldest item if cache is full
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)

        self._cache[key] = {
            "value": value,
            "timestamp": time.time(),
            "expiry": expiry_seconds
        }
        self._save_cache()

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            The cached value or None if not found or expired
        """
        if key is None:
            raise ValueError("Key cannot be None")
            
        if key not in self._cache:
            return None

        entry = self._cache[key]
        current_time = time.time()
        expiry = entry["expiry"]

        if expiry is not None and current_time - entry["timestamp"] >= expiry:
            self.remove(key)
            return None

        return entry["value"]

    def remove(self, key: str) -> None:
        """Remove a key from the cache.
        
        Args:
            key: Cache key to remove
        """
        if key in self._cache:
            del self._cache[key]
            self._save_cache()

    def clear(self) -> None:
        """Clear all items from the cache."""
        self._cache.clear()
        self._save_cache()

    def cleanup(self) -> None:
        """Remove all expired items from the cache."""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry["expiry"] is not None and current_time - entry["timestamp"] >= entry["expiry"]
        ]
        for key in expired_keys:
            self.remove(key)


# Global instance
_command_cache = Cache()


def get_command_cache() -> Cache:
    """Get the global cache instance"""
    return _command_cache


def cache_result(ttl: int = 3600):
    """Decorator to cache function results"""

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cache = get_command_cache()

            # Try to get cached result
            result = cache.get(key)
            if result is not None:
                logger.debug(f"Cache hit for {key}")
                return result

            # Calculate and cache result
            result = func(*args, **kwargs)
            cache.set(key, result)
            logger.debug(f"Cache miss for {key}, stored new result")
            return result

        return wrapper

    return decorator


# Example usage of LRU cache for memory-efficient caching
def get_cached_system_info():
    """Example of using LRU cache for system info"""
    # Import here to avoid circular imports
    from commands.system_info import get_system_info

    return get_system_info()
