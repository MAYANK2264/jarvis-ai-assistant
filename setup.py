from setuptools import setup, find_packages

setup(
    name="jarvis",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "SpeechRecognition==3.10.0",
        "pyttsx3==2.90",
        "pyaudio==0.2.13",
        "vosk==0.3.45",
        "psutil==5.9.5",
        "requests==2.31.0",
        "PySide6==6.5.3",
        "qt-material==2.14",
        "python-dotenv==1.0.0",
        "plyer==2.1.0",
        "pywin32==306",
        "winshell==0.6",
        "pvporcupine==2.2.1",
        "pygame==2.5.2",
    ],
)
