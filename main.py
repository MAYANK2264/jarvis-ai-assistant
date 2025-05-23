import sys
import os
import json
import requests
from datetime import datetime
from datetime import timedelta
import time
import threading
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication
import random
import logging

# Load environment variables
load_dotenv()

# Extend system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# === Import Modules ===
from speech.speech_recognition import recognize_speech
from speech.text_to_speech import speak
from speech.wake_word import WakeWordDetector
from ui.main_window import JarvisUI
from utils.sound_player import get_sound_player
from utils.create_sound import create_wake_sound
from utils.database import get_db_manager
from utils.memory_manager import get_memory_manager
from utils.retry import retry, transactional, Transaction
from utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Command Modules
from commands.open_apps import open_application
from commands.system_info import get_system_info
from commands.web_search import search_google
from commands.system_control import (
    shutdown,
    restart,
    set_volume,
    set_brightness,
    battery_status,
    lock_system,
    toggle_wifi,
    toggle_airplane_mode,
)
from commands.offline_ai import chat_with_gpt
from commands.file_manager import (
    create_folder,
    delete_file_or_folder,
    rename_item,
    list_items,
    move_item,
    copy_item,
    restore_item,
    search_files,
    sort_files,
    tag_file,
    get_files_by_tag,
    mark_file_private,
    access_private_file,
)
from commands.file_versioning import save_version, list_versions, restore_version
from commands.file_tagging import smart_search_files
from commands.auto_sort import auto_sort_files
from commands.reminder_handler import set_reminder


# === Google Search Configuration ===
API_KEY = os.getenv("GOOGLE_API_KEY")
CX = os.getenv("GOOGLE_CX")


def search_google(query, search_type="web"):
    if not API_KEY or not CX:
        return "Error: Google Search API configuration is missing. Please check your environment variables."

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
            summarized_results = [
                {
                    "title": item["title"],
                    "link": item["link"],
                    "snippet": item.get("snippet", "No snippet available."),
                }
                for item in results[:5]
            ]

            safe_results = [
                res
                for res in summarized_results
                if "unsafe" not in res["snippet"].lower()
            ]
            search_output = "\n".join(
                [
                    f"Title: {res['title']}\nLink: {res['link']}\nSnippet: {res['snippet']}\n"
                    for res in safe_results
                ]
            )

            return (
                search_output if search_output else "No relevant or safe results found."
            )
        return "No results found."

    except Exception as e:
        return f"Error during search: {str(e)}"


class JarvisCore:
    def __init__(self):
        self.wake_word_detector = None
        self.ui = None
        self.is_listening = False
        self.sound_player = get_sound_player()
        self.db = get_db_manager()
        self.memory_manager = get_memory_manager()

        # Setup sounds directory
        self.sounds_dir = os.path.join(os.path.dirname(__file__), "sounds")
        if not os.path.exists(self.sounds_dir):
            os.makedirs(self.sounds_dir)

        # Create wake sound if it doesn't exist
        create_wake_sound(self.sounds_dir)
        self.wake_sound = os.path.join(self.sounds_dir, "wake.wav")

        # Register cache cleanup
        self.memory_manager.register_cleanup_callback(self._cleanup_cache)

    def _cleanup_cache(self):
        """Clean up cache when memory usage is high"""
        logger.info("Performing cache cleanup")
        # Add your cache cleanup logic here

    @retry(max_attempts=3)
    def initialize(self):
        """Initialize Jarvis components"""
        try:
            # Initialize wake word detector
            access_key = os.getenv("PICOVOICE_ACCESS_KEY")
            if not access_key:
                logger.error("Picovoice access key not found in environment variables")
                return False

            self.wake_word_detector = WakeWordDetector(
                access_key=access_key,
                wake_word="jarvis",
                on_wake_word=self.on_wake_word,
            )

            # Start memory monitoring
            self.memory_manager.start_monitoring()

            logger.info("Jarvis core initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Jarvis: {str(e)}")
            return False

    def start(self):
        """Start Jarvis"""
        if self.wake_word_detector:
            self.wake_word_detector.start()
            logger.info("Jarvis started")

    def stop(self):
        """Stop Jarvis"""
        if self.wake_word_detector:
            self.wake_word_detector.stop()
        self.memory_manager.stop_monitoring()
        logger.info("Jarvis stopped")

    def get_greeting(self) -> str:
        """Get a random greeting"""
        greetings = [
            "How can I assist you?",
            "What can I do for you?",
            "How may I help you today?",
            "Ready to assist. What do you need?",
            "At your service. What's on your mind?",
            "I'm here to help. What do you need?",
        ]
        return random.choice(greetings)

    @transactional
    def process_command(self, command: str, transaction: Transaction = None) -> str:
        """Process a voice command with transaction support"""
        try:
            start_time = time.time()
            command = command.lower()

            # === Exit Keywords ===
            if any(word in command for word in ["exit", "quit", "stop", "goodbye"]):
                return "Goodbye! Have a nice day."

            # === App and Web Commands ===
            elif "open" in command:
                response = open_application(command)
                return response

            elif "search" in command:
                query = command.replace("search", "").strip()
                search_type = "web"
                if "image" in command:
                    search_type = "image"
                elif "news" in command:
                    search_type = "news"
                response = search_google(query, search_type)
                return response

            elif "system info" in command:
                response = get_system_info()
                return response

            # === File Management ===
            elif "create folder" in command:
                folder_name = command.replace("create folder", "").strip()
                response = create_folder(folder_name)
                return response

            elif "delete" in command:
                path = command.replace("delete", "").strip()
                response = delete_file_or_folder(path)
                return response

            elif "rename" in command:
                speak("Please say the current name.")
                old = recognize_speech()
                if old:
                    speak("Now say the new name.")
                    new = recognize_speech()
                    if new:
                        response = rename_item(old.strip(), new.strip())
                        return response
                    else:
                        return "Failed to hear the new name."
                else:
                    return "Failed to hear the old name."

            elif "list files" in command or "show files" in command:
                folder = (
                    command.replace("list files", "").replace("show files", "").strip()
                    or "."
                )
                response = list_items(folder)
                return response

            elif "move" in command:
                speak("Please say the source file or folder name.")
                source = recognize_speech()
                if source:
                    speak("Now say the destination folder.")
                    destination = recognize_speech()
                    if destination:
                        response = move_item(source.strip(), destination.strip())
                        return response
                    else:
                        return "Failed to hear the destination folder."
                else:
                    return "Failed to hear the source."

            elif "copy" in command:
                speak("Please say the source file or folder name.")
                source = recognize_speech()
                if source:
                    speak("Now say the destination folder.")
                    destination = recognize_speech()
                    if destination:
                        response = copy_item(source.strip(), destination.strip())
                        return response
                    else:
                        return "Failed to hear the destination folder."
                else:
                    return "Failed to hear the source."

            elif "restore" in command:
                item_name = command.replace("restore", "").strip()
                response = restore_item(item_name)
                return response

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
                    return f"I found {len(files_found)} files."
                else:
                    return "No files found matching your criteria."

            elif "sort files" in command:
                sort_by = "name"
                reverse = "desc" in command or "reverse" in command
                if "date" in command:
                    sort_by = "date"
                elif "size" in command:
                    sort_by = "size"
                sorted_files = sort_files(files_found, sort_by=sort_by, reverse=reverse)
                if sorted_files:
                    return f"Here are the sorted files by {sort_by}."
                else:
                    return "No files to sort."

            elif "tag file" in command:
                speak("Please say the file name to tag.")
                file_name = recognize_speech()
                if file_name:
                    speak("Now say the tag.")
                    tag = recognize_speech()
                    if tag:
                        response = tag_file(file_name.strip(), tag.strip().lower())
                        return response
                    else:
                        return "Failed to get the tag name."
                else:
                    return "Failed to get the file name."

            elif "show files tagged" in command:
                tag = command.replace("show files tagged", "").strip()
                if tag:
                    files = get_files_by_tag(tag)
                    if files:
                        return f"I found {len(files)} files tagged with {tag}"
                    else:
                        return f"No files found with the tag {tag}"
                else:
                    return "Please specify the tag."

            elif "mark private" in command:
                speak("Please say the file name you want to protect.")
                filename = recognize_speech()
                speak("Please say the PIN code.")
                pin = recognize_speech()
                if filename and pin:
                    response = mark_file_private(filename.strip(), pin.strip())
                    return response
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
                    pattern = (
                        r"remind me to (.+?) in (\d+) (minute|minutes|second|seconds)"
                    )
                    match = re.search(pattern, command.lower())

                    if match:
                        task = match.group(1)
                        time_value = int(match.group(2))
                        unit = match.group(3)

                        delay_seconds = (
                            time_value * 60 if "minute" in unit else time_value
                        )

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

            # Log performance metrics
            duration_ms = int((time.time() - start_time) * 1000)
            memory_usage = int(self.memory_manager.get_memory_usage())
            self.db.log_performance(
                operation="process_command",
                duration_ms=duration_ms,
                memory_usage=memory_usage,
            )

            return "Command processed successfully"

        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return f"Error: {str(e)}"

    def on_wake_word(self):
        """Handle wake word detection"""
        if not self.is_listening:
            self.is_listening = True
            logger.info("Wake word detected")

            # Play wake sound
            if os.path.exists(self.wake_sound):
                self.sound_player.play_sound(self.wake_sound, duration=1.0)

            # Greet user
            greeting = self.get_greeting()
            self.log(f"Jarvis: {greeting}")
            speak(greeting)

            # Start listening for command
            command = recognize_speech()
            if command:
                self.log(f"You: {command}")
                response = self.process_command(command)
                self.log(f"Jarvis: {response}")
                speak(response)

            self.is_listening = False

    def log(self, message: str):
        """Log a message to UI and logging system"""
        if self.ui:
            self.ui.log_message(message)
        logger.info(message)


def main():
    try:
        # Create Qt application
        app = QApplication(sys.argv)

        # Initialize Jarvis core
        jarvis = JarvisCore()
        if not jarvis.initialize():
            logger.error("Failed to initialize Jarvis")
            return

        # Create and show UI
        window = JarvisUI(jarvis)
        jarvis.ui = window
        window.show()

        # Start Jarvis
        jarvis.start()

        # Run application
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
