import pygame
import sys
import random

# Initialize Pygame
pygame.init()
# --- Super Ahaanio BGM Setup ---
# To use background music, place a Mario-like theme mp3/ogg as "bgm.mp3" in this directory.
import os
try:
    import pygame.mixer
    pygame.mixer.init()
    if os.path.exists("bgm.mp3"):
        pygame.mixer.music.load("bgm.mp3")
        pygame.mixer.music.set_volume(0.001)  # Start at volume level 1/10
        pygame.mixer.music.play(-1)  # Loop forever
        BGM_ENABLED = True
    else:
        print("bgm.mp3 not found. Game runs silently. (Add a background music file for music!)")
        BGM_ENABLED = False
except Exception as e:
    print("Could not initialize background music:", e)
    BGM_ENABLED = False

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
SLIPPER_BASE = (185, 147, 93)
SLIPPER_STRAP = (28, 60, 130)
MOM_SAREE = (221, 44, 112)
GREEN = (34, 177, 76)
PIPE_GREEN = (0, 140, 51)
YELLOW = (255, 222, 80)
GOLDEN = (255, 215, 50)
FLAGPOLE = (180, 180, 180)

PLAYER_SIZE = 50
PLAYER_SPEED = 5
JUMP_HEIGHT = -22
GRAVITY = 1

LEVEL_END_X = 2200  # Extended world width for larger first level

COIN_WORLD_STATE = "COIN_WORLD"

class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, 100, PLAYER_SIZE, PLAYER_SIZE)
        self.vy = 0
        self.on_ground = False
        self.invincible = False
        self.invincible_timer = 0
        self.speed_boost = False
        self.speed_boost_timer = 0
        self.coin_bonus = False
        self.coin_bonus_timer = 0
        self.jump_boost = False
        self.jump_boost_timer = 0

    def move(self, platforms):
        keys = pygame.key.get_pressed()
        dx = 0
        speed = PLAYER_SPEED
        if self.speed_boost:
            speed += 3
        if keys[pygame.K_LEFT]:
            dx -= speed
        if keys[pygame.K_RIGHT]:
            dx += speed

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
            if self.jump_boost:
                self.vy = JUMP_HEIGHT - 10
            else:
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

        # Handle timers for boosts
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            self.invincible = True
            if self.invincible_timer == 0:
                self.invincible = False
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
            self.speed_boost = True
            if self.speed_boost_timer == 0:
                self.speed_boost = False
        if self.coin_bonus_timer > 0:
            self.coin_bonus_timer -= 1
            self.coin_bonus = True
            if self.coin_bonus_timer == 0:
                self.coin_bonus = False
        if self.jump_boost_timer > 0:
            self.jump_boost_timer -= 1
            self.jump_boost = True
            if self.jump_boost_timer == 0:
                self.jump_boost = False

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
        # Default enemy (we will override in subclasses)
        pygame.draw.ellipse(surf, BROWN, (self.rect.x-camera_x, self.rect.y, self.rect.w, self.rect.h//2+6))
        pygame.draw.ellipse(surf, SKIN, (self.rect.x+5-camera_x, self.rect.y+self.rect.h//2-4, self.rect.w-10, self.rect.h//2-2))
        pygame.draw.ellipse(surf, BLACK, (self.rect.x+13-camera_x, self.rect.y+15, 5,7))
        pygame.draw.ellipse(surf, BLACK, (self.rect.x+22-camera_x, self.rect.y+15, 5,7))

class BookEnemy(Enemy):
    def draw(self, surf, camera_x):
        # Draw as a blue book with a face
        pygame.draw.rect(surf, (120, 200, 230), (self.rect.x-camera_x, self.rect.y, self.rect.w, self.rect.h))
        pygame.draw.line(surf, (230,230,255), (self.rect.x-camera_x+5, self.rect.y+5), (self.rect.x-camera_x+5, self.rect.y+self.rect.h-5), 3)
        pygame.draw.rect(surf, (220,220,255), (self.rect.x-camera_x+5, self.rect.y+5, self.rect.w-10, self.rect.h-10), 2)
        pygame.draw.ellipse(surf, BLACK, (self.rect.x+8-camera_x, self.rect.y+12, 5,7))
        pygame.draw.ellipse(surf, BLACK, (self.rect.x+21-camera_x, self.rect.y+12, 5,7))
        pygame.draw.arc(surf, BLACK, (self.rect.x+10-camera_x, self.rect.y+22, 13,5), 3.14, 0, 2)

class BadmintonEnemy(Enemy):
    def draw(self, surf, camera_x):
        # Draw as a shuttlecock with angry face
        pygame.draw.polygon(surf, (210,210,210), [
            (self.rect.x-camera_x+17, self.rect.y),
            (self.rect.x-camera_x+6, self.rect.y+26),
            (self.rect.x-camera_x+28, self.rect.y+26)
        ])
        pygame.draw.ellipse(surf, (255,255,255), (self.rect.x-camera_x+6, self.rect.y+22, 22,12))
        pygame.draw.ellipse(surf, BLACK, (self.rect.x+11-camera_x, self.rect.y+18, 3,4))
        pygame.draw.ellipse(surf, BLACK, (self.rect.x+20-camera_x, self.rect.y+18, 3,4))
        pygame.draw.arc(surf, BLACK, (self.rect.x+13-camera_x, self.rect.y+24, 7,4), 3.14, 0, 1)

class ParentEnemy(Enemy):
    def draw(self, surf, camera_x):
        # Draw as stick-figure with a megaphone (speaker mouth)
        pygame.draw.line(surf, BLACK, (self.rect.x-camera_x+17, self.rect.y+15), (self.rect.x-camera_x+17, self.rect.y+30), 3) # body
        pygame.draw.circle(surf, (255,212,170), (self.rect.x-camera_x+17, self.rect.y+10), 8) # head
        pygame.draw.line(surf, BLACK, (self.rect.x-camera_x+17, self.rect.y+25), (self.rect.x-camera_x+5, self.rect.y+20), 3) # left arm
        pygame.draw.line(surf, BLACK, (self.rect.x-camera_x+17, self.rect.y+25), (self.rect.x-camera_x+30, self.rect.y+10), 3) # right arm (with megaphone)
        pygame.draw.polygon(surf, (190,0,0), [
            (self.rect.x-camera_x+31, self.rect.y+9), (self.rect.x-camera_x+39, self.rect.y+7), (self.rect.x-camera_x+37, self.rect.y+13)
        ])
        pygame.draw.arc(surf, BLACK, (self.rect.x+12-camera_x, self.rect.y+14, 10,5), 3.14, 0, 1)

class Friend:
    def __init__(self, x, y, kind="VideoGame"):
        self.rect = pygame.Rect(x, y, 34, 34)
        self.kind = kind
        self.active = True

    def draw(self, surf, camera_x):
        if self.kind == "VideoGame":
            # Draw a game controller
            pygame.draw.ellipse(surf, (88,88,88), (self.rect.x-camera_x, self.rect.y+8, 34, 18))
            pygame.draw.circle(surf, (220,34,44), (self.rect.x+13-camera_x, self.rect.y+17), 3)
            pygame.draw.circle(surf, (45,89,220), (self.rect.x+21-camera_x, self.rect.y+17), 3)
            pygame.draw.rect(surf, (40,40,40), (self.rect.x+12-camera_x, self.rect.y+13, 10,6), 1)
        elif self.kind == "Lego":
            # Draw a yellow lego brick
            pygame.draw.rect(surf, (254,220,40), (self.rect.x-camera_x, self.rect.y+10, 34, 16))
            for i in range(3):
                pygame.draw.ellipse(surf, (255,255,140), (self.rect.x-camera_x+5+10*i, self.rect.y+6, 8,8))
        elif self.kind == "Pizza":
            # Pizza slice!
            pygame.draw.polygon(surf, (230,180,30), [
                (self.rect.x-camera_x+17, self.rect.y+4), (self.rect.x-camera_x+32, self.rect.y+30), (self.rect.x-camera_x+2, self.rect.y+30)
            ])
            pygame.draw.circle(surf, (255,70,70), (self.rect.x-camera_x+17, self.rect.y+21), 5)
            pygame.draw.circle(surf, (234,200,100), (self.rect.x-camera_x+9, self.rect.y+19), 2)
            pygame.draw.circle(surf, (234,200,100), (self.rect.x-camera_x+24, self.rect.y+27), 2)
        else:
            # Default: draw star
            pygame.draw.polygon(surf, (255,223,65), [
                (self.rect.x-camera_x+17, self.rect.y+3),
                (self.rect.x-camera_x+22, self.rect.y+28),
                (self.rect.x-camera_x+2, self.rect.y+12),
                (self.rect.x-camera_x+32, self.rect.y+12),
                (self.rect.x-camera_x+12, self.rect.y+28)
            ])

    def apply_power(self, player):
        if self.kind == "VideoGame":
            player.invincible = True
            player.invincible_timer = 180
        elif self.kind == "Soccer":
            player.speed_boost = True
            player.speed_boost_timer = 180
        elif self.kind == "RSM Math":
            player.coin_bonus = True
            player.coin_bonus_timer = 180
        elif self.kind == "Swimming":
            player.jump_boost = True
            player.jump_boost_timer = 180
        elif self.kind == "Lego":
            player.invincible = True
            player.invincible_timer = 120
        elif self.kind == "Pizza":
            player.coin_bonus = True
            player.coin_bonus_timer = 300
        self.active = False

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

class Slipper:
    def __init__(self, x, y, vx, vy):
        self.rect = pygame.Rect(x, y, 36, 16)
        self.vx = vx
        self.vy = vy
        self.angle = random.uniform(-0.5, 0.5)
    def move(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
    def draw(self, surf, camera_x):
        slipper_surf = pygame.Surface((36, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(slipper_surf, SLIPPER_BASE, (0, 0, 36, 16))
        pygame.draw.arc(slipper_surf, BLACK, (1, 2, 34, 12), 0.3, 2.8, 2)
        pygame.draw.line(slipper_surf, SLIPPER_STRAP, (18,2), (7,12), 4)
        pygame.draw.line(slipper_surf, SLIPPER_STRAP, (18,2), (29,12), 4)
        pygame.draw.line(slipper_surf, SLIPPER_STRAP, (15,6), (21,6), 3)
        slipper_surf = pygame.transform.rotate(slipper_surf, self.angle*50)
        surf.blit(slipper_surf, (self.rect.x-camera_x, self.rect.y))

class Mom:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y-60, 46, 60)
        self.throw_timer = 0
        self.shout_frames = 0
    def update(self):
        self.throw_timer += 1
        if self.throw_timer > random.randint(100,160):
            self.throw_timer = 0
            self.shout_frames = 30  # show "AHAAAN!!" for 30 frames
            return True
        return False
    def draw(self, surf, camera_x):
        pygame.draw.ellipse(surf, MOM_SAREE, (self.x-camera_x, self.y-25, 46,48))
        pygame.draw.ellipse(surf, SKIN, (self.x+7-camera_x, self.y-60, 32,32))
        pygame.draw.ellipse(surf, BLACK, (self.x+15-camera_x, self.y-47, 6, 10))
        pygame.draw.ellipse(surf, BLACK, (self.x+27-camera_x, self.y-47, 6, 10))
        pygame.draw.circle(surf, BLACK, (self.x+23-camera_x, self.y-63), 8)
        pygame.draw.arc(surf, BLACK, (self.x+15-camera_x, self.y-37, 16, 8), 3.5,6.0,2)
        # Draw "AHAAAAN!!" bubble if needed
        if self.shout_frames > 0:
            font = pygame.font.Font(None, 30)
            shout = font.render("AHAAAAN!!", True, YELLOW, BLACK)
            surf.blit(shout, (self.x-camera_x+10, self.y-82))

    def tick_shout(self):
        if self.shout_frames > 0:
            self.shout_frames -= 1

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

def build_level(level):
    import random
    random.seed(level + random.randint(0, 1000000))
    # Dynamic: mix up platforms, enemies, friends by level

    # Vary platform layouts per level
    plat_configs = [
        # Level 0: mostly left; Level 1: mid+right; Level 2: mid crossings, etc
        [
            (0, HEIGHT - 50, LEVEL_END_X+100, 50),
            (random.randint(300,380), 450, 120, 20),
            (random.randint(500,720), 330, 120, 20),
            (random.randint(800,1050), 210, 100, 20),
            (random.randint(900,1400), random.randint(350,440), 180, 24),
            (random.randint(1200,1600), random.randint(280,480), 160, 20),
            (random.randint(1550,1800), random.randint(200,330), 120, 20),
            (random.randint(1800,2000), random.randint(220,330), 100, 20),
        ],
        [
            (0, HEIGHT - 50, LEVEL_END_X+100, 50),
            (random.randint(150,350), random.randint(350, 500), 100, 20),
            (random.randint(600,900), random.randint(250, 400), 120, 15),
            (random.randint(950,1300), random.randint(190, 400), 100, 15),
            (random.randint(1200,1600), random.randint(120, 300), 140, 18),
            (random.randint(1700,2100), random.randint(150, 420), 160, 16),
        ],
        [
            (0, HEIGHT - 50, LEVEL_END_X+100, 50),
            (random.randint(200,400), 350, 120, 20),
            (random.randint(700,1100), 260, 110, 18),
            (random.randint(1200,1700), 200, 150, 22),
            (random.randint(1600,2100), random.randint(150,350), 160, 20),
        ]
    ]
    plat = plat_configs[level % len(plat_configs)]
    platforms = [Platform(*p) for p in plat]

    # Select different sets of enemy/friend types for each level
    ENEMY_TYPES = [
        [BookEnemy, BadmintonEnemy],
        [ParentEnemy, BookEnemy],
        [BadmintonEnemy, ParentEnemy]
    ]
    FRIEND_TYPES = [
        ["VideoGame", "Soccer", "Lego"],
        ["Swimming", "Pizza", "RSM Math"],
        ["Pizza", "Lego", "Soccer"]
    ]
    etypes = ENEMY_TYPES[level % len(ENEMY_TYPES)]
    ftypes = FRIEND_TYPES[level % len(FRIEND_TYPES)]

    # Place enemies/friends, random positions on platforms, no repeats
    enemies = []
    friends = []
    placed_enemy_pos = set()
    placed_friend_pos = set()
    # Enemies: per platform (except ground), one or two per plat, random x
    for idx, plat in enumerate(platforms[1:]):
        n = random.randint(1, 2)
        for _ in range(n):
            ex = plat.rect.x + random.randint(0, plat.rect.w-34)
            if (ex, plat.rect.y-34) not in placed_enemy_pos:
                eclass = random.choice(etypes)
                enemies.append(eclass(ex, plat.rect.y-34, plat.rect))
                placed_enemy_pos.add((ex, plat.rect.y-34))
    # Friends: a few per level, at different places
    for plat in random.sample(platforms[1:], min(3, len(platforms)-1)):
        fx = plat.rect.x + random.randint(0, plat.rect.w-34)
        kind = random.choice(ftypes)
        if (fx, plat.rect.y-34) not in placed_friend_pos:
            friends.append(Friend(fx, plat.rect.y-34, kind))
            placed_friend_pos.add((fx, plat.rect.y-34))
    # Coins: per level, random on platforms
    coins = []
    for plat in platforms[1:]:
        for _ in range(random.randint(1, 3)):
            cx = plat.rect.x + random.randint(0, plat.rect.w-20)
            cy = plat.rect.y - random.randint(10, 30)
            coins.append(Coin(cx, cy))
    # Pipes: a few at diverse locations
    pipes = [Pipe(random.randint(100, LEVEL_END_X-100), HEIGHT-120, 60, 70) for _ in range(3)]
    flag = Flag(LEVEL_END_X+35, HEIGHT-50)
    mom = Mom(random.randint(680, 1600), HEIGHT-110)
    slippers = []
    return platforms, enemies, friends, coins, pipes, flag, mom, slippers

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    current_level = 0
    max_level = 2

    # Init all level-scoped variables at main scope
    platforms, enemies, friends, coins, pipes, flag, mom, slippers = build_level(current_level)

    coinworld_entry_pipe = None
    coinworld_exit_pipe = None
    last_mainworld_pos = None

    def enter_coin_world(from_pipe):
        nonlocal state, coinworld_entry_pipe, coinworld_exit_pipe
        nonlocal coinworld_platforms, coinworld_coins, coinworld_enemies, last_mainworld_pos
    
        # Save where we exited
        last_mainworld_pos = player.rect.topleft
        state = COIN_WORLD_STATE
        coinworld_entry_pipe = from_pipe
    
        # Place player atop entrance
        player.rect.x = 100
        player.rect.y = HEIGHT - 200
    
        # Design platforms for coinworld
        coinworld_platforms = [
            Platform(0, HEIGHT-50, 600, 50),
            Platform(200, HEIGHT-180, 120, 20),
            Platform(410, HEIGHT-300, 120, 20),
            Platform(480, HEIGHT-390, 100, 20)
        ]
        # Place coins
        coinworld_coins = [
            Coin(100, HEIGHT-180), Coin(260, HEIGHT-200), Coin(350, HEIGHT-275),
            Coin(500, HEIGHT-375)
        ]
        # Add a simple enemy for challenge
        coinworld_enemies = [Enemy(220, HEIGHT-214, coinworld_platforms[1].rect)]
        # Add the exit pipe (on right side)
        coinworld_exit_pipe = Pipe(520, HEIGHT-120, 60, 70)


    player = Player()
    score = 0
    camera_x = 0

    # --- Volume control state ---
    volume_level = 3  # 0 to 10, syncs to mixer volume (0.0 to 1.0)
    volume_change_tick = 0
    last_volume_text = ""
    volume_display_timer = 0  # frames to show "Volume: X/10"
    VOLUME_COOLDOWN = 10  # frames before allowing the next volume change
    running = True
    state = "START"
    COIN_WORLD_STATE = "COIN_WORLD"
    coinworld_entry_pipe = None  # Remember from which pipe we entered
    # --- Coin World Entities ---
    coinworld_platforms = []
    coinworld_coins = []
    coinworld_enemies = []
    coinworld_exit_pipe = None

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
                slippers.clear()
                mom.throw_timer = 0
                mom.shout_frames = 0
                state = "PLAY"
                score = 0
            clock.tick(FPS)
            continue
        if state == COIN_WORLD_STATE:
            player.move(coinworld_platforms)
            for enemy in coinworld_enemies:
                enemy.move(coinworld_platforms)
            for e in coinworld_enemies[:]:
                if player.rect.colliderect(e.rect):
                    state = "GAMEOVER"
                    break
            for coin in coinworld_coins[:]:
                if player.rect.colliderect(coin.rect):
                    coinworld_coins.remove(coin)
                    score += 1
            # Collide with exit pipe to return to main world
            if player.rect.colliderect(coinworld_exit_pipe.rect):
                # place player back atop the originating pipe
                player.rect.topleft = (
                    coinworld_entry_pipe.rect.x + (coinworld_entry_pipe.rect.w - player.rect.w)//2,
                    coinworld_entry_pipe.rect.top - player.rect.h
                )
                state = "PLAY"
        
            # Draw coinworld scene
            screen.fill((56, 56, 92))
            for p in coinworld_platforms:
                p.draw(screen, 0)
            for e in coinworld_enemies:
                e.draw(screen, 0)
            for c in coinworld_coins:
                c.draw(screen, 0)
            coinworld_exit_pipe.draw(screen, 0)
            player.draw(screen, 0)
            # Score in corner
            font = pygame.font.Font(None, 36)
            text = font.render(f'Score: {score}', True, GOLDEN)
            screen.blit(text, (10, 10))
            # Show Exit Pipe Label
            exit_label = pygame.font.Font(None, 30).render("Exit", True, WHITE, None)
            screen.blit(exit_label, (coinworld_exit_pipe.rect.x + 10, coinworld_exit_pipe.rect.y - 25))
        
            pygame.display.flip()
            clock.tick(FPS)
            continue
        if state == "COMPLETE":
            screen.fill(BLACK)
            msg = pygame.font.Font(None, 64).render("Level Complete!", True, YELLOW)
            score_display = pygame.font.Font(None, 36).render(f"Final Score: {score}", True, GOLDEN)
            prompt_next = pygame.font.Font(None, 36).render("Press ENTER for Next Level", True, WHITE)
            prompt_restart = pygame.font.Font(None, 28).render("Press SPACE to Restart Current Level", True, WHITE)
            screen.blit(msg, ((WIDTH-msg.get_width())//2, HEIGHT//2-90))
            screen.blit(score_display, ((WIDTH-score_display.get_width())//2, HEIGHT//2-24))
            screen.blit(prompt_next, ((WIDTH-prompt_next.get_width())//2, HEIGHT//2+40))
            screen.blit(prompt_restart, ((WIDTH-prompt_restart.get_width())//2, HEIGHT//2+90))
            pygame.display.flip()
            if keys[pygame.K_RETURN]:
                if current_level + 1 < max_level:
                    current_level += 1
                else:
                    current_level = 0
                player.__init__()
                platforms, enemies, friends, coins, pipes, flag, mom, slippers = build_level(current_level)
                state = "PLAY"
            elif keys[pygame.K_SPACE]:
                player.__init__()
                platforms, enemies, friends, coins, pipes, flag, mom, slippers = build_level(current_level)
                state = "PLAY"
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
                if player.invincible:
                    remove_enemies.append(i)
                    score += 100
                elif player.vy > 0 and player.rect.bottom - enemy.rect.top < 24 and player.rect.top < enemy.rect.top:
                    remove_enemies.append(i)
                    player.vy = JUMP_HEIGHT // 2
                    stomped = True
                    score += 100
                else:
                    state = "GAMEOVER"
                    break
        for idx in sorted(remove_enemies, reverse=True):
            del enemies[idx]
        for friend in friends:
            if friend.active and player.rect.colliderect(friend.rect):
                friend.apply_power(player)
        for coin in coins[:]:
            if player.rect.colliderect(coin.rect):
                coins.remove(coin)
                if player.coin_bonus:
                    score += 2
                else:
                    score += 1
        for pipe in pipes:
            if player.rect.colliderect(pipe.rect):
                if player.rect.bottom > pipe.rect.top and player.vy >= 0:
                    player.rect.bottom = pipe.rect.top
                    player.vy = 0
                    player.on_ground = True
                    # (NEW) Enter the pipe if DOWN key is pressed
                    if keys[pygame.K_DOWN] and player.rect.bottom == pipe.rect.top:
                        enter_coin_world(pipe)  # Call your coinworld function

        # Mom throwing slippers in all directions (enemy)
        if mom.update():
            angle = random.uniform(-1.4, 1.4)
            speed = random.randint(8,13)
            vx = int(speed * -1 * (random.uniform(0.6, 1.2)) * random.choice([-1,1]))
            vy = int(-7 * (random.uniform(0.2, 1.2)) * random.choice([-1,1]))
            slippers.append(Slipper(mom.x + 16, mom.y-30, vx, vy))
        mom.tick_shout()

        for slipper in slippers[:]:
            slipper.move()
            if player.rect.colliderect(slipper.rect):
                if not player.invincible:
                    state = "GAMEOVER"
            if (slipper.rect.right < 0 or slipper.rect.left > LEVEL_END_X+200 or
                slipper.rect.top > HEIGHT or slipper.rect.bottom < 0):
                slippers.remove(slipper)

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
        for friend in friends:
            if friend.active:
                friend.draw(screen, camera_x)
        for coin in coins:
            coin.draw(screen, camera_x)
        mom.draw(screen, camera_x)
        for slipper in slippers:
            slipper.draw(screen, camera_x)
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
