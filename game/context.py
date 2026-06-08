"""
GameContext — a single object that carries all mutable game state.

Passing one context object between screen handlers is cleaner than
threading dozens of local variables through function signatures.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from game.states import GameState


@dataclass
class GameContext:
    # --- Core state machine ---
    state: GameState = GameState.START

    # --- Scoring & progression ---
    score: int = 0
    high_score: int = 0
    current_level: int = 1

    # --- Entities ---
    player: Any = None
    platforms: List[Any] = field(default_factory=list)
    enemies: List[Any] = field(default_factory=list)
    coins: List[Any] = field(default_factory=list)
    pipes: List[Any] = field(default_factory=list)
    flag: Any = None
    powerups: List[Any] = field(default_factory=list)
    mom: Any = None
    boss: Any = None
    particles: List[Any] = field(default_factory=list)
    secret_tokens: List[Any] = field(default_factory=list)

    # --- Camera & viewport ---
    level_end_x: int = 2000
    camera_x: float = 0.0
    screen_shake: int = 0

    # --- Combo system ---
    combo_count: int = 0
    combo_timer: int = 0

    # --- Coin goal ---
    coin_goal: int = 0
    coin_goal_done: bool = False

    # --- Checkpoint ---
    checkpoint_x: int = 120
    checkpoint_reached: bool = False

    # --- Secret world ---
    in_secret_world: bool = False
    secret_world_type: int = 1
    return_level: int = 1
    return_score: int = 0
    pipe_entry_timer: int = 0

    # --- Nintendo Switch parts ---
    switch_parts: Dict[str, bool] = field(default_factory=lambda: {
        'left_controller': False,
        'right_controller': False,
        'screen': False,
    })
    switch_parts_count: int = 0

    # --- Token tracking ---
    tokens_collected: int = 0
    token_milestone_text: str = ""
    token_milestone_timer: int = 0

    # --- Soccer ball projectiles ---
    soccer_balls: List[Any] = field(default_factory=list)

    # --- Hit freeze (juice) ---
    hit_freeze: int = 0

    # --- Level timer ---
    level_timer: float = 0.0
    level_time_limit: float = 0.0
    time_bonus_earned: bool = False

    # --- Biome ---
    biome_name: Optional[str] = None
    lava_y: float = 650.0        # rising lava Y position (starts below screen)

    # --- Pause menu ---
    game_paused: bool = False
    pause_menu_selection: int = 0

    # --- Settings & controls ---
    settings: Dict[str, Any] = field(default_factory=dict)
    balance: Dict[str, Any] = field(default_factory=dict)
    controls: Dict[str, int] = field(default_factory=dict)

    # --- Audio ---
    music_playing: bool = False
    music_volume: float = 0.15

    # --- Progress (unlocked levels, best score) ---
    progress: Dict[str, Any] = field(default_factory=dict)

    # --- UI helpers ---
    settings_menu_selection: int = 0
    settings_return_state: GameState = GameState.START
    rebinding_action: Optional[str] = None
    level_select_cursor: int = 0

    # --- Story / cutscene ---
    story_page: int = 0
    cutscene_timer: int = 0
    cutscene_segments: List[str] = field(default_factory=lambda: [
        "INTRO_WORLD",
        "INTRO_AHAAN_INTERESTS",
        "INTRO_AHAAN_SPORTS",
        "INTRO_CHALLENGES",
        "SWITCH_GAMING",
        "MOM_APPEARS",
        "SWITCH_BREAKS",
        "CHASE_BEGINS",
        "READY_TO_PLAY",
    ])

    # --- Edge-triggered key tracking ---
    input_state: Dict[str, bool] = field(default_factory=lambda: {
        "story_last_space": False,
        "pause_key_pressed": False,
        "up_key_pressed": False,
        "down_key_pressed": False,
        "select_key_pressed": False,
    })

    # --- Transitions ---
    transition: Any = None

    # --- Joystick ---
    joystick: Any = None
    prev_joy_jump: bool = False
