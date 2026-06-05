"""STORY screen — animated cutscene intro."""
from __future__ import annotations

import math
from typing import TYPE_CHECKING, List

import pygame

from game.constants import (
    BLACK, BLUE, BROWN, GOLDEN, GREEN, RED, SKIN, WHITE, YELLOW, WIDTH, HEIGHT,
)
from game.renderer import get_font
from game.states import GameState
from game.level_manager import load_normal_level, apply_player_profile, reset_checkpoint, reset_camera

if TYPE_CHECKING:
    from game.context import GameContext


def handle(ctx: "GameContext", screen: pygame.Surface,
           keydown_events: List[int], keys) -> GameState:
    ctx.cutscene_timer += 1
    current_cutscene = ctx.cutscene_segments[ctx.story_page]

    screen.fill((20, 20, 40))
    _draw_stars(screen, ctx.cutscene_timer)
    _render_cutscene(screen, current_cutscene, ctx.cutscene_timer)

    controls_prompt = get_font(24).render("SPACE: Next | S: Skip Story", True, WHITE)
    screen.blit(controls_prompt, (10, HEIGHT - 30))

    # Advance / skip
    if keys[ctx.controls["jump"]]:
        if not ctx.input_state["story_last_space"]:
            if ctx.story_page < len(ctx.cutscene_segments) - 1:
                ctx.story_page += 1
                ctx.cutscene_timer = 0
            else:
                _start_game(ctx)
                return GameState.PLAY
        ctx.input_state["story_last_space"] = True
    else:
        ctx.input_state["story_last_space"] = False

    if keys[pygame.K_s]:
        _start_game(ctx)
        return GameState.PLAY

    return GameState.STORY


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _start_game(ctx: "GameContext") -> None:
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


def _draw_stars(screen, timer):
    for i in range(20):
        star_x = (i * 137 + timer) % WIDTH
        star_y = (i * 89 + timer // 2) % HEIGHT
        brightness = int(128 + 127 * math.sin(timer * 0.05 + i))
        pygame.draw.circle(screen, (brightness, brightness, 255), (star_x, star_y), 2)


def _render_cutscene(screen, name: str, t: int):
    """Dispatch to per-cutscene renderers."""
    _RENDERERS.get(name, lambda s, ti: None)(screen, t)


# ---------------------------------------------------------------------------
# Individual cutscene renderers
# ---------------------------------------------------------------------------

def _cutscene_intro_world(screen, t):
    title = get_font(72).render("Super Ahaanio", True, GOLDEN)
    subtitle = get_font(48).render("The Adventure Begins", True, YELLOW)
    bounce = int(10 * math.sin(t * 0.1))
    for i in range(3):
        plat_x = 100 + i * 250 + int(20 * math.sin(t * 0.05 + i))
        plat_y = 400 + bounce + i * 20
        pygame.draw.rect(screen, BLUE, (plat_x, plat_y, 80, 20))
        pygame.draw.rect(screen, (100, 150, 255), (plat_x + 2, plat_y + 2, 76, 16))
    ahaan_x = 200 + int(30 * math.sin(t * 0.08))
    ahaan_y = 350 + bounce
    pygame.draw.ellipse(screen, SKIN, (ahaan_x, ahaan_y, 30, 40))
    pygame.draw.rect(screen, BLUE, (ahaan_x - 5, ahaan_y + 40, 40, 50))
    pygame.draw.rect(screen, SKIN, (ahaan_x, ahaan_y + 80, 15, 30))
    pygame.draw.rect(screen, SKIN, (ahaan_x + 20, ahaan_y + 80, 15, 30))
    screen.blit(title, ((WIDTH - title.get_width()) // 2, 100))
    screen.blit(subtitle, ((WIDTH - subtitle.get_width()) // 2, 180))
    text = get_font(36).render("In a world filled with adventure...", True, WHITE)
    screen.blit(text, ((WIDTH - text.get_width()) // 2, HEIGHT - 150))


def _cutscene_interests(screen, t):
    title = get_font(56).render("Meet Ahaan!", True, GOLDEN)
    screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
    cx, cy = WIDTH // 2, 220
    # Head
    pygame.draw.ellipse(screen, SKIN, (cx - 20, 150, 40, 50))
    pygame.draw.ellipse(screen, (240, 200, 160), (cx - 18, 152, 36, 46))
    pygame.draw.ellipse(screen, BROWN, (cx - 25, 145, 50, 25))
    # Eyes
    pygame.draw.ellipse(screen, WHITE, (cx - 12, 165, 8, 10))
    pygame.draw.ellipse(screen, WHITE, (cx + 4, 165, 8, 10))
    pygame.draw.circle(screen, BLACK, (cx - 8, 169), 3)
    pygame.draw.circle(screen, BLACK, (cx + 8, 169), 3)
    # Body
    pygame.draw.rect(screen, GREEN, (cx - 25, 200, 50, 60))
    # Gadgets orbiting
    gadgets = [("Nintendo Switch", BLUE, RED), ("PS5", BLACK, WHITE),
               ("Drums", (139, 69, 19), (160, 82, 45)), ("Apple Watch", BLACK, GREEN)]
    radius = 120
    for i, (name, c1, c2) in enumerate(gadgets):
        angle = t * 0.02 + i * (math.pi / 2)
        gx = cx + int(radius * math.cos(angle))
        gy = cy + int(radius * math.sin(angle))
        pygame.draw.circle(screen, YELLOW, (gx, gy), 8)
    text1 = get_font(32).render("He LOVES gadgets and music!", True, WHITE)
    text2 = get_font(28).render("Nintendo Switch • PS5 • Drums • Apple Watch", True, YELLOW)
    screen.blit(text1, ((WIDTH - text1.get_width()) // 2, HEIGHT - 120))
    screen.blit(text2, ((WIDTH - text2.get_width()) // 2, HEIGHT - 80))


def _cutscene_sports(screen, t):
    title = get_font(48).render("Ahaan the Athlete!", True, GOLDEN)
    screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
    sy = 200
    bo = t * 0.1
    # Soccer ball
    bx = 100 + int(20 * math.sin(bo))
    pygame.draw.circle(screen, WHITE, (bx, sy), 25)
    pygame.draw.circle(screen, BLACK, (bx, sy), 25, 3)
    # Basketball
    bx = 300 + int(15 * math.sin(bo + 1))
    pygame.draw.circle(screen, (255, 140, 0), (bx, sy), 25)
    pygame.draw.line(screen, BLACK, (bx - 20, sy), (bx + 20, sy), 3)
    text1 = get_font(32).render("He's an energetic sportsman!", True, WHITE)
    text2 = get_font(28).render("Soccer • Basketball • Swimming • Skateboarding", True, YELLOW)
    screen.blit(text1, ((WIDTH - text1.get_width()) // 2, HEIGHT - 120))
    screen.blit(text2, ((WIDTH - text2.get_width()) // 2, HEIGHT - 80))


def _cutscene_challenges(screen, t):
    title = get_font(48).render("But Ahaan faces challenges...", True, RED)
    screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
    # Storm clouds
    for i in range(0, WIDTH, 50):
        cy = 80 + int(15 * math.sin(t * 0.05 + i * 0.01))
        pygame.draw.ellipse(screen, (60, 60, 80), (i, cy, 60, 30))
    text1 = get_font(32).render("Homework, chores, forced badminton, showers...", True, WHITE)
    text2 = get_font(28).render("Parents yelling like villains!", True, RED)
    screen.blit(text1, ((WIDTH - text1.get_width()) // 2, HEIGHT - 120))
    screen.blit(text2, ((WIDTH - text2.get_width()) // 2, HEIGHT - 80))


def _cutscene_switch_gaming(screen, t):
    title = get_font(48).render("One peaceful day...", True, GREEN)
    screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
    # Simple room background
    pygame.draw.rect(screen, (140, 120, 100), (50, 150, WIDTH - 100, HEIGHT - 200))
    # Ahaan gaming
    ax, ay = WIDTH // 2 - 20, 250
    pygame.draw.ellipse(screen, SKIN, (ax, ay, 40, 50))
    pygame.draw.rect(screen, BLUE, (ax - 10, ay + 50, 60, 70))
    # Switch
    pygame.draw.rect(screen, BLACK, (ax + 10, ay + 75, 40, 25))
    pygame.draw.rect(screen, BLUE, (ax - 2, ay + 76, 14, 23))
    pygame.draw.rect(screen, RED, (ax + 48, ay + 76, 14, 23))
    text1 = get_font(36).render("Ahaan was gaming on his Nintendo Switch", True, WHITE)
    text2 = get_font(32).render("Peaceful and happy...", True, GREEN)
    screen.blit(text1, ((WIDTH - text1.get_width()) // 2, HEIGHT - 120))
    screen.blit(text2, ((WIDTH - text2.get_width()) // 2, HEIGHT - 80))


def _cutscene_mom_appears(screen, t):
    title = get_font(48).render("Suddenly...", True, RED)
    screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
    pygame.draw.rect(screen, (100, 80, 60), (50, 150, WIDTH - 100, HEIGHT - 200))
    ax, ay = WIDTH // 2 - 20, 250
    pygame.draw.ellipse(screen, SKIN, (ax, ay, 40, 50))
    pygame.draw.rect(screen, BLUE, (ax - 10, ay + 50, 60, 70))
    pygame.draw.circle(screen, BLACK, (ax + 10, ay + 15), 4)
    pygame.draw.circle(screen, BLACK, (ax + 30, ay + 15), 4)
    pygame.draw.ellipse(screen, BLACK, (ax + 15, ay + 30, 10, 8))
    progress = min(t / 60.0, 1.0)
    mx = int(100 - 50 + progress * 50)
    my = 200
    pygame.draw.ellipse(screen, SKIN, (mx, my, 50, 60))
    pygame.draw.rect(screen, (200, 100, 100), (mx - 10, my + 60, 70, 90))
    if t > 60:
        bx, by = mx + 60, my - 20
        pygame.draw.ellipse(screen, WHITE, (bx, by, 200, 60))
        pygame.draw.ellipse(screen, BLACK, (bx, by, 200, 60), 3)
        text = get_font(28).render("No more games!", True, RED)
        text2 = get_font(24).render("You have homework!", True, BLACK)
        screen.blit(text, (bx + 10, by + 10))
        screen.blit(text2, (bx + 10, by + 35))
    instruction = get_font(32).render("Mom suddenly appears!", True, WHITE)
    screen.blit(instruction, ((WIDTH - instruction.get_width()) // 2, HEIGHT - 100))


def _cutscene_switch_breaks(screen, t):
    title = get_font(48).render("OH NO!", True, RED)
    screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
    prog = t / 120.0
    cx, cy = WIDTH // 2, HEIGHT // 2
    lx = cx - int(150 * prog) - 50
    ly = cy - int(100 * prog)
    pygame.draw.rect(screen, BLUE, (lx, ly, 25, 40))
    sx = cx - 30
    sy = cy - int(80 * prog)
    pygame.draw.rect(screen, BLACK, (sx, sy, 60, 35))
    rx = cx + int(150 * prog) + 25
    ry = cy - int(120 * prog)
    pygame.draw.rect(screen, RED, (rx, ry, 25, 40))
    text1 = get_font(36).render("The Nintendo Switch breaks apart!", True, WHITE)
    text2 = get_font(32).render("Three pieces scattered!", True, RED)
    screen.blit(text1, ((WIDTH - text1.get_width()) // 2, HEIGHT - 120))
    screen.blit(text2, ((WIDTH - text2.get_width()) // 2, HEIGHT - 80))


def _cutscene_chase_begins(screen, t):
    title = get_font(48).render("The Chase is On!", True, GOLDEN)
    screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
    ax = 100 + int(t * 1.5)
    ay = 250
    pygame.draw.ellipse(screen, SKIN, (ax, ay, 35, 45))
    pygame.draw.rect(screen, BLUE, (ax - 5, ay + 45, 45, 60))
    for i in range(5):
        pygame.draw.line(screen, WHITE, (ax - 20 - i * 10, ay + 60), (ax - 5 - i * 10, ay + 65), 2)
    text1 = get_font(36).render("Ahaan must collect all three pieces!", True, WHITE)
    text2 = get_font(32).render("Defeat mom bosses to get them back!", True, YELLOW)
    screen.blit(text1, ((WIDTH - text1.get_width()) // 2, HEIGHT - 120))
    screen.blit(text2, ((WIDTH - text2.get_width()) // 2, HEIGHT - 80))


def _cutscene_ready(screen, t):
    title = get_font(56).render("Are You Ready?", True, GOLDEN)
    screen.blit(title, ((WIDTH - title.get_width()) // 2, 100))
    ax, ay = WIDTH // 2 - 25, 200
    aura = 80 + int(20 * math.sin(t * 0.1))
    for r in range(aura, aura - 30, -5):
        pygame.draw.circle(screen, (255, 215, 0), (ax + 25, ay + 100), r, 2)
    pygame.draw.ellipse(screen, SKIN, (ax, ay, 50, 60))
    pygame.draw.rect(screen, BLUE, (ax - 10, ay + 60, 70, 80))
    for i in range(3):
        angle = t * 0.05 + i * (2 * math.pi / 3)
        ox = ax + 25 + int(60 * math.cos(angle))
        oy = ay + 100 + int(40 * math.sin(angle))
        colors = [BLUE, BLACK, RED]
        pygame.draw.rect(screen, colors[i], (ox, oy, 20, 30))
    subtitle = get_font(40).render("Help Ahaan get his Nintendo Switch back!", True, WHITE)
    inst1 = get_font(32).render("Press SPACE to begin the adventure!", True, YELLOW)
    inst2 = get_font(24).render("(Press S to skip story)", True, (150, 150, 150))
    screen.blit(subtitle, ((WIDTH - subtitle.get_width()) // 2, HEIGHT - 150))
    screen.blit(inst1, ((WIDTH - inst1.get_width()) // 2, HEIGHT - 100))
    screen.blit(inst2, ((WIDTH - inst2.get_width()) // 2, HEIGHT - 60))


_RENDERERS = {
    "INTRO_WORLD": _cutscene_intro_world,
    "INTRO_AHAAN_INTERESTS": _cutscene_interests,
    "INTRO_AHAAN_SPORTS": _cutscene_sports,
    "INTRO_CHALLENGES": _cutscene_challenges,
    "SWITCH_GAMING": _cutscene_switch_gaming,
    "MOM_APPEARS": _cutscene_mom_appears,
    "SWITCH_BREAKS": _cutscene_switch_breaks,
    "CHASE_BEGINS": _cutscene_chase_begins,
    "READY_TO_PLAY": _cutscene_ready,
}
