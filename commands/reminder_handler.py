import threading
import time
from speech.text_to_speech import speak
import datetime
import json
import os

reminders = []

def set_reminder(task, delay_seconds):
    def reminder_thread():
        time.sleep(delay_seconds)
        speak(f"Reminder: {task}")
    
    thread = threading.Thread(target=reminder_thread)
    thread.daemon = True
    thread.start()

    reminders.append((task, delay_seconds))
    return f"Reminder set: {task} in {delay_seconds // 60} minutes."

REMINDER_FILE = "reminders.json"

# Function to load reminders from a file
def load_reminders():
    if os.path.exists(REMINDER_FILE):
        with open(REMINDER_FILE, 'r') as f:
            return json.load(f)
    return []

# Function to save reminders to a file
def save_reminders(reminders):
    with open(REMINDER_FILE, 'w') as f:
        json.dump(reminders, f, indent=4)

# Function to set a reminder
def set_reminder(command):
    try:
        # Example: "Set a reminder for 5 PM: Call John"
        time_str = command.split("for")[1].split(":")[0].strip()
        reminder_text = command.split(":")[1].strip()

        # Parse the time into a datetime object
        reminder_time = datetime.datetime.strptime(time_str, "%I %p")  # 5 PM -> 17:00
        
        # Load existing reminders
        reminders = load_reminders()

        # Add new reminder with the timestamp
        reminder = {
            "time": reminder_time.strftime("%Y-%m-%d %H:%M:%S"),
            "reminder": reminder_text
        }
        reminders.append(reminder)

        # Save updated reminders
        save_reminders(reminders)
        return f"Reminder set for {reminder_time.strftime('%I:%M %p')}: {reminder_text}"

    except Exception as e:
        return f"Error setting reminder: {str(e)}"

# Function to show all reminders
def show_reminders():
    reminders = load_reminders()
    if reminders:
        reminder_list = "\n".join([f"At {rem['time']}: {rem['reminder']}" for rem in reminders])
        return f"Here are your reminders:\n{reminder_list}"
    else:
        return "You have no reminders set."

# Function to delete a reminder
def delete_reminder(reminder_time):
    reminders = load_reminders()
    reminders = [rem for rem in reminders if rem['time'] != reminder_time]
    save_reminders(reminders)
    return f"Reminder for {reminder_time} deleted."

