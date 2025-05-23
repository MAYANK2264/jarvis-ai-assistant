"""Tests for file tagging functionality."""

import os
import json
import pytest
from pathlib import Path
from commands.file_manager import tag_file, get_files_by_tag, TAG_FILE

@pytest.fixture
def cleanup():
    """Clean up test files after each test."""
    yield
    if os.path.exists(TAG_FILE):
        os.remove(TAG_FILE)
    if os.path.exists("test_file.txt"):
        os.remove("test_file.txt")

def test_tag_file(cleanup):
    """Test tagging a file."""
    # Create a test file
    with open("test_file.txt", "w") as f:
        f.write("test content")
    
    # Tag the file
    result = tag_file("test_file.txt", "important")
    assert "Tagged" in result
    
    # Verify tag was saved
    with open(TAG_FILE, "r") as f:
        tags = json.load(f)
    assert "important" in tags
    assert any("test_file.txt" in path for path in tags["important"])

def test_get_files_by_tag(cleanup):
    """Test retrieving files by tag."""
    # Create and tag a test file
    with open("test_file.txt", "w") as f:
        f.write("test content")
    tag_file("test_file.txt", "important")
    
    # Get files with tag
    files = get_files_by_tag("important")
    assert len(files) == 1
    assert any("test_file.txt" in path for path in files)

def test_get_nonexistent_tag(cleanup):
    """Test retrieving files with a nonexistent tag."""
    files = get_files_by_tag("nonexistent")
    assert files == []

def test_tag_nonexistent_file(cleanup):
    """Test tagging a nonexistent file."""
    result = tag_file("nonexistent.txt", "important")
    assert "Failed" in result

def test_multiple_tags(cleanup):
    """Test tagging a file with multiple tags."""
    # Create a test file
    with open("test_file.txt", "w") as f:
        f.write("test content")
    
    # Tag with multiple tags
    tag_file("test_file.txt", "important")
    tag_file("test_file.txt", "work")
    
    # Verify both tags exist
    files1 = get_files_by_tag("important")
    files2 = get_files_by_tag("work")
    
    assert len(files1) == 1
    assert len(files2) == 1
    assert any("test_file.txt" in path for path in files1)
    assert any("test_file.txt" in path for path in files2) 