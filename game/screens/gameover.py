"""GAME OVER screen."""
from __future__ import annotations

from typing import TYPE_CHECKING, List

import pygame

from game import audio
from game.constants import BLACK, GOLDEN, RED, WHITE, YELLOW, WIDTH, HEIGHT
from game.persistence import update_high_score
from game.renderer import get_font
from game.states import GameState
from game.level_manager import reset_full_game

if TYPE_CHECKING:
    from game.context import GameContext

# Track whether we already played the sound this frame
_sound_played = False
# Lazily initialised sound object (set on first use)
_game_over_sound = None


def handle(ctx: "GameContext", screen: pygame.Surface,
           keydown_events: List[int], keys) -> GameState:
    global _sound_played, _game_over_sound
    if not _sound_played:
        if _game_over_sound is None:
            _game_over_sound = audio.create_sound_effect(200, 0.5, 0.4)
        audio.play_sound(_game_over_sound)
        _sound_played = True

    is_new_high_score, current_high_score = update_high_score(ctx.score)
    ctx.high_score = current_high_score
    ctx.progress["best_score"] = max(int(ctx.progress.get("best_score", 0)), ctx.score)

    screen.fill(BLACK)
    msg = get_font(64).render("Game Over!", True, RED)
    score_display = get_font(36).render(f"Score: {ctx.score}", True, YELLOW)
    level_display = get_font(36).render(f"Level: {ctx.current_level}", True, WHITE)
    high_score_display = get_font(36).render(f"High Score: {ctx.high_score}", True, GOLDEN)
    prompt = get_font(36).render("Press SPACE to Restart", True, WHITE)

    if is_new_high_score:
        new_record = get_font(48).render("NEW HIGH SCORE!", True, GOLDEN)
        screen.blit(new_record, ((WIDTH - new_record.get_width()) // 2, HEIGHT // 2 - 120))

    screen.blit(msg, ((WIDTH - msg.get_width()) // 2, HEIGHT // 2 - 70))
    screen.blit(score_display, ((WIDTH - score_display.get_width()) // 2, HEIGHT // 2 - 20))
    screen.blit(high_score_display, ((WIDTH - high_score_display.get_width()) // 2, HEIGHT // 2 + 10))
    screen.blit(level_display, ((WIDTH - level_display.get_width()) // 2, HEIGHT // 2 + 40))
    screen.blit(prompt, ((WIDTH - prompt.get_width()) // 2, HEIGHT // 2 + 90))

    if keys[ctx.controls["jump"]]:
        _sound_played = False
        _restart(ctx)
        return GameState.PLAY

    return GameState.GAMEOVER


def _restart(ctx: "GameContext") -> None:
    reset_full_game(ctx)
