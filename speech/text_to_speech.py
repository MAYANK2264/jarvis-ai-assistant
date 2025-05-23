import pyttsx3
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TextToSpeech:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            # Configure voice settings
            self.engine.setProperty('rate', 150)    # Speed of speech
            self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
            
            # Get available voices and set a good quality one
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if "english" in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
                    
        except Exception as e:
            logger.error(f"Failed to initialize text-to-speech engine: {str(e)}")
            self.engine = None

    def speak(self, text: str) -> bool:
        """Speak the given text.
        
        Args:
            text: Text to speak
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not text:
            return False
            
        if not self.engine:
            logger.error("Text-to-speech engine not initialized")
            return False
            
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            logger.info(f"Speaking: {text}")
            return True
        except Exception as e:
            logger.error(f"Failed to speak text: {str(e)}")
            return False

# Global TTS instance
_tts_engine = None

def get_tts_engine() -> TextToSpeech:
    """Get or create the global TTS instance."""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TextToSpeech()
    return _tts_engine

def speak(text: str) -> bool:
    """Speak the given text using the global TTS instance."""
    return get_tts_engine().speak(text)
