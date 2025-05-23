"""Tests for file versioning functionality."""

import os
import shutil
import tempfile
import unittest
from datetime import datetime
from commands.file_versioning import save_version, list_versions, restore_version, VERSION_FOLDER

class TestFileVersioning(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create test file
        self.test_file = "test_file.txt"
        with open(self.test_file, "w") as f:
            f.write("original content")

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_save_version_nonexistent_file(self):
        """Test saving version of a nonexistent file."""
        result = save_version("nonexistent.txt")
        self.assertEqual(result, "File does not exist.")

    def test_save_version(self):
        """Test saving a file version."""
        result = save_version(self.test_file)
        self.assertIn("Version saved:", result)
        
        # Verify version folder exists
        self.assertTrue(os.path.exists(VERSION_FOLDER))
        
        # Verify version file exists
        versions = os.listdir(VERSION_FOLDER)
        self.assertEqual(len(versions), 1)
        self.assertTrue(versions[0].startswith("test_file.txt_"))

    def test_list_versions_no_folder(self):
        """Test listing versions when version folder doesn't exist."""
        versions = list_versions(self.test_file)
        self.assertEqual(versions, [])

    def test_list_versions(self):
        """Test listing versions of a file."""
        # Save multiple versions
        save_version(self.test_file)
        
        # Modify and save again
        with open(self.test_file, "w") as f:
            f.write("modified content")
        save_version(self.test_file)
        
        versions = list_versions(self.test_file)
        self.assertEqual(len(versions), 2)
        for version in versions:
            self.assertTrue(version.startswith("test_file.txt_"))
            self.assertTrue(len(version.split("_")[-1]) == 14)  # timestamp length

    def test_restore_version(self):
        """Test restoring a file version."""
        # Save initial version
        save_version(self.test_file)
        initial_versions = list_versions(self.test_file)
        
        # Modify file
        with open(self.test_file, "w") as f:
            f.write("modified content")
        
        # Restore version
        version_to_restore = initial_versions[0]
        result = restore_version(self.test_file, version_to_restore.split("_")[-1])
        self.assertIn("restored successfully", result.lower())
        
        # Verify content is restored
        with open(self.test_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "original content")

    def test_restore_nonexistent_version(self):
        """Test restoring a nonexistent version."""
        result = restore_version(self.test_file, "20240101000000")
        self.assertIn("version not found", result.lower()) 