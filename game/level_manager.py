"""
Level management helpers.

Centralises level loading, difficulty configuration, biome modifiers,
secret-token generation, and coin-goal derivation.  Previously these
were scattered across main.py (and duplicated in every state branch
that needed to (re-)load a level).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from game.constants import DIFFICULTY_PRESETS, BASE_TIME_LIMIT, LEVEL_END_X, BIOMES, level_width
from game.levels import create_normal_level, create_secret_level, create_boss_level
from game.objects import SecretToken

if TYPE_CHECKING:
    from game.context import GameContext


# ---------------------------------------------------------------------------
# Low-level helpers (pure functions, no context dependency)
# ---------------------------------------------------------------------------

def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def configure_level_difficulty(level_num: int, in_secret_world: bool,
                               enemies: List[Any], boss: Optional[Any],
                               balance: Dict) -> None:
    """Scale enemy/boss speed/cooldowns based on level number and balance settings."""
    scale = 1.0 + max(0, level_num - 1) * balance.get("difficulty_per_level", 0.05)
    if in_secret_world:
        scale = 1.0

    for enemy in enemies:
        enemy.speed = clamp(enemy.speed * scale, 1.5, 5.5)
        if enemy.enemy_type == "badminton":
            enemy.shoot_cooldown = int(clamp(enemy.shoot_cooldown / scale, 60, 150))

    if boss:
        boss.speed = clamp(boss.speed * scale, 1.2, 4.5)
        boss.slipper_cooldown = int(clamp(boss.slipper_cooldown / scale, 35, 100))


def get_biome_name(level_num: int, in_secret_world: bool) -> Optional[str]:
    """Return the biome name for levels >= 10 (non-boss, non-secret)."""
    if in_secret_world or level_num < 10 or level_num % 3 == 0:
        return None
    # Cycle through biomes for levels 10+
    biome_cycle = ["ice", "lava", "underwater"]
    idx = ((level_num - 10) // 2) % len(biome_cycle)
    return biome_cycle[idx]


def get_biome_modifiers(level_num: int, in_secret_world: bool) -> Dict[str, Any]:
    """Return wind, gravity, friction, and other modifiers for the given level."""
    if in_secret_world:
        return {"wind": 0.0, "gravity": 0.9, "friction": 1.0}

    biome = get_biome_name(level_num, in_secret_world)
    if biome and biome in BIOMES:
        return dict(BIOMES[biome])

    pattern = level_num % 4
    if pattern == 0:
        return {"wind": 0.25, "gravity": 1.0, "friction": 1.0}
    if pattern == 3:
        return {"wind": 0.0, "gravity": 0.92, "friction": 1.0}
    return {"wind": 0.0, "gravity": 1.0, "friction": 1.0}


def build_secret_tokens(level_num: int, in_secret_world: bool) -> List[SecretToken]:
    if in_secret_world:
        return [SecretToken(360, 220), SecretToken(980, 190), SecretToken(1600, 240)]
    if level_num % 2 == 0:
        return [SecretToken(620, 260), SecretToken(1450, 240)]
    return [SecretToken(800, 220)]


def derive_coin_goal(coins: List[Any], balance: Dict) -> int:
    ratio = float(balance.get("coin_goal_ratio", 0.6))
    return max(3, int(len(coins) * ratio))


# ---------------------------------------------------------------------------
# High-level helpers that operate on a GameContext
# ---------------------------------------------------------------------------

def _configure_ctx(ctx: "GameContext") -> None:
    """Apply difficulty, tokens and coin-goal to ctx after a level load."""
    ctx.level_end_x = level_width(ctx.current_level)
    configure_level_difficulty(
        ctx.current_level, ctx.in_secret_world,
        ctx.enemies, ctx.boss, ctx.balance,
    )
    ctx.secret_tokens = build_secret_tokens(ctx.current_level, ctx.in_secret_world)
    ctx.coin_goal = derive_coin_goal(ctx.coins, ctx.balance)
    ctx.coin_goal_done = False
    # Level timer
    ctx.level_timer = 0.0
    ctx.level_time_limit = BASE_TIME_LIMIT * (1 + ctx.current_level * 0.1)
    ctx.time_bonus_earned = False
    # Biome
    ctx.biome_name = get_biome_name(ctx.current_level, ctx.in_secret_world)
    ctx.lava_y = 650.0  # reset lava below screen


def load_normal_level(ctx: "GameContext") -> None:
    """Load a normal (non-boss) level into ctx."""
    from game import audio
    ctx.boss = None
    (ctx.platforms, ctx.enemies, ctx.coins,
     ctx.pipes, ctx.flag, ctx.powerups, ctx.mom) = create_normal_level(ctx.current_level)
    _configure_ctx(ctx)
    audio.return_to_normal_music()


def load_boss_level(ctx: "GameContext") -> None:
    """Load a boss level into ctx."""
    from game import audio
    boss_level = ctx.current_level // 3
    (ctx.platforms, ctx.enemies, ctx.coins,
     ctx.pipes, ctx.flag, ctx.powerups, ctx.boss) = create_boss_level(boss_level)
    ctx.mom = None
    _configure_ctx(ctx)
    audio.start_boss_music()


def load_secret_level(ctx: "GameContext") -> None:
    """Load a secret (warp-pipe) level into ctx."""
    from game import audio
    ctx.boss = None
    (ctx.platforms, ctx.enemies, ctx.coins,
     ctx.pipes, ctx.flag, ctx.powerups, ctx.mom) = create_secret_level(ctx.secret_world_type)
    _configure_ctx(ctx)
    audio.return_to_normal_music()


def load_level_for_ctx(ctx: "GameContext") -> None:
    """Choose the right loader based on current level and world state."""
    if ctx.in_secret_world:
        load_secret_level(ctx)
    elif ctx.current_level % 3 == 0:
        load_boss_level(ctx)
    else:
        load_normal_level(ctx)


def reset_checkpoint(ctx: "GameContext") -> None:
    ctx.checkpoint_x = 120
    ctx.checkpoint_reached = False


def reset_camera(ctx: "GameContext") -> None:
    ctx.camera_x = 0


def apply_player_profile(ctx: "GameContext") -> None:
    """Sync balance settings into the player object."""
    player = ctx.player
    balance = ctx.balance
    player.coyote_frames = int(balance.get("coyote_frames", 7))
    player.jump_buffer_frames = int(balance.get("jump_buffer_frames", 8))
    player.short_hop_gravity_boost = float(balance.get("short_hop_gravity_boost", 0.55))
    if ctx.settings.get("assist_mode"):
        player.lives = max(player.lives, 3)


# ---------------------------------------------------------------------------
# Canonical reset helpers (used by every screen that restarts the game)
# ---------------------------------------------------------------------------

def reset_full_game(ctx: "GameContext") -> None:
    """Full game reset: new player, level 1, score 0, clear switch parts."""
    from game.player import Player
    ctx.player = Player()
    apply_player_profile(ctx)
    ctx.current_level = 1
    ctx.score = 0
    ctx.in_secret_world = False
    ctx.switch_parts = {'left_controller': False, 'right_controller': False, 'screen': False}
    ctx.switch_parts_count = 0
    ctx.tokens_collected = 0
    load_normal_level(ctx)
    reset_checkpoint(ctx)
    reset_camera(ctx)
    ctx.coin_goal_done = False


def start_chosen_level(ctx: "GameContext", level: int) -> None:
    """Start a specific level from level select (resets score & switch parts)."""
    from game.player import Player
    ctx.player = Player()
    apply_player_profile(ctx)
    ctx.current_level = level
    ctx.score = 0
    ctx.in_secret_world = False
    ctx.switch_parts = {'left_controller': False, 'right_controller': False, 'screen': False}
    ctx.switch_parts_count = 0
    ctx.tokens_collected = 0
    if level % 3 == 0:
        load_boss_level(ctx)
    else:
        load_normal_level(ctx)
    reset_checkpoint(ctx)
    reset_camera(ctx)
    ctx.coin_goal_done = False


def restart_current_level(ctx: "GameContext") -> None:
    """Restart current level preserving lives and score."""
    from game.player import Player
    saved_lives = ctx.player.lives
    ctx.player = Player()
    apply_player_profile(ctx)
    ctx.player.lives = max(saved_lives, 3) if ctx.settings.get("assist_mode") else saved_lives
    load_level_for_ctx(ctx)
    reset_checkpoint(ctx)
    reset_camera(ctx)
    ctx.pipe_entry_timer = 0
    ctx.coin_goal_done = False


def go_home(ctx: "GameContext") -> None:
    """Return to home screen (reset level/score but not switch parts)."""
    from game.player import Player
    ctx.player = Player()
    apply_player_profile(ctx)
    ctx.current_level = 1
    ctx.score = 0
    ctx.in_secret_world = False
    ctx.boss = None
    load_normal_level(ctx)
    reset_checkpoint(ctx)
    reset_camera(ctx)
    ctx.pipe_entry_timer = 0
    ctx.coin_goal_done = False
