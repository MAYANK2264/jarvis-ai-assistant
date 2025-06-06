import sys
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QStyle
from plyer import notification
from commands.offline_ai import chat_with_gpt
import wikipedia
import pyjokes
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("jarvis.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class JarvisCore:
    def __init__(self):
        # Import speech modules
        from speech.speech_recognition import recognize_speech
        from speech.text_to_speech import speak

        self.recognize_speech = recognize_speech
        self.speak = speak

        self._load_commands()
        logger.info("Jarvis Core initialized successfully")

    def _load_commands(self):
        # Import command modules
        from commands.open_apps import open_application
        from commands.system_info import get_system_info
        from commands.web_search import search_google
        from commands.system_control import (
            shutdown, restart, set_volume, set_brightness,
            battery_status, lock_system, toggle_wifi
        )

        # Command map
        self.commands = {
            "open": open_application,
            "system info": get_system_info,
            "search": search_google,
            "shutdown": shutdown,
            "restart": restart,
            "volume": set_volume,
            "brightness": set_brightness,
            "battery": battery_status,
            "lock": lock_system,
            "wifi": toggle_wifi,
        }

    def process_command(self, command):
        try:
            command = command.lower().strip()

            if "what can you do" in command or "help" in command:
                return (
                    "I can help you with:\n"
                    "1. Search the web\n"
                    "2. System info\n"
                    "3. Open apps\n"
                    "4. Control volume, brightness, wifi\n"
                    "5. Answer questions\n"
                    "6. Lock or shutdown\n"
                    "7. Battery status\n"
                    "8. Tell jokes\n"
                )

            if "date" in command or "time" in command:
                now = datetime.now()
                if "date" in command:
                    return f"Today's date is {now.strftime('%A, %B %d, %Y')}"
                else:
                    return f"The current time is {now.strftime('%I:%M %p')}"

            if "search" in command:
                return self.commands["search"](command)

            if "system" in command and "info" in command:
                return self.commands["system info"]()

            if "open" in command:
                app_name = command.replace("open", "").strip()
                return self.commands["open"](app_name) if app_name else "Please specify an application to open."

            if "volume" in command:
                try:
                    level = int(''.join(filter(str.isdigit, command)))
                    return self.commands["volume"](level)
                except ValueError:
                    return "Please specify a volume level (0-100)."

            if "brightness" in command:
                try:
                    level = int(''.join(filter(str.isdigit, command)))
                    return self.commands["brightness"](level)
                except ValueError:
                    return "Please specify a brightness level (0-100)."

            if "battery" in command:
                return self.commands["battery"]()

            if "wifi" in command:
                return self.commands["wifi"]()

            if "lock" in command:
                return self.commands["lock"]()

            if "shutdown" in command:
                return self.commands["shutdown"]()

            if "restart" in command:
                return self.commands["restart"]()

            if "joke" in command:
                return pyjokes.get_joke()

            if "who" in command and "moon" in command:
                return "Neil Armstrong was the first person to land on the moon on July 20, 1969."

            if any(word in command for word in ["who is", "what is", "when was"]):
                try:
                    summary = wikipedia.summary(command, sentences=2)
                    return summary
                except wikipedia.exceptions.DisambiguationError as e:
                    return f"Your question is too vague. Try: {e.options[0]}"
                except wikipedia.exceptions.PageError:
                    return "Sorry, I couldn't find any information."

            if any(x in command for x in ["exit", "quit", "stop", "goodbye"]):
                return "Goodbye! Have a nice day."

            return chat_with_gpt(command)

        except Exception as e:
            logger.error(f"Error processing command: {str(e)}", exc_info=True)
            return f"I encountered an error: {str(e)}"


def create_desktop_shortcut():
    try:
        import winshell
        from win32com.client import Dispatch

        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "Jarvis AI.lnk")

        if not os.path.exists(shortcut_path):
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{os.path.abspath(__file__)}"'
            shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(__file__))
            shortcut.save()

            notification.notify(
                title="Jarvis AI",
                message="Desktop shortcut created successfully!",
                timeout=5,
            )
    except Exception as e:
        logger.error(f"Error creating shortcut: {str(e)}", exc_info=True)


def main():
    try:
        app = QApplication(sys.argv)

        from ui.main_window import JarvisUI  # Moved here to avoid circular import issues

        jarvis = JarvisCore()
        window = JarvisUI(jarvis)
        window.show()

        create_desktop_shortcut()
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        notification.notify(
            title="Jarvis AI Error",
            message="An error occurred. Please check the logs.",
            timeout=5,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
