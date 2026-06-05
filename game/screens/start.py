"""START screen — title menu."""
from __future__ import annotations

from typing import TYPE_CHECKING, List

import pygame

from game import audio
from game.constants import BLACK, GOLDEN, WHITE, YELLOW, FPS
from game.player import Player
from game.renderer import get_font
from game.states import GameState
from game.level_manager import (
    load_normal_level, apply_player_profile, reset_checkpoint, reset_camera,
)

if TYPE_CHECKING:
    from game.context import GameContext


def handle(ctx: "GameContext", screen: pygame.Surface,
           keydown_events: List[int], keys) -> GameState:
    if not ctx.music_playing:
        audio.start_background_music()
        audio.set_music_volume(ctx.music_volume)
        ctx.music_playing = True

    screen.fill(BLACK)
    title = get_font(64).render("Super Ahaanio", True, YELLOW)
    prompt = get_font(36).render("Press SPACE to Start", True, WHITE)
    story_prompt = get_font(28).render("Press ENTER for Story", True, (180, 180, 255))
    settings_prompt = get_font(26).render("Press O for Settings", True, (200, 220, 255))
    level_select_prompt = get_font(26).render("Press L for Level Select", True, (200, 255, 200))
    high_score_display = get_font(32).render(f"High Score: {ctx.high_score}", True, GOLDEN)

    W, H = screen.get_size()
    screen.blit(title, ((W - title.get_width()) // 2, H // 2 - 100))
    screen.blit(prompt, ((W - prompt.get_width()) // 2, H // 2 - 20))
    screen.blit(story_prompt, ((W - story_prompt.get_width()) // 2, H // 2 + 30))
    screen.blit(settings_prompt, ((W - settings_prompt.get_width()) // 2, H // 2 + 65))
    screen.blit(level_select_prompt, ((W - level_select_prompt.get_width()) // 2, H // 2 + 95))
    screen.blit(high_score_display, ((W - high_score_display.get_width()) // 2, H // 2 + 130))

    if keys[pygame.K_RETURN]:
        ctx.story_page = 0
        ctx.cutscene_timer = 0
        return GameState.STORY

    if pygame.K_o in keydown_events:
        ctx.settings_return_state = GameState.START
        return GameState.SETTINGS

    if pygame.K_l in keydown_events:
        ctx.level_select_cursor = 0
        return GameState.LEVEL_SELECT

    if keys[ctx.controls["jump"]]:
        _start_new_game(ctx)
        return GameState.PLAY

    return GameState.START


def _start_new_game(ctx: "GameContext") -> None:
    from game.player import Player
    ctx.player = Player()
    apply_player_profile(ctx)
    ctx.current_level = 1
    ctx.score = 0
    ctx.in_secret_world = False
    ctx.switch_parts = {'left_controller': False, 'right_controller': False, 'screen': False}
    ctx.switch_parts_count = 0
    load_normal_level(ctx)
    reset_checkpoint(ctx)
    reset_camera(ctx)
    ctx.coin_goal_done = False
