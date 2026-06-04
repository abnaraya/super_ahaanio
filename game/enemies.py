import random
import pygame
from game.constants import (
    WHITE, BLACK, RED, SKIN, BLUE, BROWN, YELLOW,
    HEIGHT, LEVEL_END_X,
)


class Shuttlecock:
    def __init__(self, x, y, direction, speed=4):
        self.rect = pygame.Rect(x, y, 12, 20)
        self.direction = direction
        self.speed = speed
        self.rotation = 0
        self.gravity = 0.3
        self.vy = -2

    def update(self):
        self.rect.x += self.speed * self.direction
        self.vy += self.gravity
        self.rect.y += self.vy
        self.rotation += 5
        return (self.rect.x < -100 or self.rect.x > LEVEL_END_X + 100 or
                self.rect.y > HEIGHT + 50)

    def draw(self, surf, camera_x):
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y
        if -50 < screen_x < 800 + 50 and -50 < screen_y < 600 + 50:
            pygame.draw.ellipse(surf, WHITE, (int(screen_x), int(screen_y), 12, 8))
            pygame.draw.ellipse(surf, (240, 240, 240), (int(screen_x + 1), int(screen_y + 1), 10, 6))
            pygame.draw.ellipse(surf, BLACK, (int(screen_x + 2), int(screen_y + 8), 8, 12))
            pygame.draw.ellipse(surf, (60, 60, 60), (int(screen_x + 3), int(screen_y + 9), 6, 10))
            for i in range(3):
                line_x = screen_x + 3 + i * 2
                pygame.draw.line(surf, (200, 200, 200), (int(line_x), int(screen_y + 2)),
                                 (int(line_x), int(screen_y + 6)), 1)


class Slipper:
    def __init__(self, x, y, target_x=None, target_y=None, speed=6):
        self.rect = pygame.Rect(x, y, 20, 15)
        self.speed = speed
        if target_x is not None and target_y is not None:
            dx = target_x - x
            dy = target_y - y
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length > 0:
                self.vx = (dx / length) * speed
                self.vy = (dy / length) * speed
            else:
                self.vx = speed
                self.vy = 0
        else:
            angle = random.uniform(0, 2 * 3.14159)
            self.vx = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            self.vy = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        return (self.rect.x < -200 or self.rect.x > LEVEL_END_X + 300 or
                self.rect.y < -200 or self.rect.y > HEIGHT + 200)

    def draw(self, surf, camera_x):
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y
        if -100 < screen_x < 800 + 100 and -100 < screen_y < 600 + 100:
            pygame.draw.ellipse(surf, (139, 69, 19), (int(screen_x), int(screen_y + 8), 20, 12))
            pygame.draw.ellipse(surf, (180, 100, 60), (int(screen_x + 2), int(screen_y + 3), 16, 10))
            pygame.draw.ellipse(surf, (120, 60, 30), (int(screen_x + 1), int(screen_y + 12), 6, 6))
            pygame.draw.ellipse(surf, (200, 120, 80), (int(screen_x + 12), int(screen_y + 5), 6, 6))


class Enemy:
    def __init__(self, x, y, enemy_type="homework", plat_rect=None):
        self.rect = pygame.Rect(x, y, 34, 34)
        self.speed = 2
        self.direction = 1
        if plat_rect is None:
            self.platform = pygame.Rect(x - 50, y, 134, 34)
        else:
            self.platform = plat_rect
        self.enemy_type = enemy_type
        if self.enemy_type == "badminton":
            self.shoot_timer = 0
            self.shoot_cooldown = 120
            self.shuttlecocks = []

    def move(self, platforms):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= self.platform.left:
            self.rect.left = self.platform.left
            self.direction = 1
        if self.rect.right >= self.platform.right:
            self.rect.right = self.platform.right
            self.direction = -1

        if self.enemy_type == "badminton":
            self.shoot_timer += 1
            if self.shoot_timer >= self.shoot_cooldown:
                self.shoot_timer = 0
                shuttlecock = Shuttlecock(self.rect.centerx, self.rect.y - 10, self.direction)
                self.shuttlecocks.append(shuttlecock)
            self.shuttlecocks = [s for s in self.shuttlecocks if not s.update()]

    def draw(self, surf, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y
        w = self.rect.w
        h = self.rect.h

        if self.enemy_type == "homework":
            pygame.draw.rect(surf, BROWN, (x, y, w, h))
            pygame.draw.rect(surf, (180, 120, 70), (x + 2, y + 2, w - 4, h - 4))
            pygame.draw.rect(surf, WHITE, (x + 3, y + 3, w - 6, h - 6))
            for i in range(4):
                line_y = y + 8 + i * 6
                pygame.draw.line(surf, (200, 200, 255), (x + 5, line_y), (x + w - 5, line_y), 1)
            pygame.draw.rect(surf, (100, 60, 30), (x, y, 3, h))
            pygame.draw.rect(surf, BLACK, (x + 6, y + 6, w - 12, 4))

        elif self.enemy_type == "chores":
            pygame.draw.rect(surf, BROWN, (x + 12, y, 8, 20))
            pygame.draw.rect(surf, (160, 120, 80), (x + 13, y, 6, 20))
            for i in range(y, y + 20, 3):
                pygame.draw.line(surf, (120, 80, 40), (x + 13, i), (x + 18, i), 1)
            pygame.draw.ellipse(surf, YELLOW, (x + 5, y + 18, 22, 14))
            pygame.draw.ellipse(surf, (255, 255, 150), (x + 7, y + 20, 18, 10))
            for i in range(6):
                bristle_x = x + 8 + i * 3
                pygame.draw.line(surf, (200, 180, 100), (bristle_x, y + 22), (bristle_x, y + 30), 1)

        elif self.enemy_type == "badminton":
            pygame.draw.ellipse(surf, RED, (x + 8, y, 18, 22))
            pygame.draw.ellipse(surf, (255, 100, 100), (x + 10, y + 2, 14, 18))
            pygame.draw.rect(surf, BROWN, (x + 15, y + 15, 4, 17))
            pygame.draw.rect(surf, (160, 120, 80), (x + 15, y + 15, 4, 17))
            for i in range(y + 16, y + 30, 2):
                pygame.draw.line(surf, (100, 70, 40), (x + 15, i), (x + 18, i), 1)
            for i in range(3):
                string_x = x + 12 + i * 3
                pygame.draw.line(surf, WHITE, (string_x, y + 4), (string_x, y + 18), 1)
            for i in range(4):
                string_y = y + 5 + i * 3
                pygame.draw.line(surf, WHITE, (x + 10, string_y), (x + 24, string_y), 1)
            for shuttlecock in self.shuttlecocks:
                shuttlecock.draw(surf, camera_x)

        elif self.enemy_type == "shower":
            pygame.draw.rect(surf, (180, 180, 180), (x + 5, y + 5, 24, 15))
            pygame.draw.rect(surf, (220, 220, 220), (x + 6, y + 6, 22, 13))
            pygame.draw.rect(surf, (140, 140, 140), (x + 26, y + 6, 2, 13))
            for i in range(3):
                for j in range(6):
                    pygame.draw.circle(surf, (100, 100, 100), (x + 8 + j * 3, y + 8 + i * 3), 1)
            for i in range(6):
                drop_x = x + 8 + i * 3
                drop_y = y + 22 + random.randint(0, 8)
                pygame.draw.circle(surf, BLUE, (drop_x, drop_y), 2)
                pygame.draw.circle(surf, (150, 200, 255), (drop_x - 1, drop_y - 1), 1)

        else:
            pygame.draw.ellipse(surf, BROWN, (x, y, w, h // 2 + 6))
            pygame.draw.ellipse(surf, (180, 120, 70), (x + 2, y + 2, w - 4, h // 2 + 2))
            pygame.draw.ellipse(surf, SKIN, (x + 5, y + h // 2 - 4, w - 10, h // 2 - 2))
            pygame.draw.ellipse(surf, (240, 200, 160), (x + 7, y + h // 2 - 2, w - 14, h // 2 - 6))
            pygame.draw.ellipse(surf, WHITE, (x + 11, y + 13, 7, 9))
            pygame.draw.ellipse(surf, WHITE, (x + 20, y + 13, 7, 9))
            pygame.draw.circle(surf, BLACK, (x + 14, y + 16), 2)
            pygame.draw.circle(surf, BLACK, (x + 23, y + 16), 2)
