"""Tests for memory manager functionality."""

import os
import tempfile
import unittest
import psutil
import shutil
from utils.memory_manager import MemoryManager, get_memory_manager

class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        # Reset singleton instance
        MemoryManager._instance = None
        self.manager = MemoryManager(threshold_mb=100)

    def tearDown(self):
        """Clean up test environment."""
        try:
            # Clean up any remaining files
            if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
                shutil.rmtree(self.test_dir)
        except (OSError, IOError) as e:
            print(f"Warning: Could not clean up test directory: {e}")
        finally:
            # Reset singleton instance
            MemoryManager._instance = None
            MemoryManager._initialized = False

    def test_singleton_pattern(self):
        """Test that MemoryManager follows singleton pattern."""
        manager1 = MemoryManager()
        manager2 = MemoryManager()
        self.assertIs(manager1, manager2)

    def test_get_memory_usage(self):
        """Test getting current memory usage."""
        usage = self.manager.get_memory_usage()
        self.assertIsInstance(usage, float)
        self.assertGreater(usage, 0)

    def test_check_memory(self):
        """Test memory check functionality."""
        # Set a very high threshold to ensure we're under it
        self.manager.threshold_mb = 100000
        self.assertTrue(self.manager.check_memory())
        
        # Set a very low threshold to ensure we're over it
        self.manager.threshold_mb = 1
        self.assertFalse(self.manager.check_memory())

    def test_cleanup(self):
        """Test memory cleanup."""
        # Create some test files
        test_files = []
        for i in range(5):
            path = os.path.join(self.test_dir, f"test_file_{i}.txt")
            with open(path, "w") as f:
                f.write("x" * 1024 * 1024)  # 1MB file
            test_files.append(path)
        
        # Add files to cleanup list
        for file in test_files:
            self.manager.add_to_cleanup(file)
        
        # Trigger cleanup
        self.manager.cleanup()
        
        # Check that files were deleted
        for file in test_files:
            self.assertFalse(os.path.exists(file))

    def test_monitor_process(self):
        """Test process monitoring."""
        # Start monitoring
        self.manager.start_monitoring()
        
        # Check that monitoring is active
        self.assertTrue(self.manager.is_monitoring)
        
        # Stop monitoring
        self.manager.stop_monitoring()
        
        # Check that monitoring is stopped
        self.assertFalse(self.manager.is_monitoring)

    def test_add_remove_cleanup(self):
        """Test adding and removing files from cleanup list."""
        test_file = os.path.join(self.test_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        # Add file to cleanup
        self.manager.add_to_cleanup(test_file)
        self.assertIn(test_file, self.manager.cleanup_files)
        
        # Remove file from cleanup
        self.manager.remove_from_cleanup(test_file)
        self.assertNotIn(test_file, self.manager.cleanup_files)

    def test_get_process_info(self):
        """Test getting process information."""
        info = self.manager.get_process_info()
        
        # Check that we get the expected information
        self.assertIn("cpu_percent", info)
        self.assertIn("memory_percent", info)
        self.assertIn("num_threads", info)
        self.assertIsInstance(info["cpu_percent"], float)
        self.assertIsInstance(info["memory_percent"], float)
        self.assertIsInstance(info["num_threads"], int)

    def test_global_instance(self):
        """Test global instance getter."""
        manager1 = get_memory_manager()
        manager2 = get_memory_manager()
        self.assertIs(manager1, manager2)
        self.assertIsInstance(manager1, MemoryManager)

    def test_invalid_threshold(self):
        """Test setting invalid memory threshold."""
        # Reset singleton for this test
        MemoryManager._instance = None
        MemoryManager._initialized = False
        
        # Test with zero threshold
        with self.assertRaises(ValueError):
            MemoryManager(threshold_mb=0)
        
        # Test with negative threshold
        with self.assertRaises(ValueError):
            MemoryManager(threshold_mb=-100)
        
        # Reset singleton after test
        MemoryManager._instance = None
        MemoryManager._initialized = False

    def test_cleanup_nonexistent_file(self):
        """Test cleanup with nonexistent file."""
        nonexistent = os.path.join(self.test_dir, "nonexistent.txt")
        self.manager.add_to_cleanup(nonexistent)
        
        # Cleanup should not raise an error
        try:
            self.manager.cleanup()
        except Exception as e:
            self.fail(f"Cleanup raised an exception: {e}")

    def test_process_monitoring_data(self):
        """Test process monitoring data collection."""
        # Start monitoring
        self.manager.start_monitoring()
        
        # Wait for some data to be collected
        import time
        time.sleep(0.1)
        
        # Stop monitoring
        self.manager.stop_monitoring()
        
        # Check that we have monitoring data
        self.assertGreater(len(self.manager.monitoring_data), 0)
        
        # Check data format
        data = self.manager.monitoring_data[0]
        self.assertIn("timestamp", data)
        self.assertIn("cpu_percent", data)
        self.assertIn("memory_percent", data) 