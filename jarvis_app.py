import sys
import os
from PySide6.QtWidgets import QApplication, QStyle
from ui.main_window import JarvisUI
from dotenv import load_dotenv
import logging
from plyer import notification

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("jarvis.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class JarvisCore:
    def __init__(self):
        load_dotenv()  # Load environment variables

        # Initialize speech recognition and TTS
        from speech.speech_recognition import recognize_speech
        from speech.text_to_speech import speak

        self.recognize_speech = recognize_speech
        self.speak = speak

        # Load command modules
        self._load_commands()

        logger.info("Jarvis Core initialized successfully")

    def _load_commands(self):
        # Import all command modules
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
        )

        # Map commands to functions
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
        """Process user commands and return appropriate responses."""
        try:
            command = command.lower().strip()

            # Help command
            if "what can you do" in command or "help" in command:
                return (
                    "I can help you with:\n"
                    "1. Search the web (e.g., 'search weather today')\n"
                    "2. Get system information (e.g., 'system info')\n"
                    "3. Open applications (e.g., 'open notepad')\n"
                    "4. Control system (volume, brightness, wifi)\n"
                    "5. Answer questions (e.g., 'what is the date today')\n"
                    "6. Get battery status (e.g., 'battery status')\n"
                    "Just ask me what you need!"
                )

            # Date and time queries
            if "date" in command or "time" in command:
                from datetime import datetime
                now = datetime.now()
                if "date" in command:
                    return f"Today's date is {now.strftime('%A, %B %d, %Y')}"
                else:
                    return f"The current time is {now.strftime('%I:%M %p')}"

            # Search queries
            if "search" in command:
                return self.commands["search"](command)

            # System info query
            if "system" in command and "info" in command:
                return self.commands["system info"]()

            # Application commands
            if "open" in command:
                app_name = command.replace("open", "").strip()
                if app_name:
                    return self.commands["open"](app_name)
                return "Please specify an application to open."

            # Volume control
            if "volume" in command:
                try:
                    level = int(''.join(filter(str.isdigit, command)))
                    return self.commands["volume"](level)
                except ValueError:
                    return "Please specify a volume level (0-100)"

            # Battery status
            if "battery" in command:
                return self.commands["battery"]()

            # WiFi control
            if "wifi" in command:
                return self.commands["wifi"]()

            # Lock system
            if "lock" in command:
                return self.commands["lock"]()

            # Common questions
            if "who" in command and "moon" in command:
                return "Neil Armstrong was the first person to land on the moon on July 20, 1969, during the Apollo 11 mission."

            # Exit commands
            if any(word in command for word in ["exit", "quit", "stop", "goodbye"]):
                return "Goodbye! Have a nice day."

            # If no specific command matches
            return "I'm not sure how to help with that. Try asking 'what can you do' for a list of commands."

        except Exception as e:
            logger.error(f"Error processing command: {str(e)}", exc_info=True)
            return f"I encountered an error: {str(e)}"


def create_desktop_shortcut():
    try:
        import winshell
        from win32com.client import Dispatch

        desktop = winshell.desktop()
        path = os.path.join(desktop, "Jarvis AI.lnk")

        if not os.path.exists(path):
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{os.path.abspath(__file__)}"'
            shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(__file__))
            # Use Windows default Python icon
            shortcut.save()

            app = QApplication.instance() or QApplication([])
            icon = app.style().standardIcon(QStyle.SP_ComputerIcon)

            notification.notify(
                title="Jarvis AI",
                message="Desktop shortcut created successfully!",
                timeout=5,
            )
    except Exception as e:
        logger.error(f"Error creating shortcut: {str(e)}", exc_info=True)


def main():
    try:
        # Create the application
        app = QApplication(sys.argv)

        # Initialize Jarvis core
        jarvis = JarvisCore()

        # Create and show the UI
        window = JarvisUI(jarvis)
        window.show()

        # Create desktop shortcut
        create_desktop_shortcut()

        # Start the application
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
