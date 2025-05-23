"""Tests for database functionality."""

import os
import json
import sqlite3
import tempfile
import unittest
from datetime import datetime
from utils.database import DatabaseManager, get_db_manager

class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test.db")
        # Reset the singleton instance
        DatabaseManager._instance = None
        DatabaseManager._initialized = False
        self.db = DatabaseManager(db_path=self.db_path)

    def tearDown(self):
        """Clean up test environment."""
        # Close any open connections
        if hasattr(self, 'db'):
            with self.db.get_connection() as conn:
                conn.close()
        # Reset the singleton instance
        DatabaseManager._instance = None
        DatabaseManager._initialized = False
        # Remove test files
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            os.rmdir(self.test_dir)
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not clean up test files: {e}")

    def test_singleton_pattern(self):
        """Test that DatabaseManager follows singleton pattern."""
        db1 = DatabaseManager()
        db2 = DatabaseManager()
        self.assertIs(db1, db2)

    def test_table_creation(self):
        """Test that required tables are created."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check file_metadata table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='file_metadata'
            """)
            self.assertIsNotNone(cursor.fetchone())
            
            # Check operation_log table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='operation_log'
            """)
            self.assertIsNotNone(cursor.fetchone())
            
            # Check performance_metrics table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='performance_metrics'
            """)
            self.assertIsNotNone(cursor.fetchone())

    def test_log_operation(self):
        """Test logging file operations."""
        self.db.log_operation("COPY", "/source/path", "/target/path", "SUCCESS")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM operation_log")
            row = cursor.fetchone()
            
            self.assertEqual(row[1], "COPY")
            self.assertEqual(row[2], "/source/path")
            self.assertEqual(row[3], "/target/path")
            self.assertEqual(row[4], "SUCCESS")

    def test_log_performance(self):
        """Test logging performance metrics."""
        self.db.log_performance("SEARCH", 100, 1024)
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM performance_metrics")
            row = cursor.fetchone()
            
            self.assertEqual(row[1], "SEARCH")
            self.assertEqual(row[2], 100)
            self.assertEqual(row[3], 1024)

    def test_search_files(self):
        """Test file search functionality."""
        # Add test file metadata
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO file_metadata 
                (path, name, size, created_at, modified_at, file_type, is_directory, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "/test/path/doc.txt",
                "doc.txt",
                1024,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                "text",
                False,
                json.dumps(["important", "work"]),
                json.dumps({"author": "test"})
            ))
            conn.commit()
        
        # Test search by name
        results = self.db.search_files("doc")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "doc.txt")
        
        # Test search by tag
        results = self.db.search_files("important")
        self.assertEqual(len(results), 1)
        
        # Test search by metadata
        results = self.db.search_files("test")
        self.assertEqual(len(results), 1)
        
        # Test search with no results
        results = self.db.search_files("nonexistent")
        self.assertEqual(len(results), 0)

    def test_error_handling(self):
        """Test error handling in database operations."""
        # Test with invalid SQL
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            with self.assertRaises(sqlite3.OperationalError):
                cursor.execute("INVALID SQL")
        
        # Test with invalid file path
        results = self.db.search_files(None)
        self.assertEqual(results, []) 