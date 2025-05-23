import os
import shutil

# Define categories and extensions
FILE_CATEGORIES = {
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".pptx", ".xlsx"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov"],
    "Music": [".mp3", ".wav", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar"],
    "Code": [".py", ".js", ".java", ".cpp", ".html", ".css", ".ts"],
}


def auto_sort_files(source_folder="."):
    if not os.path.exists(source_folder):
        return "The specified folder does not exist."

    files_moved = 0

    for file_name in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file_name)
        if not os.path.isfile(file_path):
            continue

        _, ext = os.path.splitext(file_name.lower())
        moved = False

        for category, extensions in FILE_CATEGORIES.items():
            if ext in extensions:
                category_folder = os.path.join(source_folder, category)
                os.makedirs(category_folder, exist_ok=True)
                shutil.move(file_path, os.path.join(category_folder, file_name))
                files_moved += 1
                moved = True
                break

        if not moved and ext:  # Unknown but valid extension
            other_folder = os.path.join(source_folder, "Others")
            os.makedirs(other_folder, exist_ok=True)
            shutil.move(file_path, os.path.join(other_folder, file_name))
            files_moved += 1

    return f"Auto-sorting complete. Moved {files_moved} file(s)."
