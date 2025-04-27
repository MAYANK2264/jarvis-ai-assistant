import requests
import os
import random

# Assume you have a function for offline chat (chat_with_gpt_offline)
from commands.offline_ai import chat_with_gpt_offline

# Predefined fallback responses for error handling
FALLBACK_RESPONSES = [
    "I'm sorry, I couldn't understand that.",
    "Can you please rephrase?",
    "I'm having trouble processing that request right now."
]

# Function to check internet connection
def check_internet():
    try:
        # Send a request to a reliable source to check if the internet is available
        requests.get('https://www.google.com', timeout=5)
        return True
    except requests.ConnectionError:
        return False

# Function for the AI chatbot to interact
def chat_with_gpt(command):
    # Check if internet is available
    if check_internet():
        # Here we use an online model (this could be any API, such as OpenAI's GPT)
        try:
            response = get_online_ai_response(command)
            if response:
                return response
        except Exception as e:
            print(f"Error with online model: {e}")
            return random.choice(FALLBACK_RESPONSES)
    else:
        # Use the offline model if no internet
        try:
            response = chat_with_gpt_offline(command)  # Assuming you have an offline model set up
            if response:
                return response
            else:
                return random.choice(FALLBACK_RESPONSES)
        except Exception as e:
            print(f"Error with offline model: {e}")
            return random.choice(FALLBACK_RESPONSES)

# Function to get response from an online AI model (e.g., OpenAI GPT)
def get_online_ai_response(command):
    try:
        # Send request to your online AI API (e.g., OpenAI, or any other AI API)
        # For the sake of example, we’ll simulate this
        # You’ll replace the below lines with actual API calls
        response = "This is a placeholder for online model response"
        return response
    except Exception as e:
        print(f"Error with online model: {e}")
        return random.choice(FALLBACK_RESPONSES)

