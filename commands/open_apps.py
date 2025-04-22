import os

def open_application(command):
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    }

    for key in apps:
        if key in command.lower():
            os.startfile(apps[key])
            return f"Opening {key}"
    return "I couldn't recognize the app to open."
