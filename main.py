import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Player properties
PLAYER_SIZE = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = -15
GRAVITY = 1

class Player(pygame.Rect):
    def __init__(self):
        super().__init__(100, 100, PLAYER_SIZE, PLAYER_SIZE)
        self.vy = 0
        self.on_ground = False

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.x += PLAYER_SPEED
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = JUMP_HEIGHT
            self.on_ground = False

        self.vy += GRAVITY
        self.y += self.vy

        if self.bottom >= HEIGHT:
            self.bottom = HEIGHT
            self.vy = 0
            self.on_ground = True

class Enemy(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30)
        self.speed = 2

    def move(self):
        self.x += self.speed
        if self.left < 0 or self.right > WIDTH:
            self.speed = -self.speed

class Platform(pygame.Rect):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)

class Coin(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20)

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    player = Player()
    enemies = [Enemy(200, 500)]
    platforms = [Platform(0, HEIGHT - 50, WIDTH, 50), Platform(300, 400, 200, 20)]
    coins = [Coin(350, 380)]

    score = 0
    camera_x = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.move()

        for enemy in enemies:
            enemy.move()

        # Collision detection
        for platform in platforms:
            if player.colliderect(platform):
                if player.vy > 0:
                    player.bottom = platform.top
                    player.on_ground = True
                elif player.vy < 0:
                    player.top = platform.bottom
                player.vy = 0

        for coin in coins[:]:
            if player.colliderect(coin):
                coins.remove(coin)
                score += 1

        for enemy in enemies:
            if player.colliderect(enemy):
                running = False

        # Camera scrolling
        camera_x = player.centerx - WIDTH / 2
        if camera_x < 0:
            camera_x = 0

        screen.fill(GREEN)

        # Draw everything relative to camera
        for platform in platforms:
            pygame.draw.rect(screen, BLUE, (platform.x - camera_x, platform.y, platform.width, platform.height))
        for enemy in enemies:
            pygame.draw.rect(screen, RED, (enemy.x - camera_x, enemy.y, enemy.width, enemy.height))
        for coin in coins:
            pygame.draw.rect(screen, (255, 255, 0), (coin.x - camera_x, coin.y, coin.width, coin.height))
        pygame.draw.rect(screen, WHITE, (player.x - camera_x, player.y, player.width, player.height))

        font = pygame.font.Font(None, 36)
        text = font.render(f'Score: {score}', True, BLACK := (0, 0, 0))
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
