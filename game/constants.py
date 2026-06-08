import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 55, 70)
SKIN = (255, 225, 175)
BLUE = (0, 122, 255)
BROWN = (140, 100, 50)
GREEN = (34, 177, 76)
PIPE_GREEN = (0, 140, 51)
YELLOW = (255, 222, 80)
GOLDEN = (255, 215, 50)
FLAGPOLE = (180, 180, 180)

PLAYER_SIZE = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = -22
GRAVITY = 1

LEVEL_END_X = 2000   # base level width, used as default


def level_width(level_num: int) -> int:
    """Later levels get wider: base 2000, +200 per level, max 4000."""
    return min(2000 + max(0, level_num - 1) * 200, 4000)
COIN_VALUE = 10
MAX_JUMPS = 2
DOUBLE_JUMP_POWER = 0.7       # second jump is 70% of base
BASE_TIME_LIMIT = 60           # seconds per 2000px of level

DEFAULT_SETTINGS = {
    "reduced_motion": False,
    "assist_mode": False,
    "music_volume": 0.15,
    "controls": {
        "left": "left",
        "right": "right",
        "jump": "space",
        "pause": "escape",
        "alt_pause": "p",
        "pipe_down": "down",
    },
    "balance": {
        "coyote_frames": 7,
        "jump_buffer_frames": 8,
        "short_hop_gravity_boost": 0.55,
        "combo_window_frames": 75,
        "difficulty_per_level": 0.05,
        "checkpoint_bonus": 120,
        "coin_goal_bonus": 350,
        "coin_goal_ratio": 0.6,
    },
    "difficulty_preset": "Normal",
}

DEFAULT_PROGRESS = {
    "unlocked_level": 1,
    "best_score": 0,
    "total_tokens": 0,
}

TOKEN_MILESTONES = {
    5: ("extra_life", "+1 Life"),
    10: ("permanent_speed", "Permanent Speed Boost"),
    15: ("permanent_jump", "Permanent Jump Boost"),
    20: ("triple_jump", "Triple Jump Unlocked!"),
}

# Biome definitions (applied in level_manager.get_biome_modifiers)
BIOMES = {
    "ice":        {"wind": 0.0, "gravity": 1.0, "friction": 0.3,
                   "bg_top": (200, 220, 255), "bg_bottom": (240, 248, 255)},
    "lava":       {"wind": 0.0, "gravity": 1.05, "friction": 1.0,
                   "bg_top": (80, 20, 0), "bg_bottom": (200, 80, 20),
                   "rising_hazard": True, "hazard_speed": 0.3},
    "underwater": {"wind": 0.0, "gravity": 0.5, "friction": 0.85,
                   "bg_top": (10, 40, 80), "bg_bottom": (30, 100, 140)},
}

DIFFICULTY_PRESETS = {
    "Easy": {
        "coyote_frames": 9,
        "jump_buffer_frames": 10,
        "short_hop_gravity_boost": 0.48,
        "combo_window_frames": 95,
        "difficulty_per_level": 0.03,
        "checkpoint_bonus": 180,
        "coin_goal_bonus": 420,
        "coin_goal_ratio": 0.5,
    },
    "Normal": {
        "coyote_frames": 7,
        "jump_buffer_frames": 8,
        "short_hop_gravity_boost": 0.55,
        "combo_window_frames": 75,
        "difficulty_per_level": 0.05,
        "checkpoint_bonus": 120,
        "coin_goal_bonus": 350,
        "coin_goal_ratio": 0.6,
    },
    "Hard": {
        "coyote_frames": 6,
        "jump_buffer_frames": 6,
        "short_hop_gravity_boost": 0.65,
        "combo_window_frames": 60,
        "difficulty_per_level": 0.08,
        "checkpoint_bonus": 80,
        "coin_goal_bonus": 260,
        "coin_goal_ratio": 0.72,
    },
}
