"""LEVEL COMPLETE screen."""
from __future__ import annotations

from typing import TYPE_CHECKING, List

import pygame

from game import audio
from game.constants import BLACK, GOLDEN, RED, WHITE, YELLOW, WIDTH, HEIGHT
from game.persistence import update_high_score, save_progress
from game.player import Player
from game.renderer import get_font
from game.states import GameState
from game.level_manager import (
    load_normal_level, load_boss_level, apply_player_profile,
    reset_checkpoint, reset_camera,
)

if TYPE_CHECKING:
    from game.context import GameContext

_sound_played = False
_level_complete_sound = None


def handle(ctx: "GameContext", screen: pygame.Surface,
           keydown_events: List[int], keys) -> GameState:
    global _sound_played, _level_complete_sound
    if not _sound_played:
        if _level_complete_sound is None:
            _level_complete_sound = audio.create_sound_effect(1000, 0.4, 0.5)
        audio.play_sound(_level_complete_sound)
        _sound_played = True
        # Update high score on level complete (not just game over)
        is_new, hs = update_high_score(ctx.score)
        ctx.high_score = hs
        ctx.progress["best_score"] = max(int(ctx.progress.get("best_score", 0)), ctx.score)

    screen.fill(BLACK)
    if ctx.current_level % 3 == 0:
        msg = get_font(64).render("Boss Defeated!", True, YELLOW)
    else:
        msg = get_font(64).render("Level Complete!", True, YELLOW)
    score_display = get_font(36).render(f"Score: {ctx.score}", True, GOLDEN)
    level_display = get_font(36).render(f"Level: {ctx.current_level}", True, WHITE)
    high_score_display = get_font(32).render(f"High Score: {ctx.high_score}", True, GOLDEN)
    prompt = get_font(36).render("Press SPACE for Next Level", True, WHITE)

    screen.blit(msg, ((WIDTH - msg.get_width()) // 2, HEIGHT // 2 - 70))
    screen.blit(score_display, ((WIDTH - score_display.get_width()) // 2, HEIGHT // 2 - 20))
    screen.blit(level_display, ((WIDTH - level_display.get_width()) // 2, HEIGHT // 2 + 10))
    screen.blit(high_score_display, ((WIDTH - high_score_display.get_width()) // 2, HEIGHT // 2 + 40))
    screen.blit(prompt, ((WIDTH - prompt.get_width()) // 2, HEIGHT // 2 + 80))

    if keys[ctx.controls["jump"]]:
        _sound_played = False
        _advance_level(ctx)
        return GameState.PLAY

    return GameState.COMPLETE


def _advance_level(ctx: "GameContext") -> None:
    """Save powerup state, advance level, reload."""
    saved = (
        ctx.player.lives,
        ctx.player.speed_boost,
        ctx.player.jump_boost,
        ctx.player.immunity_timer,
        ctx.player.speed_timer,
        ctx.player.jump_timer,
    )
    ctx.player = Player()
    apply_player_profile(ctx)

    # Restore powerups
    (ctx.player.lives, ctx.player.speed_boost, ctx.player.jump_boost,
     ctx.player.immunity_timer, ctx.player.speed_timer, ctx.player.jump_timer) = saved
    if ctx.settings.get("assist_mode"):
        ctx.player.lives = max(saved[0], 3)

    ctx.current_level += 1
    ctx.progress["unlocked_level"] = max(
        int(ctx.progress.get("unlocked_level", 1)), ctx.current_level
    )
    save_progress(ctx.progress)

    if ctx.current_level % 3 == 0:
        load_boss_level(ctx)
    else:
        load_normal_level(ctx)

    reset_checkpoint(ctx)
    reset_camera(ctx)
    ctx.coin_goal_done = False
