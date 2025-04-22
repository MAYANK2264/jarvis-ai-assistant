import os
import shutil

def create_folder(folder_name):
    try:
        os.makedirs(folder_name, exist_ok=True)
        return f"Folder '{folder_name}' created successfully."
    except Exception as e:
        return f"Error creating folder: {e}"

def delete_file_or_folder(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
            return f"File '{path}' deleted."
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"Folder '{path}' deleted."
        else:
            return "Path does not exist."
    except Exception as e:
        return f"Error deleting: {e}"

def rename_item(old_name, new_name):
    try:
        os.rename(old_name, new_name)
        return f"Renamed from '{old_name}' to '{new_name}'."
    except Exception as e:
        return f"Error renaming: {e}"

def list_items(folder_path):
    try:
        items = os.listdir(folder_path)
        return f"Items in '{folder_path}': " + ", ".join(items) if items else "Folder is empty."
    except Exception as e:
        return f"Error listing items: {e}"
