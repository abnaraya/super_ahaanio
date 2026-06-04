import math
import pygame
from game.constants import (
    WIDTH, HEIGHT, WHITE, BLACK, RED, SKIN, BLUE, BROWN, GREEN,
    YELLOW, GOLDEN,
)

_font_cache = {}


def get_font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size]


_BACKGROUND_CACHE = {}


def build_gradient_surface(top_color, bottom_color):
    key = (top_color, bottom_color, WIDTH, HEIGHT)
    if key in _BACKGROUND_CACHE:
        return _BACKGROUND_CACHE[key]
    surface = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT - 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
    _BACKGROUND_CACHE[key] = surface
    return surface


def draw_ahaan(surf, x, y, expression="happy", hair_flow=0, scale=1.0):
    s = scale
    pygame.draw.ellipse(surf, SKIN, (x, y, int(40 * s), int(50 * s)))
    pygame.draw.ellipse(surf, (240, 200, 160), (x + int(2 * s), y + int(2 * s), int(36 * s), int(46 * s)))

    pygame.draw.ellipse(surf, BROWN, (x - int(5 * s) + hair_flow, y - int(5 * s), int(50 * s), int(25 * s)))
    pygame.draw.circle(surf, (120, 80, 40), (x + int(10 * s) + hair_flow // 2, y), int(8 * s))
    pygame.draw.circle(surf, (120, 80, 40), (x + int(30 * s) + hair_flow // 3, y + int(2 * s)), int(8 * s))

    pygame.draw.ellipse(surf, WHITE, (x + int(8 * s), y + int(15 * s), int(8 * s), int(10 * s)))
    pygame.draw.ellipse(surf, WHITE, (x + int(24 * s), y + int(15 * s), int(8 * s), int(10 * s)))
    pygame.draw.circle(surf, BLACK, (x + int(11 * s), y + int(19 * s)), int(3 * s))
    pygame.draw.circle(surf, BLACK, (x + int(27 * s), y + int(19 * s)), int(3 * s))
    pygame.draw.circle(surf, WHITE, (x + int(12 * s), y + int(18 * s)), max(1, int(1 * s)))
    pygame.draw.circle(surf, WHITE, (x + int(28 * s), y + int(18 * s)), max(1, int(1 * s)))

    if expression == "scared":
        pygame.draw.circle(surf, BLACK, (x + int(10 * s), y + int(15 * s)), int(4 * s))
        pygame.draw.circle(surf, BLACK, (x + int(30 * s), y + int(15 * s)), int(4 * s))
        pygame.draw.ellipse(surf, BLACK, (x + int(15 * s), y + int(30 * s), int(10 * s), int(8 * s)))
    elif expression == "determined":
        pygame.draw.line(surf, (200, 160, 120),
                         (x + int(4 * s), y + int(12 * s)),
                         (x + int(10 * s), y + int(14 * s)), 2)
        pygame.draw.line(surf, (200, 160, 120),
                         (x + int(28 * s), y + int(14 * s)),
                         (x + int(34 * s), y + int(12 * s)), 2)
        pygame.draw.ellipse(surf, BLACK, (x + int(12 * s), y + int(28 * s), int(8 * s), int(6 * s)))
    elif expression == "confident":
        pygame.draw.arc(surf, BLACK,
                        (x + int(10 * s), y + int(28 * s), int(20 * s), int(15 * s)),
                        0, math.pi, int(3 * s))
    else:
        pygame.draw.arc(surf, BLACK,
                        (x + int(12 * s), y + int(28 * s), int(16 * s), int(8 * s)),
                        0, math.pi, 2)


def draw_ahaan_body(surf, x, y, color=BLUE, scale=1.0):
    s = scale
    pygame.draw.rect(surf, color, (x - int(10 * s), y + int(50 * s), int(60 * s), int(70 * s)))
    pygame.draw.rect(surf, SKIN, (x - int(15 * s), y + int(60 * s), int(20 * s), int(35 * s)))
    pygame.draw.rect(surf, SKIN, (x + int(35 * s), y + int(60 * s), int(20 * s), int(35 * s)))
    pygame.draw.rect(surf, color, (x + int(5 * s), y + int(110 * s), int(15 * s), int(40 * s)))
    pygame.draw.rect(surf, color, (x + int(20 * s), y + int(110 * s), int(15 * s), int(40 * s)))


def draw_mom(surf, x, y, expression="angry", scale=1.0):
    s = scale
    pygame.draw.ellipse(surf, SKIN, (x, y, int(50 * s), int(60 * s)))
    pygame.draw.rect(surf, (200, 100, 100), (x - int(10 * s), y + int(60 * s), int(70 * s), int(90 * s)))
    pygame.draw.rect(surf, SKIN, (x - int(15 * s), y + int(130 * s), int(30 * s), int(50 * s)))
    pygame.draw.rect(surf, SKIN, (x + int(55 * s), y + int(130 * s), int(30 * s), int(50 * s)))

    if expression == "angry":
        pygame.draw.line(surf, BLACK,
                         (x + int(15 * s), y + int(20 * s)),
                         (x + int(20 * s), y + int(25 * s)), 3)
        pygame.draw.line(surf, BLACK,
                         (x + int(35 * s), y + int(25 * s)),
                         (x + int(40 * s), y + int(20 * s)), 3)
        pygame.draw.circle(surf, BLACK, (x + int(18 * s), y + int(30 * s)), int(3 * s))
        pygame.draw.circle(surf, BLACK, (x + int(37 * s), y + int(30 * s)), int(3 * s))
        pygame.draw.arc(surf, BLACK,
                        (x + int(15 * s), y + int(40 * s), int(20 * s), int(10 * s)),
                        math.pi, 2 * math.pi, 3)


def draw_switch(surf, x, y, scale=1.0):
    s = scale
    sw, sh = int(60 * s), int(35 * s)
    pygame.draw.rect(surf, BLACK, (x, y, sw, sh))
    pygame.draw.rect(surf, (100, 120, 140), (x + int(3 * s), y + int(3 * s), sw - int(6 * s), sh - int(6 * s)))
    lw = int(12 * s)
    pygame.draw.rect(surf, BLUE, (x - lw, y + int(2 * s), lw, sh - int(4 * s)))
    pygame.draw.rect(surf, RED, (x + sw, y + int(2 * s), lw, sh - int(4 * s)))


def draw_switch_part(surf, x, y, part_type, glow=False, glow_color=None):
    if glow and glow_color:
        for radius in range(40, 15, -5):
            pygame.draw.circle(surf, glow_color, (x + 15, y + 50), radius, 2)

    if part_type == "left":
        pygame.draw.rect(surf, BLUE, (x, y, 30, 100))
        pygame.draw.rect(surf, (100, 150, 255), (x + 2, y + 2, 26, 96))
        pygame.draw.circle(surf, (50, 100, 200), (x + 15, y + 30), 8)
        pygame.draw.circle(surf, (80, 130, 255), (x + 15, y + 30), 6)
        pygame.draw.circle(surf, (200, 220, 255), (x + 15, y + 30), 3)
        pygame.draw.rect(surf, (80, 120, 255), (x + 8, y + 60, 14, 4))
        pygame.draw.rect(surf, (80, 120, 255), (x + 13, y + 55, 4, 14))
    elif part_type == "right":
        pygame.draw.rect(surf, RED, (x, y, 30, 100))
        pygame.draw.rect(surf, (255, 100, 100), (x + 2, y + 2, 26, 96))
        pygame.draw.circle(surf, (200, 50, 50), (x + 15, y + 30), 8)
        pygame.draw.circle(surf, (255, 80, 80), (x + 15, y + 30), 6)
        pygame.draw.circle(surf, (255, 200, 200), (x + 15, y + 30), 3)
        pygame.draw.circle(surf, YELLOW, (x + 8, y + 55), 3)
        pygame.draw.circle(surf, GREEN, (x + 22, y + 65), 3)
        pygame.draw.circle(surf, BLUE, (x + 22, y + 45), 3)
        pygame.draw.circle(surf, RED, (x + 8, y + 65), 3)
    elif part_type == "screen":
        pygame.draw.rect(surf, BLACK, (x, y, 80, 80))
        pygame.draw.rect(surf, (40, 40, 40), (x + 4, y + 4, 72, 72))
        pygame.draw.rect(surf, (100, 255, 100), (x + 8, y + 8, 64, 64))


def draw_victory_sparkles(surf, cx, cy, timer, count=8, radius=40, colors=None):
    if colors is None:
        colors = [YELLOW, WHITE]
    for i in range(count):
        angle = timer * 0.1 + i * (2 * math.pi / count)
        sx = cx + int(radius * math.cos(angle))
        sy = cy + int(radius * math.sin(angle))
        size = 2 + int(2 * math.sin(timer * 0.3 + i))
        for ci, c in enumerate(colors):
            pygame.draw.circle(surf, c, (sx - ci, sy - ci), max(1, size - ci))


def draw_energy_particles(surf, cx, cy, timer, count=12, radius=35, color=(100, 200, 255)):
    for i in range(count):
        angle = timer * 0.08 + i * (2 * math.pi / count)
        r = radius + int(10 * math.sin(timer * 0.1 + i))
        px = cx + int(r * math.cos(angle))
        py = cy + int(r * math.sin(angle))
        size = 1 + int(2 * math.sin(timer * 0.2 + i))
        pygame.draw.circle(surf, color, (px, py), size)
