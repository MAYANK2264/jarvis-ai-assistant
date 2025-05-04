import sys
import os
import json
import requests
from datetime import datetime
from datetime import timedelta
import time
import threading

# Extend system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# === Import Modules ===
from speech.speech_recognition import recognize_speech
from speech.text_to_speech import speak

# Command Modules
from commands.open_apps import open_application
from commands.system_info import get_system_info
from commands.web_search import search_google
from commands.system_control import (
    shutdown, restart, set_volume, set_brightness, battery_status,
    lock_system, toggle_wifi, toggle_airplane_mode
)
from commands.offline_ai import chat_with_gpt
from commands.file_manager import (
    create_folder, delete_file_or_folder, rename_item, list_items,
    move_item, copy_item, restore_item, search_files, sort_files,
    tag_file, get_files_by_tag, mark_file_private, access_private_file
)
from commands.file_versioning import save_version, list_versions, restore_version
from commands.file_tagging import smart_search_files
from commands.auto_sort import auto_sort_files
from commands.reminder_handler import set_reminder



# === Google Search Configuration ===
API_KEY = "AIzaSyAzbZFUzk8TxSs_BtYKHWFBaYcx-WP0Vu0"
CX = "d42f59264d68b487d"


def search_google(query, search_type="web"):
    try:
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"

        if search_type == "image":
            url += "&searchType=image"
        elif search_type == "news":
            url += "&filter=1"

        response = requests.get(url)
        data = response.json()

        if "items" in data:
            results = data["items"]
            summarized_results = [{
                "title": item["title"],
                "link": item["link"],
                "snippet": item.get("snippet", "No snippet available.")
            } for item in results[:5]]

            safe_results = [res for res in summarized_results if "unsafe" not in res["snippet"].lower()]
            search_output = "\n".join(
                [f"Title: {res['title']}\nLink: {res['link']}\nSnippet: {res['snippet']}\n" for res in safe_results]
            )

            return search_output if search_output else "No relevant or safe results found."
        return "No results found."

    except Exception as e:
        return f"Error during search: {str(e)}"


# === Main Function ===
def main():
    speak("Hello! How can I assist you today?")

    while True:
        speak("Listening...")
        command = recognize_speech()

        if not command:
            continue

        print(f"Recognized: {command}")
        speak(f"You said: {command}")

        command = command.lower()

        # === Exit Keywords ===
        if any(word in command for word in ["exit", "quit", "stop", "goodbye"]):
            speak("Goodbye! Have a nice day.")
            break

        # === App and Web Commands ===
        elif "open" in command:
            response = open_application(command)
            print(response)
            speak(response)

        elif "search" in command:
            query = command.replace("search", "").strip()
            search_type = "web"
            if "image" in command:
                search_type = "image"
            elif "news" in command:
                search_type = "news"
            response = search_google(query, search_type)
            print(response)
            speak(response)

        elif "system info" in command:
            response = get_system_info()
            print(response)
            speak(response)

        # === File Management ===
        elif "create folder" in command:
            folder_name = command.replace("create folder", "").strip()
            response = create_folder(folder_name)
            print(response)
            speak(response)

        elif "delete" in command:
            path = command.replace("delete", "").strip()
            response = delete_file_or_folder(path)
            print(response)
            speak(response)

        elif "rename" in command:
            speak("Please say the current name.")
            old = recognize_speech()
            if old:
                speak("Now say the new name.")
                new = recognize_speech()
                if new:
                    response = rename_item(old.strip(), new.strip())
                    print(response)
                    speak(response)
                else:
                    speak("Failed to hear the new name.")
            else:
                speak("Failed to hear the old name.")

        elif "list files" in command or "show files" in command:
            folder = command.replace("list files", "").replace("show files", "").strip() or "."
            response = list_items(folder)
            print(response)
            speak(response)

        elif "move" in command:
            speak("Please say the source file or folder name.")
            source = recognize_speech()
            if source:
                speak("Now say the destination folder.")
                destination = recognize_speech()
                if destination:
                    response = move_item(source.strip(), destination.strip())
                    print(response)
                    speak(response)
                else:
                    speak("Failed to hear the destination folder.")
            else:
                speak("Failed to hear the source.")

        elif "copy" in command:
            speak("Please say the source file or folder name.")
            source = recognize_speech()
            if source:
                speak("Now say the destination folder.")
                destination = recognize_speech()
                if destination:
                    response = copy_item(source.strip(), destination.strip())
                    print(response)
                    speak(response)
                else:
                    speak("Failed to hear the destination folder.")
            else:
                speak("Failed to hear the source.")

        elif "restore" in command:
            item_name = command.replace("restore", "").strip()
            response = restore_item(item_name)
            print(response)
            speak(response)

        elif "search files" in command:
            name = file_type = after_date = None
            parts = command.split()
            if "name" in parts:
                name = command.split("name")[-1].strip()
            if "type" in parts:
                file_type = command.split("type")[-1].strip()
            if "after" in parts:
                date_str = command.split("after")[-1].strip()
                after_date = datetime.strptime(date_str, "%Y-%m-%d")
            files_found = search_files(".", name, file_type, after_date)
            if files_found:
                speak(f"I found {len(files_found)} files.")
                for file in files_found:
                    print(file)
                    speak(file)
            else:
                speak("No files found matching your criteria.")

        elif "sort files" in command:
            sort_by = "name"
            reverse = "desc" in command or "reverse" in command
            if "date" in command:
                sort_by = "date"
            elif "size" in command:
                sort_by = "size"
            sorted_files = sort_files(files_found, sort_by=sort_by, reverse=reverse)
            if sorted_files:
                speak(f"Here are the sorted files by {sort_by}.")
                for file in sorted_files:
                    print(file)
                    speak(file)
            else:
                speak("No files to sort.")

        elif "tag file" in command:
            speak("Please say the file name to tag.")
            file_name = recognize_speech()
            if file_name:
                speak("Now say the tag.")
                tag = recognize_speech()
                if tag:
                    response = tag_file(file_name.strip(), tag.strip().lower())
                    print(response)
                    speak(response)
                else:
                    speak("Failed to get the tag name.")
            else:
                speak("Failed to get the file name.")

        elif "show files tagged" in command:
            tag = command.replace("show files tagged", "").strip()
            if tag:
                files = get_files_by_tag(tag)
                if files:
                    speak(f"I found {len(files)} files tagged with {tag}")
                    for f in files:
                        print(f)
                        speak(f)
                else:
                    speak(f"No files found with the tag {tag}")
            else:
                speak("Please specify the tag.")

        elif "mark private" in command:
            speak("Please say the file name you want to protect.")
            filename = recognize_speech()
            speak("Please say the PIN code.")
            pin = recognize_speech()
            if filename and pin:
                response = mark_file_private(filename.strip(), pin.strip())
                print(response)
                speak(response)
            else:
                speak("Failed to get filename or PIN.")

        elif "access private" in command:
            speak("Please say the file name you want to access.")
            filename = recognize_speech()
            speak("Please say the PIN code.")
            pin = recognize_speech()
            if filename and pin:
                response = access_private_file(filename.strip(), pin.strip())
                print(response)
                speak(response)
            else:
                speak("Failed to get filename or PIN.")

        # === File Versioning ===
        elif "save version" in command:
            speak("Please say the file name to version.")
            file = recognize_speech()
            if file:
                response = save_version(file.strip())
                speak(response)

        elif "list versions" in command:
            speak("Please say the file name.")
            file = recognize_speech()
            if file:
                versions = list_versions(file.strip())
                if versions:
                    speak("Here are the saved versions:")
                    for v in versions:
                        print(v)
                        speak(v)
                else:
                    speak("No versions found.")

        elif "restore version" in command:
            speak("Please say the file name.")
            file = recognize_speech()
            if file:
                speak("Now say the version timestamp (e.g., 20240505123000).")
                ts = recognize_speech()
                if ts:
                    response = restore_version(file.strip(), ts.strip())
                    speak(response)

        # === Smart Search & Auto Sort ===
        elif "search file" in command:
            speak("What do you want to search?")
            query = recognize_speech()
            if query:
                results = smart_search_files(query.strip())
                if results:
                    speak(f"Found {len(results)} matching file(s):")
                    for f, meta in results:
                        print(f"File: {f} — Metadata: {meta}")
                        speak(f"{f} with info {meta}")
                else:
                    speak("No matching files found.")

        elif "organize files" in command:
            speak("Which folder should I organize?")
            folder = recognize_speech()
            if folder:
                result = auto_sort_files(folder.strip() or ".")
                print(result)
                speak(result)
            else:
                speak("I couldn't understand the folder name.")

        # === System Control Commands ===
        elif "lock system" in command or "lock computer" in command:
            response = lock_system()
            speak(response)

        elif "turn on wifi" in command:
            speak(toggle_wifi(True))

        elif "turn off wifi" in command:
            speak(toggle_wifi(False))

        elif "airplane mode on" in command:
            speak(toggle_airplane_mode(True))

        elif "airplane mode off" in command:
            speak(toggle_airplane_mode(False))

        # === Volume and Brightness Control ===
        elif "set volume" in command:
            try:
                level = int(command.split()[-1].replace("%", ""))
                response = set_volume(level)
                print(response)
                speak(response)
            except ValueError:
                speak("Sorry, I couldn't understand the volume level.")

        elif "set brightness" in command:
            try:
                level = int(command.split()[-1].replace("%", ""))
                response = set_brightness(level)
                print(response)
                speak(response)
            except ValueError:
                speak("Sorry, I couldn't understand the brightness level.")

        # reminders    
        elif "remind me to" in command.lower():
            try:
                import re

                # Extract time and task
                pattern = r"remind me to (.+?) in (\d+) (minute|minutes|second|seconds)"
                match = re.search(pattern, command.lower())

                if match:
                    task = match.group(1)
                    time_value = int(match.group(2))
                    unit = match.group(3)

                    delay_seconds = time_value * 60 if "minute" in unit else time_value

                    response = set_reminder(task, delay_seconds)
                    print(response)
                    speak(response)
                else:
                    speak("Sorry, I couldn't understand the reminder format.")
            except Exception as e:
                speak(f"Something went wrong while setting the reminder: {str(e)}")

          # === Reminder Functionality ===
        elif "remind me to" in command.lower():
            try:
                import re

                # Extract time and task from the user's command
                pattern = r"remind me to (.+?) in (\d+) (minute|minutes|second|seconds)"
                match = re.search(pattern, command.lower())

                if match:
                    task = match.group(1)  # Task to remind about
                    time_value = int(match.group(2))  # Time in minutes or seconds
                    unit = match.group(3)  # Unit of time (minute, second)

                    # Convert time to seconds
                    delay_seconds = time_value * 60 if "minute" in unit else time_value

                    response = set_reminder(task, delay_seconds)
                    print(response)
                    speak(response)
                else:
                    speak("Sorry, I couldn't understand the reminder format.")
            except Exception as e:
                speak(f"Something went wrong while setting the reminder: {str(e)}")

        # === Offline AI Chatbot ===
        elif "chat" in command or "talk to" in command:
            ai_response = chat_with_gpt(command)
            print(ai_response)
            speak(ai_response)

        # === Fallback Chat ===
        else:
            ai_response = chat_with_gpt(command)
            print(ai_response)
            speak(ai_response)

if __name__ == "__main__":
    main()