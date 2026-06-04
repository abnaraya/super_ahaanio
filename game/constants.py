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

LEVEL_END_X = 2000

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
