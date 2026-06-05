"""Victory cutscene and Congratulations screens."""
from __future__ import annotations

import math
from typing import TYPE_CHECKING, List

import pygame

from game import audio
from game.constants import (
    BLACK, BLUE, GOLDEN, GREEN, RED, SKIN, WHITE, YELLOW, WIDTH, HEIGHT
)
from game.player import Player
from game.renderer import get_font
from game.states import GameState
from game.level_manager import load_normal_level, apply_player_profile, reset_checkpoint, reset_camera

if TYPE_CHECKING:
    from game.context import GameContext


def handle_victory_cutscene(ctx: "GameContext", screen: pygame.Surface,
                             keydown_events: List[int], keys) -> GameState:
    screen.fill(BLACK)
    title = get_font(72).render("Victory!", True, GOLDEN)
    story1 = get_font(40).render("Ahaan assembles his Nintendo Switch and runs away!", True, WHITE)
    story2 = get_font(40).render("'Freedom at last!' he shouts with joy!", True, WHITE)
    story3 = get_font(32).render("Press SPACE for final congratulations!", True, YELLOW)

    # Ahaan running with Switch
    pygame.draw.ellipse(screen, SKIN, (250, 250, 40, 50))
    pygame.draw.rect(screen, BLUE, (245, 300, 50, 60))
    pygame.draw.rect(screen, SKIN, (235, 350, 20, 40))
    pygame.draw.rect(screen, SKIN, (275, 350, 20, 40))
    pygame.draw.rect(screen, BLACK, (320, 320, 60, 40))
    pygame.draw.rect(screen, BLUE, (315, 325, 15, 30))
    pygame.draw.rect(screen, RED, (385, 325, 15, 30))
    for i in range(5):
        pygame.draw.line(screen, WHITE, (200 - i * 10, 280 + i * 5), (230 - i * 10, 285 + i * 5), 2)

    screen.blit(title, ((WIDTH - title.get_width()) // 2, HEIGHT // 2 - 150))
    screen.blit(story1, ((WIDTH - story1.get_width()) // 2, HEIGHT // 2 + 100))
    screen.blit(story2, ((WIDTH - story2.get_width()) // 2, HEIGHT // 2 + 140))
    screen.blit(story3, ((WIDTH - story3.get_width()) // 2, HEIGHT // 2 + 180))

    if keys[ctx.controls["jump"]]:
        return GameState.CONGRATULATIONS
    return GameState.VICTORY_CUTSCENE


def handle_congratulations(ctx: "GameContext", screen: pygame.Surface,
                            keydown_events: List[int], keys) -> GameState:
    screen.fill(BLACK)
    ctx.cutscene_timer += 1
    ct = ctx.cutscene_timer * 0.05

    title_str = "Congratulations!"
    title_font = get_font(96)
    for i, letter in enumerate(title_str):
        r = int(128 + 127 * math.sin(ct + i * 0.5))
        g = int(128 + 127 * math.sin(ct + i * 0.5 + 2))
        b = int(128 + 127 * math.sin(ct + i * 0.5 + 4))
        bounce = int(10 * math.sin(ct * 2 + i * 0.3))
        surf = title_font.render(letter, True, (r, g, b))
        lx = (WIDTH - len(title_str) * 45) // 2 + i * 55
        ly = HEIGHT // 2 - 100 + bounce
        screen.blit(surf, (lx, ly))

    msg1 = get_font(48).render("Ahaan has his Nintendo Switch back!", True, WHITE)
    msg2 = get_font(36).render(f"Final Score: {ctx.score}", True, GOLDEN)
    msg3 = get_font(36).render(f"High Score: {ctx.high_score}", True, GOLDEN)
    msg4 = get_font(32).render("Thanks for playing Super Ahaanio!", True, YELLOW)
    msg5 = get_font(28).render("Press SPACE to return to main menu", True, WHITE)
    screen.blit(msg1, ((WIDTH - msg1.get_width()) // 2, HEIGHT // 2))
    screen.blit(msg2, ((WIDTH - msg2.get_width()) // 2, HEIGHT // 2 + 50))
    screen.blit(msg3, ((WIDTH - msg3.get_width()) // 2, HEIGHT // 2 + 90))
    screen.blit(msg4, ((WIDTH - msg4.get_width()) // 2, HEIGHT // 2 + 140))
    screen.blit(msg5, ((WIDTH - msg5.get_width()) // 2, HEIGHT // 2 + 190))

    for i in range(10):
        fx = (i * 80 + int(50 * math.sin(ct + i))) % WIDTH
        fy = (i * 40 + int(30 * math.cos(ct * 1.5 + i))) % (HEIGHT // 2) + 50
        fc = ((i * 50) % 255, (i * 100) % 255, (i * 150) % 255)
        pygame.draw.circle(screen, fc, (fx, fy), 3)

    if keys[ctx.controls["jump"]]:
        _reset_to_start(ctx)
        return GameState.START
    return GameState.CONGRATULATIONS


def _reset_to_start(ctx: "GameContext") -> None:
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
    ctx.cutscene_timer = 0
