import unittest
import os
import shutil
import tempfile
from pathlib import Path
import time
from typing import List

from commands.file_manager import (
    create_folder,
    delete_file_or_folder,
    rename_item,
    move_item,
    copy_item,
    search_files,
)
from utils.database import get_db_manager
from utils.retry import Transaction, transactional, retry


class TestFileOperations(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.db = get_db_manager()

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)

    def create_test_files(self, count: int) -> List[str]:
        """Create test files"""
        files = []
        for i in range(count):
            path = os.path.join(self.test_dir, f"test_file_{i}.txt")
            with open(path, "w") as f:
                f.write(f"Test content {i}")
            files.append(path)
        return files

    def test_create_folder(self):
        """Test folder creation"""
        folder_path = os.path.join(self.test_dir, "test_folder")
        result = create_folder(folder_path)
        self.assertTrue(os.path.exists(folder_path))
        self.assertTrue(os.path.isdir(folder_path))

    def test_delete_file(self):
        """Test file deletion"""
        files = self.create_test_files(1)
        file_path = files[0]
        result = delete_file_or_folder(file_path)
        self.assertFalse(os.path.exists(file_path))

    def test_rename_item(self):
        """Test item renaming"""
        files = self.create_test_files(1)
        old_path = files[0]
        new_path = os.path.join(self.test_dir, "renamed_file.txt")
        result = rename_item(old_path, new_path)
        self.assertFalse(os.path.exists(old_path))
        self.assertTrue(os.path.exists(new_path))

    def test_move_item(self):
        """Test item moving"""
        files = self.create_test_files(1)
        source = files[0]
        target_dir = os.path.join(self.test_dir, "target")
        os.makedirs(target_dir)
        target = os.path.join(target_dir, os.path.basename(source))
        result = move_item(source, target)
        self.assertFalse(os.path.exists(source))
        self.assertTrue(os.path.exists(target))

    def test_copy_item(self):
        """Test item copying"""
        files = self.create_test_files(1)
        source = files[0]
        target = os.path.join(self.test_dir, "copied_file.txt")
        result = copy_item(source, target)
        self.assertTrue(os.path.exists(source))
        self.assertTrue(os.path.exists(target))

    def test_search_files(self):
        """Test file searching"""
        files = self.create_test_files(5)
        results = search_files(self.test_dir, name="test_file")
        self.assertEqual(len(results), 5)

    def test_transaction_rollback(self):
        """Test transaction rollback"""
        files = self.create_test_files(2)

        @transactional
        def failing_operation(transaction: Transaction):
            transaction.add_operation(
                "move", move_item, files[0], os.path.join(self.test_dir, "moved.txt")
            )
            transaction.add_operation("delete", delete_file_or_folder, files[1])
            raise Exception("Simulated failure")

        with self.assertRaises(Exception):
            failing_operation()

        # Check files are restored
        self.assertTrue(os.path.exists(files[0]))
        self.assertTrue(os.path.exists(files[1]))

    def test_retry_mechanism(self):
        """Test retry mechanism"""
        attempts = 0

        @retry(max_attempts=3, delay_seconds=0.1)
        def test_operation():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Test error")
            return True

        result = test_operation()
        self.assertTrue(result)
        self.assertEqual(attempts, 3)


class TestFileOperationsPerformance(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db = get_db_manager()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_large_directory_performance(self):
        """Test performance with large directory"""
        start_time = time.time()

        # Create many files
        for i in range(1000):
            path = os.path.join(self.test_dir, f"file_{i}.txt")
            with open(path, "w") as f:
                f.write(f"Content {i}")

        # Measure search performance
        search_start = time.time()
        results = search_files(self.test_dir)
        search_duration = time.time() - search_start

        self.assertLess(search_duration, 1.0)  # Should complete within 1 second


if __name__ == "__main__":
    unittest.main()
