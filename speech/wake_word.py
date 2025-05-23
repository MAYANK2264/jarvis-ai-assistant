import pvporcupine
import pyaudio
import struct
import threading
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class WakeWordDetector:
    def __init__(
        self,
        access_key: str,
        wake_word: str = "jarvis",
        on_wake_word: Optional[Callable[[], None]] = None,
    ):
        """Initialize wake word detector

        Args:
            access_key: Picovoice access key
            wake_word: Wake word to detect (default: "jarvis")
            on_wake_word: Callback function when wake word is detected
        """
        self.porcupine = None
        self.pa = None
        self.audio_stream = None
        self.access_key = access_key
        self.wake_word = wake_word
        self.on_wake_word = on_wake_word
        self._thread = None
        self.is_running = False

    def start(self):
        """Start wake word detection in background thread"""
        if self.is_running:
            return

        try:
            self.porcupine = pvporcupine.create(
                access_key=self.access_key, keywords=[self.wake_word]
            )

            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length,
            )

            self.is_running = True
            self._thread = threading.Thread(target=self._detection_loop)
            self._thread.daemon = True
            self._thread.start()
            logger.info("Wake word detection started")

        except Exception as e:
            logger.error(f"Failed to start wake word detection: {str(e)}")
            self.cleanup()
            raise

    def stop(self):
        """Stop wake word detection"""
        self.is_running = False
        if self._thread:
            self._thread.join()
        self.cleanup()
        logger.info("Wake word detection stopped")

    def cleanup(self):
        """Clean up resources"""
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()

        if self.pa:
            self.pa.terminate()

        if self.porcupine:
            self.porcupine.delete()

        self.audio_stream = None
        self.pa = None
        self.porcupine = None

    def _detection_loop(self):
        """Main detection loop"""
        while self.is_running:
            try:
                pcm = self.audio_stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)

                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    logger.info("Wake word detected!")
                    if self.on_wake_word:
                        self.on_wake_word()

            except Exception as e:
                logger.error(f"Error in detection loop: {str(e)}")
                break

        self.cleanup()
