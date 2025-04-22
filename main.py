from speech.speech_recognition import recognize_speech
from speech.text_to_speech import speak
from commands.open_apps import open_application
from commands.system_info import get_system_info
from commands.web_search import search_google
from commands.system_control import shutdown, restart, set_volume, set_brightness, battery_status
from commands.offline_ai import chat_with_gpt  # Using Offline AI
from commands.file_manager import create_folder, delete_file_or_folder, rename_item, list_items

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    speak("Hello! How can I assist you?")
    
    while True:
        command = recognize_speech()

        if command:
            print(f"Recognized: {command}")
            speak(f"You said: {command}")

        exit_keywords = ["exit", "quit", "stop", "goodbye"]
        if command and any(word in command.lower() for word in exit_keywords):
            speak("Goodbye! Have a nice day.")
            break

        elif "open" in command:
            response = open_application(command)
            speak(response)

        elif "search" in command:
            query = command.replace("search", "").strip()
            response = search_google(query)
            speak(response)

        elif "system info" in command:
            response = get_system_info()
            speak(response)

        elif "shutdown" in command:
            response = shutdown()
            speak(response)
            break

        elif "restart" in command:
            response = restart()
            speak(response)
            break

        elif "set volume" in command:
            level = int(command.split()[-1].replace("%", ""))  
            response = set_volume(level)
            speak(response)

        elif "set brightness" in command:
            level = int(command.split()[-1].replace("%", ""))  
            response = set_brightness(level)
            speak(response)

        elif "battery status" in command:
            response = battery_status()
            speak(response)

        elif "create folder" in command:
            folder_name = command.replace("create folder", "").strip()
            response = create_folder(folder_name)
            speak(response)

        elif "delete folder" in command:
             # Try to extract folder name after "name" or just remove known phrases
             folder_name = command.lower().replace("delete folder", "")
             folder_name = folder_name.replace("from my directory", "")
             folder_name = folder_name.replace("named", "").replace("name", "").strip()

             path = os.path.join(os.getcwd(), folder_name)
             print(f"[DEBUG] Trying to delete folder at: {path}")
             response = delete_file_or_folder(path)
             speak(response)

        elif "delete file" in command:
            file_name = command.replace("delete file", "").strip()
            path = os.path.join(os.getcwd(), file_name)
            response = delete_file_or_folder(path)
            speak(response)


        elif "rename" in command:
            speak("Please say the current name.")
            old = recognize_speech()
            speak("Please say the new name.")
            new = recognize_speech()
            response = rename_item(old.strip(), new.strip())
            speak(response)

        elif "list files" in command or "show files" in command:
            folder = command.replace("list files", "").replace("show files", "").strip() or "."
            response = list_items(folder)
            speak(response)

        # Offline AI Chatbot Integration
        else:
            ai_response = chat_with_gpt(command)
            speak(ai_response)

if __name__ == "__main__":
    main()
