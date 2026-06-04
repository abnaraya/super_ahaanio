import math
import random
import pygame
from game.constants import (
    WHITE, BLACK, RED, SKIN, BLUE, BROWN, GREEN, PIPE_GREEN,
    YELLOW, GOLDEN, FLAGPOLE, WIDTH, HEIGHT, LEVEL_END_X,
)


class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, surf, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y
        w = self.rect.w
        h = self.rect.h

        pygame.draw.rect(surf, (0, 100, 180), (x + 8, y, w - 16, h), border_radius=9)

        brick_width = 24
        brick_height = 8
        for row in range(0, h, brick_height):
            for col in range(0, w - 16, brick_width):
                offset = (brick_width // 2) if (row // brick_height) % 2 else 0
                brick_x = x + 8 + col + offset
                brick_y = y + row

                if brick_x + brick_width <= x + w - 8:
                    pygame.draw.rect(surf, BLUE, (brick_x, brick_y, brick_width - 2, brick_height - 1))
                    pygame.draw.line(surf, (100, 150, 255), (brick_x, brick_y), (brick_x + brick_width - 2, brick_y))
                    pygame.draw.line(surf, (100, 150, 255), (brick_x, brick_y), (brick_x, brick_y + brick_height - 1))
                    pygame.draw.line(surf, (0, 80, 160), (brick_x + brick_width - 2, brick_y), (brick_x + brick_width - 2, brick_y + brick_height - 1))
                    pygame.draw.line(surf, (0, 80, 160), (brick_x, brick_y + brick_height - 1), (brick_x + brick_width - 2, brick_y + brick_height - 1))

        pygame.draw.ellipse(surf, BLUE, (x, y, 16, h))
        pygame.draw.ellipse(surf, (100, 150, 255), (x + 2, y + 1, 12, h - 2))
        pygame.draw.ellipse(surf, BLUE, (x + w - 16, y, 16, h))
        pygame.draw.ellipse(surf, (0, 80, 160), (x + w - 14, y + 1, 12, h - 2))


class MovingPlatform(Platform):
    def __init__(self, x, y, w, h, move_type="horizontal", distance=100, speed=2):
        super().__init__(x, y, w, h)
        self.start_x = x
        self.start_y = y
        self.move_type = move_type
        self.distance = distance
        self.speed = speed
        self.direction = 1
        self.angle = 0

    def update(self):
        if self.move_type == "horizontal":
            self.rect.x += self.speed * self.direction
            if self.rect.x >= self.start_x + self.distance:
                self.direction = -1
                self.rect.x = self.start_x + self.distance
            elif self.rect.x <= self.start_x:
                self.direction = 1
                self.rect.x = self.start_x
        elif self.move_type == "vertical":
            self.rect.y += self.speed * self.direction
            if self.rect.y >= self.start_y + self.distance:
                self.direction = -1
                self.rect.y = self.start_y + self.distance
            elif self.rect.y <= self.start_y:
                self.direction = 1
                self.rect.y = self.start_y
        elif self.move_type == "circular":
            self.angle += self.speed * 0.05
            radius = self.distance // 2
            center_x = self.start_x + radius
            center_y = self.start_y + radius
            self.rect.x = int(center_x + radius * math.cos(self.angle))
            self.rect.y = int(center_y + radius * math.sin(self.angle))

    def draw(self, surf, camera_x):
        super().draw(surf, camera_x)
        x = self.rect.x - camera_x
        y = self.rect.y
        w = self.rect.w
        h = self.rect.h

        if self.move_type == "horizontal":
            pygame.draw.polygon(surf, YELLOW, [
                (x + w // 2 - 8, y - 8), (x + w // 2 - 2, y - 5), (x + w // 2 - 8, y - 2)])
            pygame.draw.polygon(surf, YELLOW, [
                (x + w // 2 + 8, y - 8), (x + w // 2 + 2, y - 5), (x + w // 2 + 8, y - 2)])
        elif self.move_type == "vertical":
            pygame.draw.polygon(surf, YELLOW, [
                (x + w // 2 - 3, y - 8), (x + w // 2, y - 2), (x + w // 2 + 3, y - 8)])
            pygame.draw.polygon(surf, YELLOW, [
                (x + w // 2 - 3, y + h + 2), (x + w // 2, y + h + 8), (x + w // 2 + 3, y + h + 2)])
        elif self.move_type == "circular":
            pygame.draw.circle(surf, YELLOW, (x + w // 2, y - 6), 3)
            pygame.draw.circle(surf, YELLOW, (x + w // 2, y - 6), 6, 2)


class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.rotation = 0

    def draw(self, surf, camera_x):
        self.rotation += 3
        x = self.rect.x + 10 - camera_x
        y = self.rect.y + 10
        spin_width = int(10 * abs(math.cos(self.rotation * 0.1)))

        pygame.draw.ellipse(surf, (180, 150, 30), (x - 11, y - 9, spin_width + 2, 18))
        pygame.draw.ellipse(surf, GOLDEN, (x - 10, y - 10, spin_width, 20))
        if spin_width > 3:
            pygame.draw.ellipse(surf, (255, 240, 100), (x - 8, y - 8, max(1, spin_width - 4), 16))
        if spin_width > 6:
            star_points = []
            for i in range(5):
                angle = i * 2 * math.pi / 5 - math.pi / 2
                star_x = x + 3 * math.cos(angle)
                star_y = y + 3 * math.sin(angle)
                star_points.append((star_x, star_y))
            if len(star_points) >= 3:
                pygame.draw.polygon(surf, (200, 160, 20), star_points)


class Pipe:
    def __init__(self, x, y, width=50, height=70, is_warp_pipe=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_warp_pipe = is_warp_pipe
        self.warp_timer = 0

    def draw(self, surf, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y
        w = self.rect.w
        h = self.rect.h

        base_color = PIPE_GREEN
        highlight_color = (40, 180, 80)
        shadow_color = (0, 100, 40)

        if self.is_warp_pipe:
            glow_intensity = int(50 + 30 * math.sin(self.warp_timer * 0.1))
            base_color = (0, 140 + glow_intensity // 2, 51 + glow_intensity // 3)
            highlight_color = (40 + glow_intensity // 3, 180 + glow_intensity // 4, 80 + glow_intensity // 3)
            shadow_color = (0, 100 + glow_intensity // 6, 40 + glow_intensity // 4)
            self.warp_timer += 1

        pygame.draw.rect(surf, base_color, (x, y + 15, w, h - 15))
        pygame.draw.rect(surf, highlight_color, (x, y + 15, 8, h - 15))
        pygame.draw.rect(surf, shadow_color, (x + w - 8, y + 15, 8, h - 15))
        pygame.draw.ellipse(surf, base_color, (x - 8, y, w + 16, 28))
        pygame.draw.ellipse(surf, highlight_color, (x - 6, y + 2, w + 12, 24), 3)
        pygame.draw.ellipse(surf, shadow_color, (x - 6, y + 4, w + 12, 20), 2)
        pygame.draw.rect(surf, highlight_color, (x + 9, y + 25, 8, h - 31))
        pygame.draw.rect(surf, shadow_color, (x + w - 17, y + 25, 8, h - 31))

        for i in range(y + 30, y + h - 10, 12):
            pygame.draw.line(surf, shadow_color, (x + 3, i), (x + w - 3, i), 1)
            pygame.draw.line(surf, highlight_color, (x + 3, i + 1), (x + w - 3, i + 1), 1)

        if self.is_warp_pipe:
            sparkle_colors = [YELLOW, WHITE, (255, 200, 255), (200, 255, 255)]
            for i in range(5):
                if random.randint(1, 8) == 1:
                    sparkle_x = x + random.randint(5, w - 5)
                    sparkle_y = y + random.randint(10, h - 10)
                    color = random.choice(sparkle_colors)
                    pygame.draw.circle(surf, color, (sparkle_x, sparkle_y), 3)
                    pygame.draw.circle(surf, WHITE, (sparkle_x, sparkle_y), 1)


class Flag:
    def __init__(self, x, y, height=140):
        self.rect = pygame.Rect(x, y - height, 15, height)

    def draw(self, surf, camera_x):
        pole = pygame.Rect(self.rect.x - camera_x, self.rect.y, 8, self.rect.h)
        pygame.draw.rect(surf, FLAGPOLE, pole)
        pygame.draw.circle(surf, YELLOW, (self.rect.x - camera_x + 4, self.rect.y), 8)
        pygame.draw.polygon(surf, YELLOW, [
            (self.rect.x - camera_x + 8, self.rect.y + 14),
            (self.rect.x - camera_x + 8 + 40, self.rect.y + 34),
            (self.rect.x - camera_x + 8, self.rect.y + 47)])


class PowerUp:
    def __init__(self, x, y, power_type):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.power_type = power_type
        self.collected = False
        self.float_timer = 0
        self.original_y = y

    def update(self):
        self.float_timer += 0.1
        self.rect.y = self.original_y + int(3 * pygame.math.Vector2(0, 1).rotate(self.float_timer * 10).y)

    def draw(self, surf, camera_x):
        if self.collected:
            return
        cx = self.rect.x - camera_x
        cy = self.rect.y

        if self.power_type == 'speed':
            pygame.draw.polygon(surf, (255, 206, 84), [
                (cx + 2, cy + 20), (cx + 23, cy + 20), (cx + 12, cy + 2)])
            pygame.draw.polygon(surf, (255, 255, 153), [
                (cx + 4, cy + 18), (cx + 21, cy + 18), (cx + 12, cy + 4)])
            pygame.draw.circle(surf, (139, 0, 0), (cx + 10, cy + 12), 2)
            pygame.draw.circle(surf, (139, 0, 0), (cx + 16, cy + 15), 2)
        elif self.power_type == 'jump':
            pygame.draw.circle(surf, (139, 69, 19), (cx + 12, cy + 12), 11)
            pygame.draw.circle(surf, (92, 192, 255), (cx + 12, cy + 12), 5)
            pygame.draw.circle(surf, (255, 182, 193), (cx + 12, cy + 12), 9, 2)
            pygame.draw.rect(surf, RED, (cx + 8, cy + 8, 2, 6))
            pygame.draw.rect(surf, GREEN, (cx + 15, cy + 10, 6, 2))
            pygame.draw.rect(surf, BLUE, (cx + 10, cy + 15, 2, 4))
        elif self.power_type == 'life':
            pygame.draw.ellipse(surf, RED, (cx + 2, cy + 8, 20, 10))
            pygame.draw.ellipse(surf, (255, 182, 193), (cx + 4, cy + 9, 16, 8))
            pygame.draw.polygon(surf, (255, 215, 0), [
                (cx + 2, cy + 8), (cx, cy + 5), (cx, cy + 12), (cx + 2, cy + 18)])
            pygame.draw.polygon(surf, (255, 215, 0), [
                (cx + 22, cy + 8), (cx + 24, cy + 5), (cx + 24, cy + 12), (cx + 22, cy + 18)])
        elif self.power_type == 'nintendo':
            pygame.draw.rect(surf, BLACK, (cx + 3, cy + 6, 18, 12))
            pygame.draw.rect(surf, (100, 100, 100), (cx + 5, cy + 8, 14, 8))
            pygame.draw.rect(surf, BLUE, (cx, cy + 8, 4, 8))
            pygame.draw.rect(surf, RED, (cx + 20, cy + 8, 4, 8))
        elif self.power_type == 'drums':
            pygame.draw.ellipse(surf, (139, 69, 19), (cx + 5, cy + 10, 15, 10))
            pygame.draw.ellipse(surf, (160, 82, 45), (cx + 6, cy + 11, 13, 8))
            pygame.draw.line(surf, BROWN, (cx + 8, cy + 5), (cx + 10, cy + 12), 2)
            pygame.draw.line(surf, BROWN, (cx + 14, cy + 5), (cx + 16, cy + 12), 2)
        elif self.power_type == 'soccer':
            pygame.draw.circle(surf, WHITE, (cx + 12, cy + 12), 10)
            pygame.draw.circle(surf, BLACK, (cx + 12, cy + 12), 10, 2)
            pygame.draw.polygon(surf, BLACK, [
                (cx + 12, cy + 6), (cx + 8, cy + 10), (cx + 10, cy + 15),
                (cx + 14, cy + 15), (cx + 16, cy + 10)])


class SecretToken:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 18, 18)
        self.collected = False
        self.spin = 0

    def update(self):
        self.spin += 0.15

    def draw(self, surf, camera_x):
        if self.collected:
            return
        cx = self.rect.centerx - camera_x
        cy = self.rect.centery
        radius = 8 + int(2 * math.sin(self.spin))
        pygame.draw.circle(surf, (120, 0, 180), (cx, cy), radius)
        pygame.draw.circle(surf, YELLOW, (cx, cy), max(2, radius - 4))
        pygame.draw.circle(surf, WHITE, (cx - 2, cy - 2), 2)


class Particle:
    def __init__(self, x, y, color, vx=0, vy=0, life=20, radius=3):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.life = life
        self.max_life = life
        self.color = color
        self.radius = radius

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08
        self.life -= 1
        return self.life <= 0

    def draw(self, surf, camera_x):
        if self.life <= 0:
            return
        fade = self.life / max(1, self.max_life)
        r = max(1, int(self.radius * fade))
        color = (
            int(self.color[0] * (0.5 + fade * 0.5)),
            int(self.color[1] * (0.5 + fade * 0.5)),
            int(self.color[2] * (0.5 + fade * 0.5)),
        )
        pygame.draw.circle(surf, color, (int(self.x - camera_x), int(self.y)), r)
