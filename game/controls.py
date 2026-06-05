"""
controls.py — keyboard / joystick mapping helpers.

Kept separate so that both main.py and settings_screen.py can import
resolve_controls without creating a circular dependency.
"""
import pygame


def _key_from_name(name: str, fallback: int) -> int:
    normalized = str(name).replace(" ", "_")
    key = getattr(pygame, f"K_{normalized}", None)
    return key if isinstance(key, int) else fallback


def _key_from_value(value, fallback: int) -> int:
    if isinstance(value, int):
        return value
    return _key_from_name(value, fallback)


def resolve_controls(settings: dict) -> dict:
    """Translate settings dict into a pygame key-code dict."""
    controls = settings.get("controls", {})
    return {
        "left":      _key_from_value(controls.get("left", "left"), pygame.K_LEFT),
        "right":     _key_from_value(controls.get("right", "right"), pygame.K_RIGHT),
        "jump":      _key_from_value(controls.get("jump", "space"), pygame.K_SPACE),
        "pause":     _key_from_value(controls.get("pause", "escape"), pygame.K_ESCAPE),
        "alt_pause": _key_from_value(controls.get("alt_pause", "p"), pygame.K_p),
        "pipe_down": _key_from_value(controls.get("pipe_down", "down"), pygame.K_DOWN),
    }
