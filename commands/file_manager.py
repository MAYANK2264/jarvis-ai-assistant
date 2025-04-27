import os
import shutil

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
