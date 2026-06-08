"""LEVEL SELECT screen."""
from __future__ import annotations

from typing import TYPE_CHECKING, List

import pygame

from game import audio
from game.constants import RED, WHITE, YELLOW, WIDTH, HEIGHT
from game.renderer import get_font
from game.states import GameState
from game.level_manager import start_chosen_level

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
    total_tokens = ctx.progress.get("total_tokens", 0)
    token_text = get_font(22).render(f"Secret Tokens: {total_tokens}", True, (180, 100, 255))
    screen.blit(token_text, ((WIDTH - token_text.get_width()) // 2, 100))

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
        is_special = lvl == 5
        if is_boss:
            bg_color = (80, 40, 40)
        elif is_special:
            bg_color = (80, 70, 20)
        else:
            bg_color = (40, 50, 80)
        border_color = YELLOW if selected else (100, 100, 120)
        pygame.draw.rect(screen, bg_color, (cx - 30, cy - 20, 60, 40), border_radius=6)
        pygame.draw.rect(screen, border_color, (cx - 30, cy - 20, 60, 40), 3, border_radius=6)
        label = get_font(30).render(str(lvl), True, YELLOW if selected else WHITE)
        screen.blit(label, (cx - label.get_width() // 2, cy - label.get_height() // 2))
        if is_boss:
            tag = get_font(16).render("BOSS", True, RED)
            screen.blit(tag, (cx - tag.get_width() // 2, cy + 22))
        elif is_special:
            tag = get_font(14).render("BADMINTON", True, YELLOW)
            screen.blit(tag, (cx - tag.get_width() // 2, cy + 22))

    if pygame.K_ESCAPE in keydown_events:
        return GameState.START

    if ctx.controls["jump"] in keydown_events or pygame.K_RETURN in keydown_events:
        _start_chosen_level(ctx)
        return GameState.PLAY

    return GameState.LEVEL_SELECT


def _start_chosen_level(ctx: "GameContext") -> None:
    start_chosen_level(ctx, ctx.level_select_cursor + 1)
