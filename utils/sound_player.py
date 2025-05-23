import pygame
import os
import threading
from pathlib import Path


class SoundPlayer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundPlayer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        pygame.mixer.init()
        self._initialized = True

    def play_sound(self, sound_file: str, duration: float = None):
        """Play a sound file

        Args:
            sound_file: Path to the sound file
            duration: Optional duration to play (in seconds)
        """

        def _play():
            try:
                sound = pygame.mixer.Sound(sound_file)
                sound.play()
                if duration:
                    pygame.time.wait(int(duration * 1000))
                    sound.stop()
            except Exception as e:
                print(f"Error playing sound: {str(e)}")

        # Play in background thread to avoid blocking
        thread = threading.Thread(target=_play)
        thread.daemon = True
        thread.start()


# Global instance
_sound_player = None


def get_sound_player() -> SoundPlayer:
    global _sound_player
    if _sound_player is None:
        _sound_player = SoundPlayer()
    return _sound_player
