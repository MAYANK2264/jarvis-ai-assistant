# 🤖 JARVIS - AI Virtual Assistant (Offline + Voice Controlled)

JARVIS is a personal AI assistant built using Python that interacts through **voice commands** and performs a wide variety of tasks—entirely **offline** with an optional **online chatbot fallback**. Inspired by Iron Man's JARVIS, this assistant can speak, listen, understand, and perform actions like file operations, system commands, opening apps, answering questions, and more.

---

## 🎯 Features

✅ Voice-controlled interaction  
✅ Offline AI chatbot (Mistral 7B via GPT4All)  
✅ Text-to-speech and speech recognition  
✅ File manager: Create, delete, rename folders/files  
✅ Open installed applications  
✅ System info (battery, volume, brightness, etc.)  
✅ Google search via browser  
✅ Shutdown, restart commands  
✅ Easy modular design — new features can be plugged in easily

---

## 🧠 Tech Stack

- Python 3.10+
- [GPT4All](https://github.com/nomic-ai/gpt4all) for offline AI
- `speech_recognition` for voice input
- `pyttsx3` for voice output
- `pyautogui`, `psutil`, `os`, and more for system commands
- Modular architecture using a `commands` folder

---

## 📂 File Structure
plaintext
Copy
Edit
JarvisAI/
│
├── main.py                      # Entry point for running the assistant
├── requirements.txt             # All dependencies listed here
├── .env                         # (Optional) Store OpenAI API key (if using online AI)
│
├── commands/                    # Command handlers - modularized functionalities
│   ├── ai_chatbot.py            # Online AI chatbot using OpenAI (for web-based AI)
│   ├── offline_ai.py           # Offline AI chatbot using GPT4All (Mistral model)
│   ├── file_manager.py         # File operations: create, delete, rename folders/files
│   ├── open_apps.py            # Commands to open installed applications based on voice
│   ├── system_control.py       # System control commands: shutdown, restart, volume, etc.
│   ├── system_info.py          # Get system info like battery status, volume, brightness, etc.
│   └── web_search.py           # Perform Google search via web browser
│
├── speech/                      # Speech-related modules for recognition and synthesis
│   ├── speech_recognition.py   # Voice input (recognize speech)
│   └── text_to_speech.py       # Text-to-speech conversion (speak responses)

## 🧰 Explanation of the Files
main.py: The entry point of the application. It runs the assistant, listens to commands, processes them, and invokes the appropriate command handler from the commands folder.

requirements.txt: Contains all the required dependencies that need to be installed for the assistant to function. This will be installed using pip install -r requirements.txt.

commands/: Contains all the modules that handle different functionalities. Each file in this folder is responsible for a set of commands like opening apps, managing files, or controlling system functions.

ai_chatbot.py: This file manages communication with the OpenAI API for online-based AI features (use this if you want to switch to an online model).

offline_ai.py: Contains code to interact with an offline AI (GPT4All) for conversational purposes.

file_manager.py: Contains methods for managing files and folders such as creating, deleting, and renaming them.

open_apps.py: This file allows the assistant to open installed applications based on user commands.

system_control.py: Provides system control capabilities like shutting down the system, restarting, adjusting volume/brightness, etc.

system_info.py: This file fetches system information like battery status, disk space, and other system-related queries.

web_search.py: Allows the assistant to search the web via Google using voice commands.

speech/: Contains the files related to speech recognition and speech synthesis.

speech_recognition.py: Handles voice input, converting spoken words into text.

text_to_speech.py: Converts text into speech, making the assistant respond verbally.


#### 🛠️ Setup Instructions

# 🔹 Step 1: Clone the repository

        git clone https://github.com/your-username/jarvis-ai-assistant.git
        cd jarvis-ai-assistant
    
# 🔹 Step 2: Create & activate virtual environment

        python -m venv my_jarvis
        my_jarvis\Scripts\activate
    
# 🔹 Step 3: Install dependencies

        pip install -r requirements.txt
    
# 🔹 Step 4: Download GPT4All Offline Model (Optional for offline AI)
Go to: https://gpt4all.io/index.html

Download the Mistral-7B-Instruct model (gguf version)

Place it in the following directory:

makefile
Copy
Edit
C:\Users\<your_username>\AppData\Local\nomic.ai\GPT4All\
Example file path:

makefile
Copy
Edit
C:\Users\kmmay\AppData\Local\nomic.ai\GPT4All\mistral-7b-instruct-v0.1.Q4_0.gguf

## 🚀 Running the Assistant
In your terminal:


        python main.py
    
Then just speak a command like:

“Open Notepad”
“Create folder test”
“Delete folder test”
“What is the battery status”
“Who is the first person to walk on the moon”
“Tell me a joke”
“Search Python tutorials”
“Shutdown the system”
“Stop” (to exit)


## 🧠 Switching Between Online and Offline AI
Offline AI is used by default using GPT4All.

To use OpenAI GPT-3.5/4 online, replace this line in main.py:

python
Copy
Edit
from commands.offline_ai import chat_with_gpt
with
from commands.ai_chatbot import chat_with_gpt
Also, set your OpenAI API key in a .env file:

env
Copy
Edit
OPENAI_API_KEY=your_api_key_here


## 📌 Dependencies

        gpt4all
        pyttsx3
        speechrecognition
        pyaudio
        psutil
        requests
        keyboard
        python-dotenv
    

## 🛡️ Disclaimer
This assistant can perform file operations and system commands. Use with caution to avoid unintended file deletion or system shutdown.


## 📣 Contribute
Have ideas to make it better? Feel free to open an issue or a pull request.

## 📃 License
MIT License

## ✨ Author
Built with ❤️ by MAYANK CHOUHAN
