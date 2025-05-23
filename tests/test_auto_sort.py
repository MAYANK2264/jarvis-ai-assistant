"""Tests for auto_sort functionality."""

import os
import shutil
import tempfile
import unittest
from commands.auto_sort import auto_sort_files, FILE_CATEGORIES

class TestAutoSort(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_files = {
            "image.jpg": "Images",
            "document.pdf": "Documents",
            "video.mp4": "Videos",
            "song.mp3": "Music",
            "archive.zip": "Archives",
            "script.py": "Code",
            "unknown.xyz": "Others"
        }
        # Create test files
        for filename in self.test_files:
            with open(os.path.join(self.test_dir, filename), 'w') as f:
                f.write("test content")

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_auto_sort_nonexistent_folder(self):
        """Test sorting a nonexistent folder."""
        result = auto_sort_files("/nonexistent/folder")
        self.assertEqual(result, "The specified folder does not exist.")

    def test_auto_sort_empty_folder(self):
        """Test sorting an empty folder."""
        empty_dir = tempfile.mkdtemp()
        result = auto_sort_files(empty_dir)
        self.assertEqual(result, "Auto-sorting complete. Moved 0 file(s).")
        shutil.rmtree(empty_dir)

    def test_auto_sort_files(self):
        """Test sorting files into categories."""
        result = auto_sort_files(self.test_dir)
        self.assertIn("Auto-sorting complete. Moved 7 file(s).", result)

        # Verify each file is in the correct category folder
        for filename, category in self.test_files.items():
            category_path = os.path.join(self.test_dir, category)
            file_path = os.path.join(category_path, filename)
            self.assertTrue(os.path.exists(file_path), f"{filename} not found in {category}")

    def test_auto_sort_mixed_case_extensions(self):
        """Test sorting files with mixed case extensions."""
        mixed_files = {
            "image.JPG": "Images",
            "doc.PDF": "Documents",
            "code.PY": "Code"
        }
        
        # Create test files with mixed case extensions
        for filename in mixed_files:
            with open(os.path.join(self.test_dir, filename), 'w') as f:
                f.write("test content")

        result = auto_sort_files(self.test_dir)
        self.assertIn("Auto-sorting complete.", result)

        # Verify files are sorted correctly regardless of extension case
        for filename, category in mixed_files.items():
            category_path = os.path.join(self.test_dir, category)
            file_path = os.path.join(category_path, filename)
            self.assertTrue(os.path.exists(file_path), f"{filename} not found in {category}")

    def test_auto_sort_duplicate_files(self):
        """Test sorting when destination already has files with same names."""
        # Create a file
        filename = "test.jpg"
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, 'w') as f:
            f.write("original content")

        # Create Images directory and put a file with same name
        images_dir = os.path.join(self.test_dir, "Images")
        os.makedirs(images_dir)
        with open(os.path.join(images_dir, filename), 'w') as f:
            f.write("existing content")

        # Try to sort
        result = auto_sort_files(self.test_dir)
        self.assertIn("Auto-sorting complete.", result)

        # Verify both files exist (one should be renamed)
        files_in_images = os.listdir(images_dir)
        self.assertEqual(len(files_in_images), 2, "Expected both original and new file") 