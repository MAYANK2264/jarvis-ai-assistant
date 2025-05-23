import requests
import random
import json
import os
from datetime import datetime

# Enhanced fallback responses for more natural conversation
FALLBACK_RESPONSES = [
    "I'm here to help. Could you rephrase that?",
    "I want to help you better. Can you explain that differently?",
    "I'm not quite sure I understood. Could you say that another way?",
    "I'm learning all the time. Could you try asking that differently?",
]

# Personality traits for more human-like responses
PERSONALITY_TRAITS = {
    "friendly": True,
    "helpful": True,
    "polite": True,
    "knowledgeable": True
}

# Common conversation patterns
CONVERSATION_PATTERNS = {
    "greeting": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"],
    "farewell": ["bye", "goodbye", "see you", "talk to you later"],
    "gratitude": ["thanks", "thank you", "appreciate it"],
    "affirmative": ["yes", "yeah", "sure", "okay"],
    "negative": ["no", "nope", "not really"],
}

# Contextual responses for common patterns
CONTEXTUAL_RESPONSES = {
    "greeting": [
        "Hello! How can I assist you today?",
        "Hi there! What can I help you with?",
        "Greetings! How may I be of service?",
    ],
    "farewell": [
        "Goodbye! Have a great day!",
        "See you later! Don't hesitate to ask if you need anything.",
        "Take care! I'm here if you need help.",
    ],
    "gratitude": [
        "You're welcome! Is there anything else you need?",
        "My pleasure! Let me know if you need more help.",
        "Glad I could help! What else can I do for you?",
    ],
}

class ConversationContext:
    def __init__(self):
        self.context = []
        self.max_context = 5

    def add_to_context(self, message, response):
        self.context.append({"message": message, "response": response, "timestamp": datetime.now()})
        if len(self.context) > self.max_context:
            self.context.pop(0)

    def get_context(self):
        return self.context

# Initialize conversation context
conversation_context = ConversationContext()

def check_internet():
    """Check internet connectivity"""
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def get_pattern_type(command):
    """Identify the type of conversation pattern"""
    command = command.lower()
    for pattern_type, patterns in CONVERSATION_PATTERNS.items():
        if any(pattern in command for pattern in patterns):
            return pattern_type
    return None

def generate_contextual_response(pattern_type):
    """Generate a contextual response based on the pattern type"""
    if pattern_type in CONTEXTUAL_RESPONSES:
        return random.choice(CONTEXTUAL_RESPONSES[pattern_type])
    return None

def chat_with_gpt_offline(command):
    """Enhanced offline chatbot with better conversation handling"""
    try:
        # Check for conversation patterns
        pattern_type = get_pattern_type(command)
        if pattern_type:
            response = generate_contextual_response(pattern_type)
            if response:
                conversation_context.add_to_context(command, response)
                return response

        # Process general queries
        # This is where you would integrate with your offline AI model (e.g., GPT4All)
        # For now, we'll use a simple response system
        response = process_general_query(command)
        conversation_context.add_to_context(command, response)
        return response

    except Exception as e:
        print(f"Error in offline processing: {e}")
        return random.choice(FALLBACK_RESPONSES)

def process_general_query(command):
    """Process general queries with more natural responses"""
    command = command.lower()
    
    # Time-related queries
    if "time" in command:
        return f"It's {datetime.now().strftime('%I:%M %p')}."
    
    # Weather-related queries (placeholder)
    if "weather" in command:
        return "I'm sorry, I can't check the weather right now as it requires internet connectivity."
    
    # General knowledge queries
    if any(word in command for word in ["what", "who", "where", "when", "why", "how"]):
        return "I'm designed to help with system tasks and basic conversations. For detailed information, you might want to try an online search."
    
    # Personal queries
    if "your name" in command:
        return "I'm Jarvis, your AI assistant. I'm here to help you with various tasks."
    
    if "how are you" in command:
        return "I'm functioning well, thank you for asking! How can I assist you today?"
    
    # Default response with context awareness
    context = conversation_context.get_context()
    if context:
        last_interaction = context[-1]
        return f"I'm here to help you. Previously we talked about {last_interaction['message'][:30]}... What would you like to know about that or something else?"
    
    return "I'm here to help. What would you like me to do for you?"

def chat_with_gpt(command):
    """Main chat function with online/offline handling"""
    if check_internet():
        try:
            # Try online model first
            response = get_online_ai_response(command)
            if response:
                return response
        except Exception as e:
            print(f"Error with online model: {e}")
            # Fallback to offline
            return chat_with_gpt_offline(command)
    else:
        # Use offline model
        return chat_with_gpt_offline(command)

def get_online_ai_response(command):
    """Get response from online AI model"""
    try:
        # Implement your online AI API call here
        # For now, we'll use the offline response
        return chat_with_gpt_offline(command)
    except Exception as e:
        print(f"Error with online model: {e}")
        return random.choice(FALLBACK_RESPONSES)
