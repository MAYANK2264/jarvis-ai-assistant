from speech.speech_recognition import recognize_speech
from speech.text_to_speech import speak
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
    move_item, copy_item, restore_item, search_files, sort_files
)
from datetime import datetime
import sys
import os
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Google API Key and Custom Search Engine ID (CX)
API_KEY = "AIzaSyAzbZFUzk8TxSs_BtYKHWFBaYcx-WP0Vu0"
CX = "d42f59264d68b487d"

def search_google(query, search_type="web"):
    try:
        # Construct the Google Search API URL
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"

        # Add filters based on search type (optional)
        if search_type == "image":
            url += "&searchType=image"
        elif search_type == "news":
            url += "&filter=1"

        # Make the API request
        response = requests.get(url)
        data = response.json()

        if "items" in data:
            results = data["items"]
            summarized_results = []
            for item in results[:5]:  # Get top 5 results
                summary = {
                    "title": item["title"],
                    "link": item["link"],
                    "snippet": item.get("snippet", "No snippet available.")
                }
                summarized_results.append(summary)

            safe_results = [res for res in summarized_results if "unsafe" not in res["snippet"].lower()]

            # Format results for output
            search_output = "\n".join([f"Title: {res['title']}\nLink: {res['link']}\nSnippet: {res['snippet']}\n" for res in safe_results])

            if not search_output:
                search_output = "No relevant or safe results found."
            return search_output
        else:
            return "No results found."

    except Exception as e:
        return f"Error during search: {str(e)}"


def main():
    speak("Hello! How can I assist you today?")

    while True:
        speak("Listening...")
        command = recognize_speech()

        if command:
            print(f"Recognized: {command}")
            speak(f"You said: {command}")
        else:
            continue

        exit_keywords = ["exit", "quit", "stop", "goodbye"]
        if any(word in command.lower() for word in exit_keywords):
            speak("Goodbye! Have a nice day.")
            break

        # --- App and Web Commands ---

        elif "open" in command.lower():
            response = open_application(command)
            print(response)
            speak(response)

        elif "search" in command.lower():
            query = command.replace("search", "").strip()
            search_type = "web"  # Default search type

            # Determine if it's an image or news search
            if "image" in command.lower():
                search_type = "image"
            elif "news" in command.lower():
                search_type = "news"

            response = search_google(query, search_type)
            print(response)
            speak(response)

        elif "system info" in command.lower():
            response = get_system_info()
            print(response)
            speak(response)

        # --- File Management Commands ---
        
        elif "create folder" in command.lower():
            folder_name = command.replace("create folder", "").strip()
            response = create_folder(folder_name)
            print(response)
            speak(response)

        elif "delete" in command.lower():
            path = command.replace("delete", "").strip()
            response = delete_file_or_folder(path)
            print(response)
            speak(response)

        elif "rename" in command.lower():
            speak("Please say the current name.")
            old = recognize_speech()
            if old:
                speak(f"You said: {old}. Now say the new name.")
                new = recognize_speech()
                if new:
                    response = rename_item(old.strip(), new.strip())
                    print(response)
                    speak(response)
                else:
                    speak("Failed to hear the new name.")
            else:
                speak("Failed to hear the old name.")

        elif "list files" in command.lower() or "show files" in command.lower():
            folder = command.replace("list files", "").replace("show files", "").strip() or "."
            response = list_items(folder)
            print(response)
            speak(response)

        elif "move" in command.lower():
            speak("Please say the source file or folder name.")
            source = recognize_speech()
            if source:
                speak(f"You said: {source}. Now say the destination folder.")
                destination = recognize_speech()
                if destination:
                    response = move_item(source.strip(), destination.strip())
                    print(response)
                    speak(response)
                else:
                    speak("Failed to hear the destination folder.")
            else:
                speak("Failed to hear the source.")

        elif "copy" in command.lower():
            speak("Please say the source file or folder name.")
            source = recognize_speech()
            if source:
                speak(f"You said: {source}. Now say the destination folder.")
                destination = recognize_speech()
                if destination:
                    response = copy_item(source.strip(), destination.strip())
                    print(response)
                    speak(response)
                else:
                    speak("Failed to hear the destination folder.")
            else:
                speak("Failed to hear the source.")

        elif "restore" in command.lower():
            item_name = command.replace("restore", "").strip()
            response = restore_item(item_name)
            print(response)
            speak(response)

        elif "search files" in command.lower():
            # Extract search parameters from the command
            command_parts = command.lower().split()
            name = None
            file_type = None
            after_date = None

            # Extract search criteria from the command (e.g., name, type, date)
            if "name" in command_parts:
                name = command.split("name")[-1].strip()
            if "type" in command_parts:
                file_type = command.split("type")[-1].strip()
            if "after" in command_parts:
                date_str = command.split("after")[-1].strip()
                after_date = datetime.strptime(date_str, "%Y-%m-%d")

            # Perform file search
            files_found = search_files(directory=".", name=name, file_type=file_type, after_date=after_date)

            # Display the search results
            if files_found:
                speak(f"I found {len(files_found)} files.")
                for file in files_found:
                    print(file)
                    speak(file)
            else:
                speak("No files found matching your criteria.")

        elif "sort files" in command.lower():
            # Extract sorting criteria
            command_parts = command.lower().split()
            sort_by = "name"
            reverse = False

            if "date" in command_parts:
                sort_by = "date"
            elif "size" in command_parts:
                sort_by = "size"

            if "desc" in command_parts or "reverse" in command_parts:
                reverse = True

            # Perform sorting
            sorted_files = sort_files(files_found, sort_by=sort_by, reverse=reverse)

            # Display sorted files
            if sorted_files:
                speak(f"Here are the sorted files by {sort_by}.")
                for file in sorted_files:
                    print(file)
                    speak(file)
            else:
                speak("No files to sort.")    

        # --- System Control Commands ---
        elif "lock system" in command or "lock computer" in command:
            response = lock_system()
            speak(response)

        elif "turn on wifi" in command:
            response = toggle_wifi(True)
            speak(response)

        elif "turn off wifi" in command:
            response = toggle_wifi(False)
            speak(response)

        elif "airplane mode on" in command:
            response = toggle_airplane_mode(True)
            speak(response)

        elif "airplane mode off" in command:
            response = toggle_airplane_mode(False)
            speak(response)

        # --- Volume and Brightness Commands ---
        elif "set volume" in command.lower():
            try:
                level = int(command.split()[-1].replace("%", ""))
                response = set_volume(level)
                print(response)
                speak(response)
            except ValueError:
                speak("Sorry, I couldn't understand the volume level.")

        elif "set brightness" in command.lower():
            try:
                level = int(command.split()[-1].replace("%", ""))
                response = set_brightness(level)
                print(response)
                speak(response)
            except ValueError:
                speak("Sorry, I couldn't understand the brightness level.")

        # --- Offline AI Chatbot ---
        elif "chat" in command.lower() or "talk to" in command.lower():
            ai_response = chat_with_gpt(command)
            print(ai_response)
            speak(ai_response)

        else:
            ai_response = chat_with_gpt(command)
            print(ai_response)
            speak(ai_response)

if __name__ == "__main__":
    main()
