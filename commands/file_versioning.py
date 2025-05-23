"""File versioning module for managing file versions."""

import os
import shutil
from datetime import datetime
import time

VERSION_FOLDER = "file_versions"


def save_version(file_path: str) -> str:
    """Save a version of a file.
    
    Args:
        file_path: Path to the file to version
        
    Returns:
        str: Status message indicating success or failure
    """
    if not os.path.isfile(file_path):
        return "File does not exist."

    # Create version folder if not exists
    if not os.path.exists(VERSION_FOLDER):
        os.makedirs(VERSION_FOLDER)

    file_name = os.path.basename(file_path)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    version_name = f"{file_name}_{timestamp}"
    version_path = os.path.join(VERSION_FOLDER, version_name)

    try:
        # Ensure we don't overwrite existing versions
        while os.path.exists(version_path):
            time.sleep(1)  # Wait a second to get a unique timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            version_name = f"{file_name}_{timestamp}"
            version_path = os.path.join(VERSION_FOLDER, version_name)

        shutil.copy2(file_path, version_path)
        return f"Version saved: {version_name}"
    except OSError as e:
        return f"Failed to save version: {str(e)}"


def list_versions(file_name: str) -> list:
    """List all versions of a file.
    
    Args:
        file_name: Name of the file to list versions for
        
    Returns:
        list: List of version names
    """
    if not os.path.exists(VERSION_FOLDER):
        return []

    return sorted([f for f in os.listdir(VERSION_FOLDER) if f.startswith(file_name + "_")])


def restore_version(file_name: str, timestamp: str) -> str:
    """Restore a specific version of a file.
    
    Args:
        file_name: Name of the file to restore
        timestamp: Timestamp of the version to restore
        
    Returns:
        str: Status message indicating success or failure
    """
    version_name = f"{file_name}_{timestamp}"
    version_path = os.path.join(VERSION_FOLDER, version_name)
    
    if not os.path.exists(version_path):
        return "Version not found."
        
    try:
        shutil.copy2(version_path, file_name)
        return "Version restored successfully."
    except OSError as e:
        return f"Failed to restore version: {str(e)}"
