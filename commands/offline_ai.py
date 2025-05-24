import requests
import random
import json
import os
from datetime import datetime
import re
from typing import Optional, Dict, List, Any

# Enhanced fallback responses with more specific suggestions
FALLBACK_RESPONSES = [
    "I'm not sure I understood. Are you asking about: \n1. System tasks\n2. General information\n3. Personal assistance\nPlease specify or rephrase your question.",
    "Could you be more specific? For example:\n- 'What time is it?'\n- 'Create a new folder'\n- 'How do I [specific task]?'",
    "I want to help, but I need more context. Could you:\n1. Be more specific\n2. Provide an example\n3. Break down your request",
    "I'm having trouble understanding. Could you:\n1. Use simpler terms\n2. Ask one question at a time\n3. Provide more details",
]

# Personality traits for more human-like responses
PERSONALITY_TRAITS = {
    "friendly": True,
    "helpful": True,
    "polite": True,
    "knowledgeable": True
}

# Enhanced conversation patterns with more variations and categories
CONVERSATION_PATTERNS = {
    "greeting": [
        "hi", "hello", "hey", "good morning", "good afternoon", 
        "good evening", "greetings", "hi there", "hello there"
    ],
    "farewell": [
        "bye", "goodbye", "see you", "talk to you later", "bye bye",
        "have a good day", "catch you later", "until next time"
    ],
    "gratitude": [
        "thanks", "thank you", "appreciate it", "grateful",
        "thanks a lot", "thank you very much", "thanks so much"
    ],
    "affirmative": [
        "yes", "yeah", "sure", "okay", "alright", "fine",
        "certainly", "absolutely", "indeed"
    ],
    "negative": [
        "no", "nope", "not really", "negative", "not at all",
        "don't think so", "definitely not"
    ],
    "help": [
        "help", "assist", "support", "guide", "how do i",
        "how to", "what is", "explain"
    ],
    "system": [
        "file", "folder", "directory", "create", "delete", "move",
        "copy", "rename", "list", "show"
    ]
}

# Enhanced contextual responses with more natural language variations
CONTEXTUAL_RESPONSES = {
    "greeting": [
        "Hello! I'm your AI assistant. How can I help you today?",
        "Hi there! I'm ready to assist you with any tasks or questions.",
        "Greetings! I'm here to help. What would you like to do?",
        "Hello! I can help you with file management, answer questions, or assist with tasks. What do you need?"
    ],
    "farewell": [
        "Goodbye! Don't hesitate to return if you need anything else.",
        "See you later! Remember, I'm here 24/7 if you need assistance.",
        "Take care! Feel free to come back anytime you need help.",
        "Goodbye! I'll be here when you need me next time."
    ],
    "gratitude": [
        "You're welcome! Is there anything else you'd like help with?",
        "My pleasure! Don't hesitate to ask if you need more assistance.",
        "Glad I could help! Remember, I'm here for any other questions.",
        "You're welcome! Let me know if you need clarification on anything."
    ],
    "help": [
        "I can help you with:\n1. File management (create, delete, move files)\n2. System information\n3. General questions\nWhat would you like to know?",
        "Sure! I can assist with various tasks. Could you specify what type of help you need?",
        "I'm here to help! To better assist you, could you specify your request?"
    ]
}

class ConversationContext:
    def __init__(self):
        self.context = []
        self.max_context = 5
        self.last_topic = None
        self.topic_history = []

    def add_to_context(self, message: str, response: str, topic: Optional[str] = None):
        """Add a message-response pair to the conversation context."""
        self.context.append({
            "message": message,
            "response": response,
            "timestamp": datetime.now(),
            "topic": topic or self._detect_topic(message)
        })
        if len(self.context) > self.max_context:
            self.context.pop(0)
        
        if topic:
            self.last_topic = topic
            self.topic_history.append(topic)
            if len(self.topic_history) > self.max_context:
                self.topic_history.pop(0)

    def _detect_topic(self, message: str) -> str:
        """Detect the topic of a message."""
        message = message.lower()
        for topic, patterns in CONVERSATION_PATTERNS.items():
            if any(pattern in message for pattern in patterns):
                return topic
        return "general"

    def get_context(self) -> List[Dict[str, Any]]:
        """Get the current conversation context."""
        return self.context

    def get_last_topic(self) -> Optional[str]:
        """Get the last discussed topic."""
        return self.last_topic

    def clear_context(self):
        """Clear the conversation context."""
        self.context = []
        self.last_topic = None
        self.topic_history = []

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

def extract_intent(command: str) -> Dict[str, Any]:
    """Extract the intent and entities from a command."""
    command = command.lower()
    intent = {
        "action": None,
        "target": None,
        "parameters": {},
        "type": "unknown"
    }
    
    # Check for system commands
    system_actions = ["create", "delete", "move", "copy", "rename", "list", "show"]
    for action in system_actions:
        if action in command:
            intent["action"] = action
            intent["type"] = "system"
            # Extract target (file/folder)
            if "file" in command:
                intent["target"] = "file"
            elif "folder" in command or "directory" in command:
                intent["target"] = "directory"
            break
    
    # Check for questions
    question_words = ["what", "who", "where", "when", "why", "how"]
    if any(word in command for word in question_words):
        intent["type"] = "question"
        intent["action"] = "answer"
        
    # Check for general queries
    if "time" in command:
        intent["type"] = "query"
        intent["action"] = "get_time"
    elif "weather" in command:
        intent["type"] = "query"
        intent["action"] = "get_weather"
    
    return intent

def process_general_query(command: str) -> str:
    """Process general queries with improved understanding."""
    command = command.lower()
    intent = extract_intent(command)
    
    # Handle system-related queries
    if intent["type"] == "system":
        return f"I understand you want to {intent['action']} a {intent['target']}. Please use the specific command or let me know if you need help with the syntax."
    
    # Handle time queries
    if intent["action"] == "get_time":
        return f"The current time is {datetime.now().strftime('%I:%M %p')}."
    
    # Handle weather queries
    if intent["action"] == "get_weather":
        return "I apologize, but I need internet connectivity to check the weather. Is there something else I can help you with?"
    
    # Handle help queries
    if "help" in command or "how" in command:
        return CONTEXTUAL_RESPONSES["help"][0]
    
    # Handle questions about capabilities
    if "what can you do" in command or "your abilities" in command:
        return ("I can help you with:\n"
                "1. File management (create, delete, move files)\n"
                "2. Answer questions about the system\n"
                "3. Basic task assistance\n"
                "4. Remember our conversation context\n"
                "Please let me know what you'd like to do!")
    
    # Use context for better responses
    context = conversation_context.get_context()
    if context:
        last_interaction = context[-1]
        last_topic = last_interaction["topic"]
        
        if last_topic in ["system", "help"]:
            return ("Based on our previous conversation about "
                   f"{last_topic}, would you like me to:\n"
                   "1. Explain more about that topic\n"
                   "2. Show you how to do something specific\n"
                   "3. Move on to a different topic")
    
    return ("I'm here to help! I can:\n"
            "1. Manage files and folders\n"
            "2. Answer questions\n"
            "3. Assist with tasks\n"
            "Please let me know what you'd like to do.")

def chat_with_gpt_offline(command: str) -> str:
    """Enhanced offline chatbot with better understanding and responses."""
    try:
        # Clean and normalize the input
        command = command.strip()
        if not command:
            return "I'm listening. What would you like me to do?"

        # Check for conversation patterns
        pattern_type = get_pattern_type(command)
        if pattern_type:
            response = generate_contextual_response(pattern_type)
            if response:
                conversation_context.add_to_context(command, response, pattern_type)
                return response

        # Process the command with intent recognition
        intent = extract_intent(command)
        response = process_general_query(command)
        
        # Add to context with detected topic
        conversation_context.add_to_context(
            command, response, 
            topic=intent["type"] if intent["type"] != "unknown" else None
        )
        
        return response

    except Exception as e:
        print(f"Error in offline processing: {e}")
        return random.choice(FALLBACK_RESPONSES)

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
