from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QLabel,
    QSystemTrayIcon,
    QMenu,
    QApplication,
    QStyle,
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer
from PySide6.QtGui import QIcon, QPixmap, QKeyEvent
from qt_material import apply_stylesheet
import sys
import os


class JarvisUI(QMainWindow):
    def __init__(self, jarvis_core):
        super().__init__()
        self.jarvis = jarvis_core
        self.wake_word_active = False
        self.recognizer = None
        self.setup_ui()
        self.setup_tray()

    def setup_ui(self):
        self.setWindowTitle("Jarvis AI Assistant")
        self.setMinimumSize(800, 600)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Status area
        status_layout = QHBoxLayout()
        
        # Create status indicator and text
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(20, 20)
        self.status_text = QLabel("Jarvis is inactive")
        
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()
        main_layout.addLayout(status_layout)
        
        # Update status indicator after creating status_text
        self.update_status_indicator(False)

        # Console output
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet(
            """
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border-radius: 10px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 14px;
            }
        """
        )
        main_layout.addWidget(self.console)

        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your command here...")
        self.input_field.returnPressed.connect(self.process_input)
        self.input_field.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                border-radius: 5px;
                font-size: 14px;
                min-height: 30px;
            }
        """
        )
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.process_input)
        self.send_button.setStyleSheet(
            """
            QPushButton {
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """
        )
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        main_layout.addLayout(input_layout)

        # Control buttons
        button_layout = QHBoxLayout()

        self.toggle_button = QPushButton("Enable Wake Word")
        self.toggle_button.clicked.connect(self.toggle_wake_word)
        self.toggle_button.setStyleSheet(
            """
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """
        )

        self.clear_button = QPushButton("Clear Console")
        self.clear_button.clicked.connect(self.console.clear)

        button_layout.addWidget(self.toggle_button)
        button_layout.addWidget(self.clear_button)
        main_layout.addLayout(button_layout)

        # Apply material theme
        apply_stylesheet(self, theme="dark_teal.xml")

    def setup_tray(self):
        """Setup system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(
            QIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        )

        # Create tray menu
        tray_menu = QMenu()
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        hide_action = tray_menu.addAction("Hide")
        hide_action.triggered.connect(self.hide)
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def update_status_indicator(self, is_active: bool):
        """Update the status indicator color"""
        color = (
            "#4CAF50" if is_active else "#F44336"
        )  # Green if active, red if inactive
        self.status_indicator.setStyleSheet(
            f"""
            QLabel {{
                background-color: {color};
                border-radius: 10px;
            }}
        """
        )
        self.status_text.setText("Jarvis is " + ("active" if is_active else "inactive"))

    def toggle_wake_word(self):
        """Toggle wake word detection"""
        try:
            if not self.wake_word_active:
                # Initialize speech recognition if not already done
                if not self.recognizer:
                    from speech.speech_recognition import get_recognizer
                    self.recognizer = get_recognizer()
                
                # Start listening with callback
                self.recognizer.start_listening(self.handle_speech)
                self.wake_word_active = True
                self.log_message("Wake word detection activated")
            else:
                # Stop listening
                if self.recognizer:
                    self.recognizer.stop_listening()
                self.wake_word_active = False
                self.log_message("Wake word detection deactivated")
            
            # Update UI
            self.toggle_button.setText(
                "Disable Wake Word" if self.wake_word_active else "Enable Wake Word"
            )
            self.update_status_indicator(self.wake_word_active)
            
        except Exception as e:
            self.log_message(f"Error toggling wake word detection: {str(e)}")
            self.wake_word_active = False
            self.update_status_indicator(False)

    def handle_speech(self, text: str):
        """Handle recognized speech"""
        try:
            text = text.lower().strip()
            
            # Check for wake word
            if "jarvis" in text:
                from speech.text_to_speech import speak
                speak("Yes, how can I help you?")
                self.log_message("Listening for command...")
                return
                
            # Process command if wake word was detected
            if self.wake_word_active:
                self.log_message(f"You: {text}")
                response = self.jarvis.process_command(text)
                self.log_message(f"Jarvis: {response}")
                
        except Exception as e:
            self.log_message(f"Error processing speech: {str(e)}")

    def log_message(self, message: str):
        """Add a message to the console"""
        self.console.append(message)

    def process_input(self):
        """Process user input and get AI response"""
        command = self.input_field.text().strip()
        if command:
            # Log user input
            self.log_message(f"You: {command}")
            
            # Process command through Jarvis core
            response = self.jarvis.process_command(command)
            
            # Log AI response
            self.log_message(f"Jarvis: {response}")
            
            # Clear input field
            self.input_field.clear()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.process_input()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle window close event"""
        # Stop speech recognition if active
        if self.recognizer and self.wake_word_active:
            self.recognizer.stop_listening()
            
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Jarvis AI",
            "Jarvis is still running in the background.",
            QSystemTrayIcon.Information,
            2000,
        )
