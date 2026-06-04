import json
from pathlib import Path

HIGHSCORE_FILE = Path("highscore.json")
SETTINGS_FILE = Path("settings.json")
PROGRESS_FILE = Path("progress.json")


def load_high_score() -> int:
    """Load the high score from disk."""
    try:
        if HIGHSCORE_FILE.exists():
            with HIGHSCORE_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
                return int(data.get("high_score", 0))
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    return 0


def save_high_score(score: int) -> None:
    """Persist the high score to disk."""
    try:
        with HIGHSCORE_FILE.open("w", encoding="utf-8") as file:
            json.dump({"high_score": int(score)}, file)
    except OSError:
        pass


def update_high_score(current_score: int) -> tuple[bool, int]:
    """Update score if current score is a new high score."""
    high_score = load_high_score()
    if current_score > high_score:
        save_high_score(current_score)
        return True, current_score
    return False, high_score


def load_json(path: Path, default: dict) -> dict:
    try:
        if path.exists():
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    return data
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    return dict(default)


def save_json(path: Path, payload: dict) -> None:
    try:
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file)
    except OSError:
        pass


def load_settings(default: dict) -> dict:
    return load_json(SETTINGS_FILE, default)


def save_settings(settings: dict) -> None:
    save_json(SETTINGS_FILE, settings)


def load_progress(default: dict) -> dict:
    return load_json(PROGRESS_FILE, default)


def save_progress(progress: dict) -> None:
    save_json(PROGRESS_FILE, progress)
