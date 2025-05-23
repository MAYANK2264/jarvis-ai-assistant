import speech_recognition as sr
import threading
import queue
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.is_listening = False
        self._recognition_thread = None

    def start_listening(self, callback: Optional[Callable[[str], None]] = None):
        """Start listening in the background"""
        if self.is_listening:
            return

        self.is_listening = True
        self._recognition_thread = threading.Thread(
            target=self._recognition_worker, args=(callback,), daemon=True
        )
        self._recognition_thread.start()

    def stop_listening(self):
        """Stop the background listening"""
        self.is_listening = False
        if self._recognition_thread:
            self._recognition_thread.join()
            self._recognition_thread = None

    def _recognition_worker(self, callback: Optional[Callable[[str], None]]):
        """Background worker for speech recognition"""
        while self.is_listening:
            try:
                with sr.Microphone() as source:
                    logger.debug("Listening for speech...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(
                        source, timeout=5, phrase_time_limit=10
                    )

                try:
                    text = self.recognizer.recognize_google(audio)
                    logger.info(f"Recognized: {text}")
                    if callback:
                        callback(text)
                    self.result_queue.put(text)
                except sr.UnknownValueError:
                    logger.debug("Speech not understood")
                except sr.RequestError as e:
                    logger.error(f"Could not request results: {str(e)}")

            except Exception as e:
                logger.error(f"Error in recognition worker: {str(e)}")
                if not self.is_listening:
                    break

    def get_last_result(self) -> Optional[str]:
        """Get the last recognition result if available"""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None


# Global recognizer instance
_recognizer = None


def get_recognizer() -> SpeechRecognizer:
    """Get or create the global recognizer instance"""
    global _recognizer
    if _recognizer is None:
        _recognizer = SpeechRecognizer()
    return _recognizer


def recognize_speech() -> Optional[str]:
    """Legacy synchronous recognition function"""
    recognizer = get_recognizer()
    if not recognizer.is_listening:
        recognizer.start_listening()
    return recognizer.get_last_result()
