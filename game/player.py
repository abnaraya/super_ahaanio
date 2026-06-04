import pygame
from game.constants import (
    WHITE, BLACK, RED, SKIN, BLUE, BROWN,
    PLAYER_SIZE, PLAYER_SPEED, JUMP_HEIGHT, GRAVITY, HEIGHT, LEVEL_END_X,
)


class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, 100, PLAYER_SIZE, PLAYER_SIZE)
        self.vy = 0
        self.on_ground = False
        self.lives = 1
        self.speed_boost = 0
        self.jump_boost = 0
        self.immunity_timer = 0
        self.speed_timer = 0
        self.jump_timer = 0
        self.base_speed = PLAYER_SPEED
        self.base_jump = JUMP_HEIGHT
        self.coyote_time = 0
        self.jump_buffer = 0
        self.holding_jump = False
        self.current_gravity = GRAVITY
        self.current_wind = 0
        self.coyote_frames = 8
        self.jump_buffer_frames = 10
        self.short_hop_gravity_boost = 0.6

    def move(self, platforms, actions):
        self._just_jumped = False

        if self.immunity_timer > 0:
            self.immunity_timer -= 1
        if self.speed_timer > 0:
            self.speed_timer -= 1
        else:
            self.speed_boost = 0
        if self.jump_timer > 0:
            self.jump_timer -= 1
        else:
            self.jump_boost = 0

        if self.coyote_time > 0:
            self.coyote_time -= 1
        if self.jump_buffer > 0:
            self.jump_buffer -= 1

        dx = 0
        current_speed = self.base_speed + self.speed_boost

        if actions.get("left"):
            dx -= current_speed
        if actions.get("right"):
            dx += current_speed

        dx += self.current_wind

        new_x = self.rect.x + dx
        if new_x < 0:
            dx = -self.rect.x
        elif new_x + self.rect.w > LEVEL_END_X + 70:
            dx = (LEVEL_END_X + 70) - (self.rect.x + self.rect.w)
        self.rect.x += dx

        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if dx > 0:
                    self.rect.right = plat.rect.left
                elif dx < 0:
                    self.rect.left = plat.rect.right

        jump_pressed = actions.get("jump_pressed", False)
        jump_held = actions.get("jump", False)

        if jump_pressed:
            self.jump_buffer = self.jump_buffer_frames

        can_jump = self.on_ground or self.coyote_time > 0
        if self.jump_buffer > 0 and can_jump:
            current_jump = self.base_jump + self.jump_boost
            self.vy = current_jump
            self.on_ground = False
            self.coyote_time = 0
            self.jump_buffer = 0
            self._just_jumped = True

        if not jump_held and self.vy < 0:
            self.vy += self.current_gravity * self.short_hop_gravity_boost

        self.vy += self.current_gravity
        if self.vy > 15:
            self.vy = 15

        old_bottom = self.rect.bottom
        self.rect.y += self.vy

        self.on_ground = False
        for plat in platforms:
            if (self.vy >= 0 and
                    old_bottom <= plat.rect.top and
                    self.rect.colliderect(plat.rect)):
                self.rect.bottom = plat.rect.top
                self.vy = 0
                self.on_ground = True
                self.coyote_time = self.coyote_frames
            elif self.vy < 0 and self.rect.colliderect(plat.rect):
                self.rect.top = plat.rect.bottom
                self.vy = 0

        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vy = 0
            self.on_ground = True
            self.coyote_time = self.coyote_frames

    def apply_powerup(self, power_type):
        if power_type == 'speed':
            self.speed_boost = 3
            self.speed_timer = 600
        elif power_type == 'jump':
            self.jump_boost = -8
            self.jump_timer = 600
        elif power_type == 'life':
            self.lives += 1

    def die(self):
        if self.lives > 1:
            self.lives -= 1
            self.immunity_timer = 180
            return False
        else:
            return True

    def is_immune(self):
        return self.immunity_timer > 0

    def draw(self, surf, camera_x):
        if self.is_immune() and self.immunity_timer % 10 < 5:
            return

        x = self.rect.x - camera_x
        y = self.rect.y

        pygame.draw.ellipse(surf, RED, (x, y + 10, self.rect.w, self.rect.h - 10))
        pygame.draw.ellipse(surf, (180, 45, 60), (x + 5, y + 12, self.rect.w - 10, self.rect.h - 15))
        pygame.draw.ellipse(surf, BLUE, (x + 10, y + 25, self.rect.w - 20, self.rect.h // 2))
        pygame.draw.rect(surf, (0, 100, 200), (x + 15, y + 28, 4, 15))
        pygame.draw.rect(surf, (0, 100, 200), (x + 31, y + 28, 4, 15))
        pygame.draw.ellipse(surf, SKIN, (x + 10, y + 5, self.rect.w - 20, self.rect.h // 2))
        pygame.draw.ellipse(surf, (240, 200, 160), (x + 12, y + 7, self.rect.w - 24, self.rect.h // 2 - 4))
        pygame.draw.ellipse(surf, BROWN, (x + 5, y, self.rect.w - 10, 20))
        pygame.draw.circle(surf, (120, 80, 40), (x + 12, y + 5), 8)
        pygame.draw.circle(surf, (120, 80, 40), (x + 38, y + 5), 8)
        pygame.draw.ellipse(surf, WHITE, (x + 16, y + 15, 8, 10))
        pygame.draw.ellipse(surf, WHITE, (x + 26, y + 15, 8, 10))
        pygame.draw.circle(surf, BLACK, (x + 19, y + 19), 3)
        pygame.draw.circle(surf, BLACK, (x + 29, y + 19), 3)
        pygame.draw.circle(surf, WHITE, (x + 20, y + 18), 1)
        pygame.draw.circle(surf, WHITE, (x + 30, y + 18), 1)
        pygame.draw.circle(surf, (220, 180, 140), (x + 25, y + 22), 2)
        pygame.draw.arc(surf, BLACK, (x + 18, y + 25, 14, 8), 0, 3.14, 2)
        pygame.draw.ellipse(surf, BROWN, (x + 16, y + 23, 18, 4))
