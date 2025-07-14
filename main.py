import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (220, 55, 70)
SKIN = (255, 225, 175)
BLUE = (0, 122, 255)
BROWN = (140, 100, 50)
GREEN = (34, 177, 76)
PIPE_GREEN = (0, 140, 51)
YELLOW = (255, 222, 80)
GOLDEN = (255, 215, 50)
FLAGPOLE = (180, 180, 180)

PLAYER_SIZE = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = -22
GRAVITY = 1

LEVEL_END_X = 1100  # World width

class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, 100, PLAYER_SIZE, PLAYER_SIZE)
        self.vy = 0
        self.on_ground = False

    def move(self, platforms):
        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            dx += PLAYER_SPEED

        # Clamp to world's left and right boundaries
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

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = JUMP_HEIGHT
            self.on_ground = False

        self.vy += GRAVITY
        if self.vy > 15: self.vy = 15

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
            elif (self.vy < 0 and self.rect.colliderect(plat.rect)):
                self.rect.top = plat.rect.bottom
                self.vy = 0

        if self.rect.bottom >= HEIGHT:
            self.rect.bottom = HEIGHT
            self.vy = 0
            self.on_ground = True

    def draw(self, surf, camera_x):
        pygame.draw.ellipse(surf, RED, (self.rect.x-camera_x, self.rect.y+10, self.rect.w, self.rect.h-10))
        pygame.draw.ellipse(surf, SKIN, (self.rect.x+10-camera_x, self.rect.y+10, self.rect.w-20, self.rect.h//2-5))
        pygame.draw.ellipse(surf, BLUE, (self.rect.x+5-camera_x, self.rect.y, self.rect.w-10, 18))
        pygame.draw.ellipse(surf, BLACK, (self.rect.x+19-camera_x, self.rect.y + 27, 6,11))
        pygame.draw.ellipse(surf, BLACK, (self.rect.x+32-camera_x, self.rect.y + 27, 6,11))
        pygame.draw.arc(surf, BLACK, (self.rect.x+18-camera_x, self.rect.y+37, 18,8), 3.5,6.0,2)

class Enemy:
    def __init__(self, x, y, plat_rect):
        self.rect = pygame.Rect(x, y, 34, 34)
        self.speed = 2
        self.direction = 1
        self.platform = plat_rect

    def move(self, platforms):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= self.platform.left:
            self.rect.left = self.platform.left
            self.direction = 1
        if self.rect.right >= self.platform.right:
            self.rect.right = self.platform.right
            self.direction = -1

    def draw(self, surf, camera_x):
        pygame.draw.ellipse(surf, BROWN, (self.rect.x-camera_x, self.rect.y, self.rect.w, self.rect.h//2+6))
        pygame.draw.ellipse(surf, SKIN, (self.rect.x+5-camera_x, self.rect.y+self.rect.h//2-4, self.rect.w-10, self.rect.h//2-2))
        pygame.draw.ellipse(surf, BLACK, (self.rect.x+13-camera_x, self.rect.y+15, 5,7))
        pygame.draw.ellipse(surf, BLACK, (self.rect.x+22-camera_x, self.rect.y+15, 5,7))

class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
    def draw(self, surf, camera_x):
        pygame.draw.rect(surf, BLUE, (self.rect.x+8-camera_x, self.rect.y, self.rect.w-16, self.rect.h), border_radius=9)
        pygame.draw.ellipse(surf, BLUE, (self.rect.x-camera_x, self.rect.y, 16, self.rect.h))
        pygame.draw.ellipse(surf, BLUE, (self.rect.x+self.rect.w-16-camera_x, self.rect.y, 16, self.rect.h))

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
    def draw(self, surf, camera_x):
        pygame.draw.circle(surf, GOLDEN, (self.rect.x+10-camera_x, self.rect.y+10), 10)
        pygame.draw.ellipse(surf, WHITE, (self.rect.x+10-camera_x, self.rect.y+3, 6,5))

class Pipe:
    def __init__(self, x, y, width=50, height=70):
        self.rect = pygame.Rect(x, y, width, height)
    def draw(self, surf, camera_x):
        pygame.draw.rect(surf, PIPE_GREEN, (self.rect.x-camera_x, self.rect.y+15, self.rect.w, self.rect.h-15))
        pygame.draw.ellipse(surf, PIPE_GREEN, (self.rect.x-camera_x-8, self.rect.y, self.rect.w+16, 28))
        pygame.draw.rect(surf, (80,200,120), (self.rect.x-camera_x+9, self.rect.y+25, 8, self.rect.h-31))

class Flag:
    def __init__(self, x, y, height=140):
        self.rect = pygame.Rect(x, y-height, 15, height)
    def draw(self, surf, camera_x):
        pole = pygame.Rect(self.rect.x-camera_x, self.rect.y, 8, self.rect.h)
        pygame.draw.rect(surf, FLAGPOLE, pole)
        pygame.draw.circle(surf, YELLOW, (self.rect.x-camera_x+4, self.rect.y), 8)
        pygame.draw.polygon(surf, YELLOW, [
            (self.rect.x-camera_x+8, self.rect.y+14),
            (self.rect.x-camera_x+8+40, self.rect.y+34),
            (self.rect.x-camera_x+8, self.rect.y+47)
        ])

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    platforms = [
        Platform(0, HEIGHT - 50, LEVEL_END_X+100, 50),
        Platform(300, 450, 120, 20),
        Platform(480, 330, 120, 20),
        Platform(640, 210, 100, 20),
        Platform(900, 400, 180, 24)
    ]

    enemies = [
        Enemy(320, 450-34, platforms[1].rect),
        Enemy(500, 330-34, platforms[2].rect),
        Enemy(650, 210-34, platforms[3].rect),
        Enemy(950, 400-34, platforms[4].rect)
    ]

    coins = [
        Coin(350, 430), Coin(500, 310), Coin(700, 190),
        Coin(950, 380), Coin(1020, 380)
    ]

    # Pipes at logical Mario-like locations:
    pipes = [
        Pipe(170, HEIGHT-120, 60, 70),     # Early pipe after game start
        Pipe(570, HEIGHT-120, 60, 70),     # Middle pipe, between features and gaps
        Pipe(980, HEIGHT-120, 60, 70)      # Pipe before the final flag
    ]

    flag = Flag(LEVEL_END_X+35, HEIGHT-50)

    player = Player()
    score = 0
    camera_x = 0

    running = True
    state = "START"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if state == "START":
            screen.fill(BLACK)
            title = pygame.font.Font(None, 64).render("Super Ahaanio", True, YELLOW)
            prompt = pygame.font.Font(None, 36).render("Press SPACE to Start", True, WHITE)
            screen.blit(title, ((WIDTH-title.get_width())//2, HEIGHT//2-70))
            screen.blit(prompt, ((WIDTH-prompt.get_width())//2, HEIGHT//2))
            pygame.display.flip()
            if keys[pygame.K_SPACE]:
                state = "PLAY"
            clock.tick(FPS)
            continue
        if state == "GAMEOVER":
            screen.fill(BLACK)
            msg = pygame.font.Font(None, 64).render("Game Over!", True, RED)
            score_display = pygame.font.Font(None, 36).render(f"Score: {score}", True, YELLOW)
            prompt = pygame.font.Font(None, 36).render("Press SPACE to Restart", True, WHITE)
            screen.blit(msg, ((WIDTH-msg.get_width())//2, HEIGHT//2-70))
            screen.blit(score_display, ((WIDTH-score_display.get_width())//2, HEIGHT//2))
            screen.blit(prompt, ((WIDTH-prompt.get_width())//2, HEIGHT//2+50))
            pygame.display.flip()
            if keys[pygame.K_SPACE]:
                player.__init__()
                enemies[:] = [
                    Enemy(320, 450-34, platforms[1].rect),
                    Enemy(500, 330-34, platforms[2].rect),
                    Enemy(650, 210-34, platforms[3].rect),
                    Enemy(950, 400-34, platforms[4].rect)
                ]
                coins[:] = [
                    Coin(350, 430), Coin(500, 310), Coin(700, 190),
                    Coin(950, 380), Coin(1020, 380)
                ]
                state = "PLAY"
                score = 0
            clock.tick(FPS)
            continue
        if state == "COMPLETE":
            screen.fill(BLACK)
            msg = pygame.font.Font(None, 64).render("Level Complete!", True, YELLOW)
            score_display = pygame.font.Font(None, 36).render(f"Final Score: {score}", True, GOLDEN)
            prompt = pygame.font.Font(None, 36).render("Press SPACE to Restart", True, WHITE)
            screen.blit(msg, ((WIDTH-msg.get_width())//2, HEIGHT//2-70))
            screen.blit(score_display, ((WIDTH-score_display.get_width())//2, HEIGHT//2))
            screen.blit(prompt, ((WIDTH-prompt.get_width())//2, HEIGHT//2+50))
            pygame.display.flip()
            if keys[pygame.K_SPACE]:
                player.__init__()
                enemies[:] = [
                    Enemy(320, 450-34, platforms[1].rect),
                    Enemy(500, 330-34, platforms[2].rect),
                    Enemy(650, 210-34, platforms[3].rect),
                    Enemy(950, 400-34, platforms[4].rect)
                ]
                coins[:] = [
                    Coin(350, 430), Coin(500, 310), Coin(700, 190),
                    Coin(950, 380), Coin(1020, 380)
                ]
                state = "PLAY"
                score = 0
            clock.tick(FPS)
            continue

        # --- Game Play ---
        player.move(platforms)
        stomped = False
        remove_enemies = []
        for enemy in enemies:
            enemy.move(platforms)
        for i,enemy in enumerate(enemies):
            if player.rect.colliderect(enemy.rect):
                if player.vy > 0 and player.rect.bottom - enemy.rect.top < 24 and player.rect.top < enemy.rect.top:
                    remove_enemies.append(i)
                    player.vy = JUMP_HEIGHT // 2
                    stomped = True
                    score += 100
                else:
                    state = "GAMEOVER"
                    break
        for idx in sorted(remove_enemies, reverse=True):
            del enemies[idx]
        for coin in coins[:]:
            if player.rect.colliderect(coin.rect):
                coins.remove(coin)
                score += 1
        for pipe in pipes:
            if player.rect.colliderect(pipe.rect):
                if player.rect.bottom > pipe.rect.top and player.vy >= 0:
                    player.rect.bottom = pipe.rect.top
                    player.vy = 0
                    player.on_ground = True

        if player.rect.colliderect(flag.rect):
            state = "COMPLETE"

        camera_x = player.rect.centerx - WIDTH // 2
        if camera_x < 0:
            camera_x = 0
        max_cam = LEVEL_END_X + 100 - WIDTH
        if camera_x > max_cam:
            camera_x = max_cam

        screen.fill((92,192,255))
        for platform in platforms:
            platform.draw(screen, camera_x)
        for pipe in pipes:
            pipe.draw(screen, camera_x)
        for enemy in enemies:
            enemy.draw(screen, camera_x)
        for coin in coins:
            coin.draw(screen, camera_x)
        flag.draw(screen, camera_x)
        player.draw(screen, camera_x)
        font = pygame.font.Font(None, 36)
        text = font.render(f'Score: {score}', True, BLACK)
        screen.blit(text, (10, 10))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
