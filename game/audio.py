import logging

import pygame
import numpy as np

logger = logging.getLogger(__name__)

MUSIC_AVAILABLE = False
current_music_type = "normal"


def initialize_music(track_path: str = "bgm.mp3") -> bool:
    global MUSIC_AVAILABLE
    try:
        pygame.mixer.music.load(track_path)
        MUSIC_AVAILABLE = True
    except pygame.error:
        logger.debug("Music file not found, continuing without music")
        MUSIC_AVAILABLE = False
    return MUSIC_AVAILABLE


def create_sound_effect(frequency: float, duration: float, volume: float = 0.5):
    if not MUSIC_AVAILABLE:
        return None
    try:
        sample_rate = 22050
        frames = int(duration * sample_rate)
        t = np.linspace(0, duration, frames, False)
        fundamental = np.sin(2 * np.pi * frequency * t)
        harmonics = 0.3 * np.sin(2 * np.pi * frequency * 2 * t)
        square_component = 0.2 * np.sign(np.sin(2 * np.pi * frequency * t))
        wave = fundamental + harmonics + square_component
        envelope = np.exp(-t * 4)
        wave = wave * envelope * volume
        wave = np.clip(wave, -1.0, 1.0)
        wave = (wave * 32767).astype(np.int16)
        stereo_wave = np.column_stack((wave, wave))
        return pygame.sndarray.make_sound(stereo_wave)
    except Exception as exc:
        logger.debug("Could not create sound effect: %s", exc)
        return None


def play_sound(sound) -> None:
    if sound and MUSIC_AVAILABLE:
        try:
            if hasattr(sound, "play"):
                sound.play()
            else:
                logger.debug("Sound effect has no play method")
        except Exception as exc:
            logger.debug("Could not play sound: %s", exc)


def start_background_music(track_path: str = "bgm.mp3", normal_volume: float = 0.15) -> None:
    global current_music_type
    if MUSIC_AVAILABLE:
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(-1, 0.0)
            pygame.mixer.music.set_volume(normal_volume)
            current_music_type = "normal"
        except Exception:
            pass


def start_boss_music(boss_volume: float = 0.35) -> None:
    global current_music_type
    if MUSIC_AVAILABLE and current_music_type != "boss":
        try:
            pygame.mixer.music.set_volume(boss_volume)
            current_music_type = "boss"
        except Exception as exc:
            logger.debug("Error starting boss music: %s", exc)
            current_music_type = "boss"


def stop_background_music() -> None:
    global current_music_type
    if MUSIC_AVAILABLE:
        try:
            pygame.mixer.music.stop()
            current_music_type = "normal"
        except Exception:
            pass


def return_to_normal_music(normal_volume: float = 0.15) -> None:
    global current_music_type
    if MUSIC_AVAILABLE and current_music_type == "boss":
        try:
            pygame.mixer.music.set_volume(normal_volume)
            current_music_type = "normal"
        except Exception as exc:
            logger.debug("Error returning to normal music: %s", exc)
            current_music_type = "normal"


def set_music_volume(volume: float) -> None:
    if MUSIC_AVAILABLE:
        try:
            pygame.mixer.music.set_volume(volume)
        except Exception:
            pass
