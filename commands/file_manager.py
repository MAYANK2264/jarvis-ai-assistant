import os
import shutil
from datetime import datetime
import json

# Folder where deleted files/folders will be stored
RECYCLE_BIN = ".recycle_bin"

# Make sure recycle bin exists
if not os.path.exists(RECYCLE_BIN):
    os.makedirs(RECYCLE_BIN)

def create_folder(folder_name):
    try:
        os.makedirs(folder_name)
        return f"Folder '{folder_name}' created successfully."
    except FileExistsError:
        return f"Folder '{folder_name}' already exists."
    except Exception as e:
        return f"Failed to create folder: {e}"

def delete_file_or_folder(path):
    try:
        if not os.path.exists(path):
            return "Path does not exist."

        item_name = os.path.basename(path)
        destination = os.path.join(RECYCLE_BIN, item_name)

        # Move the file/folder to recycle bin
        shutil.move(path, destination)
        return f"'{item_name}' moved to recycle bin."
    except Exception as e:
        return f"Failed to delete: {e}"

def rename_item(old_name, new_name):
    try:
        os.rename(old_name, new_name)
        return f"Renamed '{old_name}' to '{new_name}' successfully."
    except Exception as e:
        return f"Failed to rename: {e}"

def list_items(folder="."):
    try:
        items = os.listdir(folder)
        if not items:
            return "The folder is empty."
        return "Items:\n" + "\n".join(items)
    except Exception as e:
        return f"Failed to list items: {e}"

def move_item(source, destination):
    try:
        shutil.move(source, destination)
        return f"Moved '{source}' to '{destination}' successfully."
    except Exception as e:
        return f"Failed to move item: {e}"

def copy_item(source, destination):
    try:
        if os.path.isdir(source):
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        return f"Copied '{source}' to '{destination}' successfully."
    except Exception as e:
        return f"Failed to copy item: {e}"

def restore_item(item_name):
    try:
        recycle_path = os.path.join(RECYCLE_BIN, item_name)
        if not os.path.exists(recycle_path):
            return f"No such item in recycle bin."

        # Restore to current working directory
        shutil.move(recycle_path, item_name)
        return f"'{item_name}' restored successfully."
    except Exception as e:
        return f"Failed to restore item: {e}"

def search_files(directory=".", name=None, file_type=None, after_date=None):
    # List to store matching files
    matching_files = []

    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Check name
            if name and name.lower() not in file.lower():
                continue

            # Check file type (extension)
            if file_type and not file.endswith(file_type):
                continue

            # Check modification date
            if after_date:
                file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_mod_time < after_date:
                    continue

            # Add the matching file to the list
            matching_files.append(file_path)

    return matching_files

def sort_files(files, sort_by="name", reverse=False):
    # Sort by name, date, or size
    if sort_by == "name":
        return sorted(files, key=lambda x: os.path.basename(x).lower(), reverse=reverse)
    elif sort_by == "date":
        return sorted(files, key=lambda x: os.path.getmtime(x), reverse=reverse)
    elif sort_by == "size":
        return sorted(files, key=lambda x: os.path.getsize(x), reverse=reverse)
    else:
        return files
    
# -- tag files --    
TAG_FILE = "tags.json"

def load_tags():
    if os.path.exists(TAG_FILE):
        with open(TAG_FILE, "r") as file:
            return json.load(file)
    return {}

def save_tags(tags):
    with open(TAG_FILE, "w") as file:
        json.dump(tags, file, indent=4)

def tag_file(file_path, tag):
    file_path = os.path.abspath(file_path)
    tags = load_tags()
    if tag in tags:
        if file_path not in tags[tag]:
            tags[tag].append(file_path)
    else:
        tags[tag] = [file_path]
    save_tags(tags)
    return f"Tagged '{file_path}' as '{tag}'."

def get_files_by_tag(tag):
    tags = load_tags()
    return tags.get(tag, [])    

#private files
private_files = {}  # { "filename": "PIN" }

def mark_file_private(filename, pin):
    private_files[filename] = pin
    return f"{filename} is now marked as private."

def access_private_file(filename, pin_attempt):
    if filename in private_files:
        if private_files[filename] == pin_attempt:
            return f"Access granted to {filename}."
        else:
            return "Incorrect PIN. Access denied."
    return "File is not marked as private."
