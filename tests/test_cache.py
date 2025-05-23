"""Tests for cache functionality."""

import os
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from utils.cache import Cache

class TestCache(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.test_dir, "test_cache.json")
        self.cache = Cache(self.cache_file)

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        os.rmdir(self.test_dir)

    def test_set_get(self):
        """Test basic set and get operations."""
        # Test setting and getting a value
        self.cache.set("test_key", "test_value")
        self.assertEqual(self.cache.get("test_key"), "test_value")
        
        # Test getting a nonexistent key
        self.assertIsNone(self.cache.get("nonexistent"))
        
        # Test setting and getting with expiry
        self.cache.set("expiring_key", "expiring_value", expiry_seconds=1)
        self.assertEqual(self.cache.get("expiring_key"), "expiring_value")

    def test_expiry(self):
        """Test cache expiry."""
        # Set a value with 1 second expiry
        self.cache.set("expiring", "value", expiry_seconds=1)
        
        # Wait for expiry
        import time
        time.sleep(1.1)
        
        # Value should be None after expiry
        self.assertIsNone(self.cache.get("expiring"))

    def test_clear(self):
        """Test clearing the cache."""
        # Set multiple values
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        # Clear the cache
        self.cache.clear()
        
        # All values should be None
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))

    def test_remove(self):
        """Test removing specific keys."""
        # Set multiple values
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        
        # Remove one key
        self.cache.remove("key1")
        
        # Removed key should be None, other key should remain
        self.assertIsNone(self.cache.get("key1"))
        self.assertEqual(self.cache.get("key2"), "value2")

    def test_persistence(self):
        """Test cache persistence to disk."""
        # Set some values
        self.cache.set("persistent1", "value1")
        self.cache.set("persistent2", "value2")
        
        # Create a new cache instance with the same file
        new_cache = Cache(self.cache_file)
        
        # Values should be loaded from disk
        self.assertEqual(new_cache.get("persistent1"), "value1")
        self.assertEqual(new_cache.get("persistent2"), "value2")

    def test_max_size(self):
        """Test cache size limits."""
        # Set cache with small max size
        small_cache = Cache(self.cache_file, max_size=2)
        
        # Add items up to and beyond max size
        small_cache.set("key1", "value1")
        small_cache.set("key2", "value2")
        small_cache.set("key3", "value3")  # This should evict the oldest item
        
        # Oldest item should be evicted
        self.assertIsNone(small_cache.get("key1"))
        self.assertEqual(small_cache.get("key2"), "value2")
        self.assertEqual(small_cache.get("key3"), "value3")

    def test_invalid_operations(self):
        """Test invalid cache operations."""
        # Test setting None as key
        with self.assertRaises(ValueError):
            self.cache.set(None, "value")
        
        # Test setting None as value
        with self.assertRaises(ValueError):
            self.cache.set("key", None)
        
        # Test negative expiry time
        with self.assertRaises(ValueError):
            self.cache.set("key", "value", expiry_seconds=-1)
        
        # Test getting with None key
        with self.assertRaises(ValueError):
            self.cache.get(None)

    def test_cleanup(self):
        """Test automatic cleanup of expired items."""
        # Set items with different expiry times
        self.cache.set("no_expiry", "value1")
        self.cache.set("short_expiry", "value2", expiry_seconds=1)
        self.cache.set("long_expiry", "value3", expiry_seconds=10)
        
        # Wait for short expiry
        import time
        time.sleep(1.1)
        
        # Trigger cleanup by getting a value
        self.cache.get("no_expiry")
        
        # Check state after cleanup
        self.assertEqual(self.cache.get("no_expiry"), "value1")
        self.assertIsNone(self.cache.get("short_expiry"))
        self.assertEqual(self.cache.get("long_expiry"), "value3") 