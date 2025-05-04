import os
import shutil
from datetime import datetime

VERSION_FOLDER = "file_versions"

def save_version(file_path):
    if not os.path.isfile(file_path):
        return "File does not exist."

    # Create version folder if not exists
    if not os.path.exists(VERSION_FOLDER):
        os.makedirs(VERSION_FOLDER)

    file_name = os.path.basename(file_path)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    version_name = f"{file_name}_{timestamp}"
    version_path = os.path.join(VERSION_FOLDER, version_name)

    shutil.copy(file_path, version_path)
    return f"Version saved: {version_name}"


def list_versions(file_name):
    if not os.path.exists(VERSION_FOLDER):
        return []

    return [
        f for f in os.listdir(VERSION_FOLDER)
        if f.startswith(file_name + "_")
    ]


def restore_version(file_name, version_timestamp):
    version_name = f"{file_name}_{version_timestamp}"
    version_path = os.path.join(VERSION_FOLDER, version_name)
    original_path = os.path.join(".", file_name)

    if os.path.exists(version_path):
        shutil.copy(version_path, original_path)
        return f"Version {version_timestamp} restored."
    else:
        return "Version not found."
