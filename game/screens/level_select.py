"""LEVEL SELECT screen."""
from __future__ import annotations

from typing import TYPE_CHECKING, List

import pygame

from game import audio
from game.constants import RED, WHITE, YELLOW, WIDTH, HEIGHT
from game.renderer import get_font
from game.states import GameState
from game.level_manager import (
    load_normal_level, load_boss_level, apply_player_profile,
    reset_checkpoint, reset_camera,
)

if TYPE_CHECKING:
    from game.context import GameContext


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def handle(ctx: "GameContext", screen: pygame.Surface,
           keydown_events: List[int], keys) -> GameState:
    unlocked = int(ctx.progress.get("unlocked_level", 1))
    cols = 5

    # Navigation
    if pygame.K_RIGHT in keydown_events:
        ctx.level_select_cursor = min(ctx.level_select_cursor + 1, unlocked - 1)
    if pygame.K_LEFT in keydown_events:
        ctx.level_select_cursor = max(ctx.level_select_cursor - 1, 0)
    if pygame.K_DOWN in keydown_events:
        ctx.level_select_cursor = min(ctx.level_select_cursor + cols, unlocked - 1)
    if pygame.K_UP in keydown_events:
        ctx.level_select_cursor = max(ctx.level_select_cursor - cols, 0)

    # Draw
    screen.fill((18, 22, 35))
    title = get_font(56).render("Level Select", True, WHITE)
    screen.blit(title, ((WIDTH - title.get_width()) // 2, 30))
    hint = get_font(24).render("Arrows navigate, SPACE select, ESC back", True, (180, 180, 200))
    screen.blit(hint, ((WIDTH - hint.get_width()) // 2, 80))

    cell_w, cell_h = 80, 60
    grid_w = cols * cell_w
    start_x = (WIDTH - grid_w) // 2
    start_y = 120
    for i in range(unlocked):
        r = i // cols
        c = i % cols
        cx = start_x + c * cell_w + cell_w // 2
        cy = start_y + r * cell_h + cell_h // 2
        lvl = i + 1
        selected = i == ctx.level_select_cursor
        is_boss = lvl % 3 == 0
        bg_color = (80, 40, 40) if is_boss else (40, 50, 80)
        border_color = YELLOW if selected else (100, 100, 120)
        pygame.draw.rect(screen, bg_color, (cx - 30, cy - 20, 60, 40), border_radius=6)
        pygame.draw.rect(screen, border_color, (cx - 30, cy - 20, 60, 40), 3, border_radius=6)
        label = get_font(30).render(str(lvl), True, YELLOW if selected else WHITE)
        screen.blit(label, (cx - label.get_width() // 2, cy - label.get_height() // 2))
        if is_boss:
            tag = get_font(16).render("BOSS", True, RED)
            screen.blit(tag, (cx - tag.get_width() // 2, cy + 22))

    if pygame.K_ESCAPE in keydown_events:
        return GameState.START

    if ctx.controls["jump"] in keydown_events or pygame.K_RETURN in keydown_events:
        _start_chosen_level(ctx)
        return GameState.PLAY

    return GameState.LEVEL_SELECT


def _start_chosen_level(ctx: "GameContext") -> None:
    from game.player import Player
    chosen = ctx.level_select_cursor + 1
    ctx.player = Player()
    apply_player_profile(ctx)
    ctx.current_level = chosen
    ctx.score = 0
    ctx.in_secret_world = False
    ctx.switch_parts = {'left_controller': False, 'right_controller': False, 'screen': False}
    ctx.switch_parts_count = 0
    if chosen % 3 == 0:
        load_boss_level(ctx)
    else:
        load_normal_level(ctx)
    reset_checkpoint(ctx)
    reset_camera(ctx)
    ctx.coin_goal_done = False
