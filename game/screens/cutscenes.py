"""Nintendo Switch part-retrieval cutscenes (CUTSCENE_LEFT_CONTROLLER, etc.)."""
from __future__ import annotations

import math
from typing import TYPE_CHECKING, List

import pygame

from game.constants import (
    BLACK, BLUE, BROWN, GOLDEN, GREEN, RED, SKIN, WHITE, YELLOW, WIDTH, HEIGHT,
)
from game.renderer import get_font
from game.states import GameState

if TYPE_CHECKING:
    from game.context import GameContext


def handle_left_controller(ctx: "GameContext", screen: pygame.Surface,
                            keydown_events: List[int], keys) -> GameState:
    ctx.cutscene_timer += 1
    t = ctx.cutscene_timer

    screen.fill((10, 10, 30))
    _floating_particles(screen, t, count=20, color_fn=lambda i: (100 + i * 5, 150 + i * 3, 255))

    # Title
    tp = min(t / 60.0, 1.0)
    ts = int(64 * tp)
    if ts > 0:
        title = get_font(ts).render("FIRST PART RETRIEVED!", True, BLUE)
        screen.blit(title, ((WIDTH - title.get_width()) // 2, HEIGHT // 2 - 150))

    # Ahaan celebrating
    if t > 30:
        _draw_ahaan_celebrate(screen, WIDTH // 2 - 100, HEIGHT // 2 - 50, t)

    # Left controller entrance
    if t > 60:
        ep = min((t - 60) / 60.0, 1.0)
        cx = int(WIDTH + (WIDTH // 2 + 50 - WIDTH) * ep)
        cy = HEIGHT // 2 - 20
        pygame.draw.rect(screen, BLUE, (cx, cy, 30, 100))
        pygame.draw.rect(screen, (100, 150, 255), (cx + 2, cy + 2, 26, 96))
        pygame.draw.circle(screen, (50, 100, 200), (cx + 15, cy + 30), 8)

    if t > 90:
        _typewriter(screen, "Ahaan defeats the first Mom boss and retrieves the Left Joy-Con!",
                    t, start=90, y=HEIGHT // 2 + 80)
    if t > 180:
        _typewriter(screen, "'One piece down, two to go!' Ahaan shouts with determination!",
                    t, start=180, y=HEIGHT // 2 + 110, color=YELLOW, size=28)

    if t > 240:
        prompt = get_font(32).render("Press SPACE to continue the adventure!", True, (150, 255, 150))
        screen.blit(prompt, ((WIDTH - prompt.get_width()) // 2, HEIGHT // 2 + 150))

    if keys[ctx.controls["jump"]] and t > 240:
        ctx.cutscene_timer = 0
        return GameState.COMPLETE
    return GameState.CUTSCENE_LEFT_CONTROLLER


def handle_right_controller(ctx: "GameContext", screen: pygame.Surface,
                             keydown_events: List[int], keys) -> GameState:
    ctx.cutscene_timer += 1
    t = ctx.cutscene_timer

    screen.fill((30, 10, 10))
    _floating_particles(screen, t, count=25, color_fn=lambda i: (255, 100 + i * 3, 100 + i * 2))

    tp = min(t / 45.0, 1.0)
    ts = int(72 * tp)
    if ts > 0:
        title = get_font(ts).render("SECOND PART SECURED!", True, RED)
        screen.blit(title, ((WIDTH - title.get_width()) // 2, HEIGHT // 2 - 160))

    if t > 25:
        _draw_ahaan_celebrate(screen, WIDTH // 2 - 120, HEIGHT // 2 - 60, t)

    if t > 50:
        ep = min((t - 50) / 45.0, 1.0)
        cx = int(WIDTH + 100 + (WIDTH // 2 + 80 - WIDTH - 100) * ep)
        cy = HEIGHT // 2 - 30
        pygame.draw.rect(screen, RED, (cx, cy, 30, 100))
        pygame.draw.rect(screen, (255, 100, 100), (cx + 2, cy + 2, 26, 96))
        pygame.draw.circle(screen, (200, 50, 50), (cx + 15, cy + 30), 8)

    if t > 80:
        _typewriter(screen, "Ahaan conquers the second Mom boss and claims the Right Joy-Con!",
                    t, start=80, y=HEIGHT // 2 + 90)
    if t > 160:
        _typewriter(screen, "'Just the screen left!' he declares with unwavering confidence!",
                    t, start=160, y=HEIGHT // 2 + 120, color=YELLOW, size=26)

    if t > 220:
        pi = int(200 + 55 * math.sin(t * 0.25))
        prompt = get_font(32).render("Press SPACE for the final showdown!", True, (255, pi, pi))
        screen.blit(prompt, ((WIDTH - prompt.get_width()) // 2, HEIGHT // 2 + 160))

    if keys[ctx.controls["jump"]] and t > 220:
        ctx.cutscene_timer = 0
        return GameState.COMPLETE
    return GameState.CUTSCENE_RIGHT_CONTROLLER


def handle_screen_piece(ctx: "GameContext", screen: pygame.Surface,
                         keydown_events: List[int], keys) -> GameState:
    ctx.cutscene_timer += 1
    t = ctx.cutscene_timer

    if ctx.switch_parts_count >= 3:
        # Final victory cutscene
        _draw_final_cutscene(screen, t)
        state_after = GameState.VICTORY_CUTSCENE
        min_timer = 200
    else:
        # Intermediate
        _draw_intermediate_cutscene(screen, t)
        state_after = GameState.COMPLETE
        min_timer = 200

    if keys[ctx.controls["jump"]] and t > min_timer:
        ctx.cutscene_timer = 0
        return state_after
    return GameState.CUTSCENE_SCREEN


# ---------------------------------------------------------------------------
# Shared drawing helpers
# ---------------------------------------------------------------------------

def _floating_particles(screen, t, count=20, color_fn=None):
    for i in range(count):
        px = (i * 47 + t * 2) % WIDTH
        py = 50 + int(30 * math.sin(t * 0.03 + i))
        color = color_fn(i) if color_fn else (200, 200, 255)
        pygame.draw.circle(screen, color, (px, py), 2)


def _typewriter(screen, text, t, start, y, color=WHITE, size=32):
    progress = min((t - start) / 3.0, 1.0)
    visible = text[:int(len(text) * progress)]
    surf = get_font(size).render(visible, True, color)
    screen.blit(surf, ((WIDTH - surf.get_width()) // 2, y))


def _draw_ahaan_celebrate(screen, ax, ay, t):
    pygame.draw.ellipse(screen, SKIN, (ax, ay, 40, 50))
    hf = int(5 * math.sin(t * 0.2))
    pygame.draw.ellipse(screen, BROWN, (ax - 5 + hf, ay - 5, 50, 25))
    pygame.draw.ellipse(screen, WHITE, (ax + 8, ay + 15, 8, 10))
    pygame.draw.ellipse(screen, WHITE, (ax + 24, ay + 15, 8, 10))
    pygame.draw.circle(screen, BLACK, (ax + 11, ay + 19), 3)
    pygame.draw.circle(screen, BLACK, (ax + 27, ay + 19), 3)
    pygame.draw.arc(screen, BLACK, (ax + 10, ay + 28, 20, 15), 0, math.pi, 3)
    pygame.draw.rect(screen, BLUE, (ax - 10, ay + 50, 60, 70))
    # Raised fist
    pygame.draw.rect(screen, SKIN, (ax - 25, ay + 40, 20, 40))
    pygame.draw.ellipse(screen, SKIN, (ax - 20, ay + 30, 10, 12))
    # Sparkles
    for sp in range(8):
        sa = t * 0.1 + sp * (2 * math.pi / 8)
        sx = ax + 20 + int(40 * math.cos(sa))
        sy = ay + 75 + int(30 * math.sin(sa))
        ss = 2 + int(2 * math.sin(t * 0.3 + sp))
        pygame.draw.circle(screen, YELLOW, (sx, sy), ss)


def _draw_final_cutscene(screen, t):
    screen.fill((10, 30, 10))
    _floating_particles(screen, t, count=30, color_fn=lambda i: (100 + i * 3, 255, 100 + i * 2))
    tp = min(t / 30.0, 1.0)
    ts = int(96 * tp)
    if ts > 0:
        title = get_font(ts).render("NINTENDO SWITCH COMPLETE!", True, GREEN)
        screen.blit(title, ((WIDTH - title.get_width()) // 2, HEIGHT // 2 - 200))
    if t > 70:
        _typewriter(screen, "Ahaan defeats the final Mom boss and claims the screen!",
                    t, start=70, y=HEIGHT // 2 + 120)
    if t > 140:
        _typewriter(screen, "He quickly assembles his Nintendo Switch - VICTORY IS HIS!",
                    t, start=140, y=HEIGHT // 2 + 150, color=GOLDEN, size=28)
    if t > 200:
        pi = int(200 + 55 * math.sin(t * 0.3))
        prompt = get_font(36).render("Press SPACE to see the grand finale!", True, (pi, 255, pi))
        screen.blit(prompt, ((WIDTH - prompt.get_width()) // 2, HEIGHT // 2 + 190))


def _draw_intermediate_cutscene(screen, t):
    screen.fill((20, 10, 30))
    _floating_particles(screen, t, count=20, color_fn=lambda i: (150 + i * 2, 255, 150 + i * 3))
    tp = min(t / 40.0, 1.0)
    ts = int(68 * tp)
    if ts > 0:
        title = get_font(ts).render("FINAL PIECE OBTAINED!", True, GREEN)
        screen.blit(title, ((WIDTH - title.get_width()) // 2, HEIGHT // 2 - 140))
    if t > 80:
        _typewriter(screen, "Ahaan retrieves the final piece - the Nintendo Switch screen!",
                    t, start=80, y=HEIGHT // 2 + 100)
    if t > 150:
        _typewriter(screen, "But something feels different... more challenges await!",
                    t, start=150, y=HEIGHT // 2 + 130, color=(255, 200, 100), size=26)
    if t > 200:
        pi = int(150 + 105 * math.sin(t * 0.2))
        prompt = get_font(32).render("Press SPACE to continue the adventure!", True, (pi, 255, pi))
        screen.blit(prompt, ((WIDTH - prompt.get_width()) // 2, HEIGHT // 2 + 170))
