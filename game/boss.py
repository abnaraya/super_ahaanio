import math
import random
import pygame
from game.constants import (
    WHITE, BLACK, RED, SKIN, BROWN, YELLOW,
    HEIGHT, LEVEL_END_X,
)
from game.enemies import Slipper


class Boss:
    def __init__(self, x, y, level=1):
        self.rect = pygame.Rect(x, y, 80, 80)
        self.health = 3
        self.stage = 1
        self.level = level
        self.speed = 1.5 + (level - 1) * 0.3
        self.direction = 1
        self.slipper_timer = 0
        self.slipper_cooldown = max(90 - (level - 1) * 8, 50)
        self.move_timer = 0
        self.move_duration = 180
        self.slippers = []
        self.hit_invulnerable = 0
        self.shout_frames = 0
        self.attack_warning_frames = 0

    def update(self, player):
        if self.hit_invulnerable > 0:
            self.hit_invulnerable -= 1
        if self.shout_frames > 0:
            self.shout_frames -= 1
        if self.attack_warning_frames > 0:
            self.attack_warning_frames -= 1

        if self.stage == 1:
            self.slipper_timer += 1
            if self.slipper_timer >= self.slipper_cooldown - 18:
                self.attack_warning_frames = max(self.attack_warning_frames, 6)
            if self.slipper_timer >= self.slipper_cooldown:
                self._throw_random_slippers()
                self.slipper_timer = 0
                self.shout_frames = 30

        elif self.stage == 2:
            self.slipper_timer += 1
            if self.slipper_timer >= int(self.slipper_cooldown * 0.8) - 14:
                self.attack_warning_frames = max(self.attack_warning_frames, 6)
            if self.slipper_timer >= int(self.slipper_cooldown * 0.8):
                self._throw_targeted_slipper(player)
                self.slipper_timer = 0
                self.shout_frames = 30

        elif self.stage == 3:
            self.move_timer += 1
            if self.move_timer >= self.move_duration:
                self.direction *= -1
                self.move_timer = 0

            self.rect.x += self.speed * self.direction
            if self.rect.left <= 100:
                self.rect.left = 100
                self.direction = 1
            elif self.rect.right >= LEVEL_END_X - 100:
                self.rect.right = LEVEL_END_X - 100
                self.direction = -1
            if self.rect.centerx < 150:
                self.rect.centerx = 150
                self.direction = 1
            elif self.rect.centerx > LEVEL_END_X - 150:
                self.rect.centerx = LEVEL_END_X - 150
                self.direction = -1
            if self.rect.bottom > HEIGHT - 80:
                self.rect.bottom = HEIGHT - 80
            if self.rect.top < 100:
                self.rect.top = 100

            self.slipper_timer += 1
            if self.slipper_timer >= int(self.slipper_cooldown * 0.6) - 10:
                self.attack_warning_frames = max(self.attack_warning_frames, 6)
            if self.slipper_timer >= int(self.slipper_cooldown * 0.6):
                self._throw_targeted_slipper(player)
                self.slipper_timer = 0
                self.shout_frames = 30

        self.slippers = [s for s in self.slippers if not s.update()]

        if self.rect.left < 50:
            self.rect.left = 50
        if self.rect.right > LEVEL_END_X - 50:
            self.rect.right = LEVEL_END_X - 50
        if self.rect.bottom > HEIGHT - 60:
            self.rect.bottom = HEIGHT - 60
        if self.rect.top < 80:
            self.rect.top = 80

    def _throw_random_slippers(self):
        num_slippers = random.randint(3, 4)
        for _ in range(num_slippers):
            slipper = Slipper(self.rect.centerx, self.rect.centery, None, None, 3 + self.level * 0.5)
            self.slippers.append(slipper)

    def _throw_targeted_slipper(self, player):
        slipper = Slipper(self.rect.centerx, self.rect.centery,
                          player.rect.centerx, player.rect.centery, speed=4 + self.level * 0.5)
        self.slippers.append(slipper)

    def take_damage(self):
        if self.hit_invulnerable <= 0:
            self.health -= 1
            self.stage += 1
            self.hit_invulnerable = 180
            return True
        return False

    def is_defeated(self):
        return self.health <= 0

    def draw(self, surf, camera_x):
        if self.hit_invulnerable > 0 and self.hit_invulnerable % 10 < 5:
            return
        cx = self.rect.x - camera_x
        pygame.draw.ellipse(surf, (255, 182, 193), (cx, self.rect.y + 30, self.rect.w, self.rect.h - 30))
        pygame.draw.ellipse(surf, SKIN, (cx + 15, self.rect.y, self.rect.w - 30, 40))
        pygame.draw.ellipse(surf, BROWN, (cx + 10, self.rect.y - 5, self.rect.w - 20, 25))
        pygame.draw.ellipse(surf, BLACK, (cx + 25, self.rect.y + 15, 8, 8))
        pygame.draw.ellipse(surf, BLACK, (cx + 45, self.rect.y + 15, 8, 8))
        pygame.draw.arc(surf, BLACK, (cx + 30, self.rect.y + 25, 20, 10), 0, 3.14, 3)

        if self.shout_frames > 0:
            from game.renderer import get_font
            shout = get_font(30).render("AHAAAAN!!", True, YELLOW, BLACK)
            surf.blit(shout, (cx + 10, self.rect.y - 30))

        for i in range(self.health):
            pygame.draw.circle(surf, RED, (cx + 10 + i * 25, self.rect.y - 15), 8)

        if self.attack_warning_frames > 0:
            pygame.draw.circle(surf, YELLOW, (self.rect.centerx - camera_x, self.rect.top - 20), 10, 3)

        for slipper in self.slippers:
            slipper.draw(surf, camera_x)


class Mom:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y - 60, 46, 60)
        self.throw_timer = 0
        self.shout_frames = 0
        self.slippers = []

    def update(self):
        self.throw_timer += 1
        if self.shout_frames > 0:
            self.shout_frames -= 1

        if self.throw_timer > random.randint(180, 300):
            self.throw_timer = 0
            self.shout_frames = 30
            num_slippers = random.randint(3, 5)
            for _ in range(num_slippers):
                slipper = Slipper(self.x + 16, self.y - 30, None, None, random.randint(4, 8))
                self.slippers.append(slipper)

        self.slippers = [s for s in self.slippers if not s.update()]

    def draw(self, surf, camera_x):
        cx = self.x - camera_x
        pygame.draw.ellipse(surf, (255, 182, 193), (cx, self.y - 25, 46, 48))
        pygame.draw.ellipse(surf, SKIN, (cx + 7, self.y - 60, 32, 32))
        pygame.draw.ellipse(surf, BLACK, (cx + 15, self.y - 47, 6, 10))
        pygame.draw.ellipse(surf, BLACK, (cx + 27, self.y - 47, 6, 10))
        pygame.draw.circle(surf, BLACK, (cx + 23, self.y - 63), 8)
        pygame.draw.arc(surf, BLACK, (cx + 15, self.y - 37, 16, 8), 3.5, 6.0, 2)

        if self.shout_frames > 0:
            from game.renderer import get_font
            shout = get_font(30).render("AHAAAAN!!", True, YELLOW, BLACK)
            surf.blit(shout, (cx + 10, self.y - 82))

        for slipper in self.slippers:
            slipper.draw(surf, camera_x)
