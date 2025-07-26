import pygame
import sys
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Load music files
try:
    pygame.mixer.music.load("bgm.mp3")
    MUSIC_AVAILABLE = True
except pygame.error:
    print("Music file not found, continuing without music")
    MUSIC_AVAILABLE = False

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

LEVEL_END_X = 2000  # Extended world width for longer and more challenging levels

# Sound effects (using NumPy for high-quality sound generation)
def create_sound_effect(frequency, duration, volume=0.5):
    """Create a high-quality sound effect using NumPy"""
    if not MUSIC_AVAILABLE:
        return None
    try:
        import numpy as np
        import pygame.sndarray
        
        sample_rate = 22050
        frames = int(duration * sample_rate)
        
        # Create time array
        t = np.linspace(0, duration, frames, False)
        
        # Generate waveform - using a mix of sine and square for more interesting sounds
        fundamental = np.sin(2 * np.pi * frequency * t)
        harmonics = 0.3 * np.sin(2 * np.pi * frequency * 2 * t)  # Second harmonic
        square_component = 0.2 * np.sign(np.sin(2 * np.pi * frequency * t))  # Square wave component
        
        wave = fundamental + harmonics + square_component
        
        # Apply envelope (exponential decay for more realistic sound)
        envelope = np.exp(-t * 4)  # Exponential decay
        wave = wave * envelope * volume
        
        # Normalize and convert to 16-bit range
        wave = np.clip(wave, -1.0, 1.0)
        wave = (wave * 32767).astype(np.int16)
        
        # Convert to stereo
        stereo_wave = np.column_stack((wave, wave))
        
        sound = pygame.sndarray.make_sound(stereo_wave)
        return sound
        
    except ImportError as e:
        print(f"Could not import required modules for sound: {e}")
        return None
    except Exception as e:
        print(f"Could not create sound effect: {e}")
        return None

# Create sound effects with better parameters
JUMP_SOUND = create_sound_effect(600, 0.15, 0.4)  # Higher pitch, longer duration
COIN_SOUND = create_sound_effect(1200, 0.15, 0.4)
ENEMY_DEFEAT_SOUND = create_sound_effect(300, 0.3, 0.4)  # Lower pitch, longer duration
STOMP_SOUND = create_sound_effect(200, 0.2, 0.5)  # Deep stomp sound
BOSS_HIT_SOUND = create_sound_effect(600, 0.3, 0.5)
GAME_OVER_SOUND = create_sound_effect(200, 0.5, 0.4)
LEVEL_COMPLETE_SOUND = create_sound_effect(1000, 0.4, 0.5)

def play_sound(sound):
    """Play a sound effect if available"""
    if sound and MUSIC_AVAILABLE:
        try:
            if hasattr(sound, 'play'):
                sound.play()
            else:
                print("♪ Sound effect (no play method)")
        except Exception as e:
            print(f"Could not play sound: {e}")
    elif sound:
        # Handle fallback sound descriptions if they exist
        if isinstance(sound, dict) and sound.get('type') == 'sound_effect':
            freq = sound['frequency']
            if freq >= 1000:
                print("♪ *DING*")
            elif freq >= 500:
                print("♪ *BOING*")
            elif freq >= 300:
                print("♪ *THUMP*")
            else:
                print("♪ *BOOM*")
        else:
            print("♪ Sound effect played (fallback)")
    else:
        print("♪ No sound to play")

def start_background_music():
    """Start playing background music"""
    if MUSIC_AVAILABLE:
        try:
            pygame.mixer.music.play(-1, 0.0)  # Loop indefinitely
            pygame.mixer.music.set_volume(0.15)  # Reduced from 0.3 to 0.15 (50% quieter)
        except:
            pass

def stop_background_music():
    """Stop background music"""
    if MUSIC_AVAILABLE:
        try:
            pygame.mixer.music.stop()
        except:
            pass

def set_music_volume(volume):
    """Set music volume (0.0 to 1.0)"""
    if MUSIC_AVAILABLE:
        try:
            pygame.mixer.music.set_volume(volume)
        except:
            pass

class Slipper:
    def __init__(self, x, y, target_x=None, target_y=None, speed=6):
        self.rect = pygame.Rect(x, y, 20, 15)
        self.speed = speed
        if target_x is not None and target_y is not None:
            # Calculate direction towards target
            dx = target_x - x
            dy = target_y - y
            length = (dx**2 + dy**2)**0.5
            if length > 0:
                self.vx = (dx / length) * speed
                self.vy = (dy / length) * speed
            else:
                self.vx = speed
                self.vy = 0
        else:
            # Random direction for stage 1
            import random
            angle = random.uniform(0, 2 * 3.14159)
            self.vx = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            self.vy = speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Remove if off screen (using world coordinates, not screen coordinates)
        should_remove = (self.rect.x < -200 or self.rect.x > LEVEL_END_X + 300 or 
                        self.rect.y < -200 or self.rect.y > HEIGHT + 200)
        return should_remove

    def draw(self, surf, camera_x):
        # Draw a realistic slipper shape
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y
        
        # Only draw if on screen
        if screen_x > -100 and screen_x < WIDTH + 100 and screen_y > -100 and screen_y < HEIGHT + 100:
            # Draw slipper base (main sole)
            pygame.draw.ellipse(surf, (139, 69, 19), (int(screen_x), int(screen_y + 8), 20, 12))  # Brown sole
            # Draw slipper top (fabric part)
            pygame.draw.ellipse(surf, (180, 100, 60), (int(screen_x + 2), int(screen_y + 3), 16, 10))  # Lighter brown fabric
            # Draw heel part
            pygame.draw.ellipse(surf, (120, 60, 30), (int(screen_x + 1), int(screen_y + 12), 6, 6))  # Dark heel
            # Draw toe part highlight
            pygame.draw.ellipse(surf, (200, 120, 80), (int(screen_x + 12), int(screen_y + 5), 6, 6))  # Toe highlight

class Boss:
    def __init__(self, x, y, level=1):
        self.rect = pygame.Rect(x, y, 80, 80)
        self.health = 3  # Three stages
        self.stage = 1
        self.level = level  # Boss level (increases every 5 game levels)
        self.speed = 1.5 + (level - 1) * 0.3  # Slower movement, less speed increase per level
        self.direction = 1
        self.slipper_timer = 0
        self.slipper_cooldown = max(90 - (level - 1) * 8, 50)  # Slower slipper throwing, longer cooldown
        self.move_timer = 0
        self.move_duration = 180  # Moves for longer periods (more predictable)
        self.slippers = []
        self.hit_invulnerable = 0  # Invulnerability frames after being hit
        self.shout_frames = 0  # Frames to show "AHAAAAN!!" yelling

    def update(self, player):
        if self.hit_invulnerable > 0:
            self.hit_invulnerable -= 1
            
        # Update shout timer
        if self.shout_frames > 0:
            self.shout_frames -= 1

        # Stage-specific behavior
        if self.stage == 1:
            # Stage 1: Stationary, throws slippers in all directions
            self.slipper_timer += 1
            if self.slipper_timer >= self.slipper_cooldown:
                self.throw_random_slippers()
                self.slipper_timer = 0
                # Mom yells when throwing slippers
                self.shout_frames = 30  # Show "AHAAAAN!!" for 30 frames

        elif self.stage == 2:
            # Stage 2: Stationary, throws targeted slippers
            self.slipper_timer += 1
            if self.slipper_timer >= int(self.slipper_cooldown * 0.8):  # Slightly faster than stage 1, but not too fast
                self.throw_targeted_slipper(player)
                self.slipper_timer = 0
                # Mom yells when throwing slippers
                self.shout_frames = 30  # Show "AHAAAAN!!" for 30 frames

        elif self.stage == 3:
            # Stage 3: Moves around and throws targeted slippers
            self.move_timer += 1
            if self.move_timer >= self.move_duration:
                self.direction *= -1
                self.move_timer = 0

            # Move horizontally
            self.rect.x += self.speed * self.direction
            if self.rect.left <= 200:
                self.rect.left = 200
                self.direction = 1
            elif self.rect.right >= LEVEL_END_X - 200:
                self.rect.right = LEVEL_END_X - 200
                self.direction = -1

            # Throw slippers
            self.slipper_timer += 1
            if self.slipper_timer >= int(self.slipper_cooldown * 0.6):  # Faster than stage 2, but not overwhelming
                self.throw_targeted_slipper(player)
                self.slipper_timer = 0
                # Mom yells when throwing slippers
                self.shout_frames = 30  # Show "AHAAAAN!!" for 30 frames

        # Update slippers
        self.slippers = [s for s in self.slippers if not s.update()]

    def throw_random_slippers(self):
        # Throw 3-4 slippers in different directions (reduced from 4-6)
        import random
        num_slippers = random.randint(3, 4)
        for _ in range(num_slippers):
            slipper = Slipper(self.rect.centerx, self.rect.centery, None, None, 3 + self.level * 0.5)  # Slower slippers
            self.slippers.append(slipper)

    def throw_targeted_slipper(self, player):
        # Throw slipper towards player (slower speed)
        slipper = Slipper(self.rect.centerx, self.rect.centery, 
                         player.rect.centerx, player.rect.centery, speed=4 + self.level * 0.5)  # Slower targeted slippers
        self.slippers.append(slipper)

    def take_damage(self):
        if self.hit_invulnerable <= 0:
            self.health -= 1
            self.stage += 1
            self.hit_invulnerable = 180  # 3 seconds of invulnerability (increased from 2 seconds)
            return True
        return False

    def is_defeated(self):
        return self.health <= 0

    def draw(self, surf, camera_x):
        # Flash when invulnerable
        if self.hit_invulnerable > 0 and self.hit_invulnerable % 10 < 5:
            return

        # Draw boss (mom)
        # Body
        pygame.draw.ellipse(surf, (255, 182, 193), (self.rect.x - camera_x, self.rect.y + 30, self.rect.w, self.rect.h - 30))
        # Head
        pygame.draw.ellipse(surf, SKIN, (self.rect.x + 15 - camera_x, self.rect.y, self.rect.w - 30, 40))
        # Hair
        pygame.draw.ellipse(surf, BROWN, (self.rect.x + 10 - camera_x, self.rect.y - 5, self.rect.w - 20, 25))
        # Eyes
        pygame.draw.ellipse(surf, BLACK, (self.rect.x + 25 - camera_x, self.rect.y + 15, 8, 8))
        pygame.draw.ellipse(surf, BLACK, (self.rect.x + 45 - camera_x, self.rect.y + 15, 8, 8))
        # Angry mouth
        pygame.draw.arc(surf, BLACK, (self.rect.x + 30 - camera_x, self.rect.y + 25, 20, 10), 0, 3.14, 3)

        # Draw "AHAAAAN!!" yelling bubble if mom is shouting
        if self.shout_frames > 0:
            font = pygame.font.Font(None, 30)
            shout = font.render("AHAAAAN!!", True, YELLOW, BLACK)
            surf.blit(shout, (self.rect.x - camera_x + 10, self.rect.y - 30))

        # Draw health indicator
        for i in range(self.health):
            pygame.draw.circle(surf, RED, (self.rect.x - camera_x + 10 + i * 25, self.rect.y - 15), 8)

        # Draw slippers
        for slipper in self.slippers:
            slipper.draw(surf, camera_x)

class Mom:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y-60, 46, 60)
        self.throw_timer = 0
        self.shout_frames = 0
        self.slippers = []
        
    def update(self):
        import random
        self.throw_timer += 1
        # Update shout timer
        if self.shout_frames > 0:
            self.shout_frames -= 1
        
        # Throw slippers randomly
        if self.throw_timer > random.randint(180, 300):  # Every 3-5 seconds (more reasonable pace)
            self.throw_timer = 0
            self.shout_frames = 30  # Show "AHAAAAN!!" for 30 frames
            # Throw multiple slippers in different directions
            num_slippers = random.randint(3, 5)  # Throw 3-5 slippers
            for _ in range(num_slippers):
                # Create slipper with random direction (no target_x, target_y)
                slipper = Slipper(self.x + 16, self.y - 30, None, None, random.randint(4, 8))  # Slightly slower slippers
                self.slippers.append(slipper)
            
        # Update slippers
        self.slippers = [s for s in self.slippers if not s.update()]
        
    def draw(self, surf, camera_x):
        # Draw mom
        pygame.draw.ellipse(surf, (255, 182, 193), (self.x - camera_x, self.y - 25, 46, 48))  # Saree
        pygame.draw.ellipse(surf, SKIN, (self.x + 7 - camera_x, self.y - 60, 32, 32))  # Head
        pygame.draw.ellipse(surf, BLACK, (self.x + 15 - camera_x, self.y - 47, 6, 10))  # Left eye
        pygame.draw.ellipse(surf, BLACK, (self.x + 27 - camera_x, self.y - 47, 6, 10))  # Right eye
        pygame.draw.circle(surf, BLACK, (self.x + 23 - camera_x, self.y - 63), 8)  # Hair
        pygame.draw.arc(surf, BLACK, (self.x + 15 - camera_x, self.y - 37, 16, 8), 3.5, 6.0, 2)  # Angry mouth
        
        # Draw "AHAAAAN!!" yelling bubble if mom is shouting
        if self.shout_frames > 0:
            font = pygame.font.Font(None, 30)
            shout = font.render("AHAAAAN!!", True, YELLOW, BLACK)
            surf.blit(shout, (self.x - camera_x + 10, self.y - 82))
            
        # Draw slippers
        for slipper in self.slippers:
            slipper.draw(surf, camera_x)

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

    def move(self, platforms):
        # Update power-up timers
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
            
        keys = pygame.key.get_pressed()
        dx = 0
        current_speed = self.base_speed + self.speed_boost
        
        if keys[pygame.K_LEFT]:
            dx -= current_speed
        if keys[pygame.K_RIGHT]:
            dx += current_speed

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
            current_jump = self.base_jump + self.jump_boost
            self.vy = current_jump
            self.on_ground = False
            play_sound(JUMP_SOUND)

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
    
    def apply_powerup(self, power_type):
        if power_type == 'speed':
            self.speed_boost = 3  # +3 speed
            self.speed_timer = 600  # 10 seconds at 60 FPS
        elif power_type == 'jump':
            self.jump_boost = -8  # Higher jump (more negative = higher)
            self.jump_timer = 600  # 10 seconds at 60 FPS
        elif power_type == 'life':
            self.lives += 1
    
    def die(self):
        if self.lives > 1:
            self.lives -= 1
            self.immunity_timer = 180  # 3 seconds of immunity
            return False  # Not game over
        else:
            return True  # Game over
    
    def is_immune(self):
        return self.immunity_timer > 0

    def draw(self, surf, camera_x):
        # Flash when immune
        if self.is_immune() and self.immunity_timer % 10 < 5:
            return  # Skip drawing to create flashing effect
        
        # Enhanced Ahaanio character design
        x = self.rect.x - camera_x
        y = self.rect.y
        
        # Body (red shirt with better shading)
        pygame.draw.ellipse(surf, RED, (x, y+10, self.rect.w, self.rect.h-10))
        pygame.draw.ellipse(surf, (180, 45, 60), (x+5, y+12, self.rect.w-10, self.rect.h-15))  # Shirt highlight
        
        # Overalls/pants (blue with details)
        pygame.draw.ellipse(surf, BLUE, (x+10, y+25, self.rect.w-20, self.rect.h//2))
        pygame.draw.rect(surf, (0, 100, 200), (x+15, y+28, 4, 15))  # Overall strap left
        pygame.draw.rect(surf, (0, 100, 200), (x+31, y+28, 4, 15))  # Overall strap right
        
        # Head (better skin tone and shading)
        pygame.draw.ellipse(surf, SKIN, (x+10, y+5, self.rect.w-20, self.rect.h//2))
        pygame.draw.ellipse(surf, (240, 200, 160), (x+12, y+7, self.rect.w-24, self.rect.h//2-4))  # Face highlight
        
        # Hair (more detailed)
        pygame.draw.ellipse(surf, BROWN, (x+5, y, self.rect.w-10, 20))
        pygame.draw.circle(surf, (120, 80, 40), (x+12, y+5), 8)  # Hair tuft left
        pygame.draw.circle(surf, (120, 80, 40), (x+38, y+5), 8)  # Hair tuft right
        
        # Eyes (more expressive)
        pygame.draw.ellipse(surf, WHITE, (x+16, y+15, 8, 10))  # Left eye white
        pygame.draw.ellipse(surf, WHITE, (x+26, y+15, 8, 10))  # Right eye white
        pygame.draw.circle(surf, BLACK, (x+19, y+19), 3)  # Left pupil
        pygame.draw.circle(surf, BLACK, (x+29, y+19), 3)  # Right pupil
        pygame.draw.circle(surf, WHITE, (x+20, y+18), 1)  # Left eye shine
        pygame.draw.circle(surf, WHITE, (x+30, y+18), 1)  # Right eye shine
        
        # Nose
        pygame.draw.circle(surf, (220, 180, 140), (x+25, y+22), 2)
        
        # Mouth (happy expression)
        pygame.draw.arc(surf, BLACK, (x+18, y+25, 14, 8), 0, 3.14, 2)
        
        # Mustache (Mario-style)
        pygame.draw.ellipse(surf, BROWN, (x+16, y+23, 18, 4))

class Enemy:
    def __init__(self, x, y, enemy_type="homework", plat_rect=None):
        self.rect = pygame.Rect(x, y, 34, 34)
        self.speed = 2
        self.direction = 1
        # If plat_rect is not provided, create a default platform area
        if plat_rect is None:
            self.platform = pygame.Rect(x - 50, y, 134, 34)  # Default platform area
        else:
            self.platform = plat_rect
        self.enemy_type = enemy_type  # "homework", "chores", "badminton", "shower"

    def move(self, platforms):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= self.platform.left:
            self.rect.left = self.platform.left
            self.direction = 1
        if self.rect.right >= self.platform.right:
            self.rect.right = self.platform.right
            self.direction = -1

    def draw(self, surf, camera_x):
        x = self.rect.x - camera_x
        y = self.rect.y
        w = self.rect.w
        h = self.rect.h
        
        if self.enemy_type == "homework":
            # Enhanced homework book with more detail
            # Book cover (brown with gradient)
            pygame.draw.rect(surf, BROWN, (x, y, w, h))
            pygame.draw.rect(surf, (180, 120, 70), (x+2, y+2, w-4, h-4))  # Inner cover
            
            # Book pages (white with lines)
            pygame.draw.rect(surf, WHITE, (x+3, y+3, w-6, h-6))
            # Ruled lines
            for i in range(4):
                line_y = y + 8 + i * 6
                pygame.draw.line(surf, (200, 200, 255), (x+5, line_y), (x+w-5, line_y), 1)
            
            # Book spine
            pygame.draw.rect(surf, (100, 60, 30), (x, y, 3, h))
            
            # Title on cover
            pygame.draw.rect(surf, BLACK, (x+6, y+6, w-12, 4))
            
        elif self.enemy_type == "chores":
            # Enhanced broom with more detail
            # Broom handle (wood grain effect)
            pygame.draw.rect(surf, BROWN, (x+12, y, 8, 20))
            pygame.draw.rect(surf, (160, 120, 80), (x+13, y, 6, 20))  # Wood highlight
            # Wood grain lines
            for i in range(y, y+20, 3):
                pygame.draw.line(surf, (120, 80, 40), (x+13, i), (x+18, i), 1)
            
            # Broom head (bristles)
            pygame.draw.ellipse(surf, YELLOW, (x+5, y+18, 22, 14))
            pygame.draw.ellipse(surf, (255, 255, 150), (x+7, y+20, 18, 10))  # Bristle highlight
            
            # Individual bristle details
            for i in range(6):
                bristle_x = x + 8 + i * 3
                pygame.draw.line(surf, (200, 180, 100), (bristle_x, y+22), (bristle_x, y+30), 1)
            
        elif self.enemy_type == "badminton":
            # Enhanced badminton racket
            # Racket frame
            pygame.draw.ellipse(surf, RED, (x+8, y, 18, 22))
            pygame.draw.ellipse(surf, (255, 100, 100), (x+10, y+2, 14, 18))  # Inner frame
            
            # Handle with grip
            pygame.draw.rect(surf, BROWN, (x+15, y+15, 4, 17))
            pygame.draw.rect(surf, (160, 120, 80), (x+15, y+15, 4, 17))
            # Grip texture
            for i in range(y+16, y+30, 2):
                pygame.draw.line(surf, (100, 70, 40), (x+15, i), (x+18, i), 1)
            
            # Racket strings (crossing pattern)
            for i in range(3):
                string_x = x + 12 + i * 3
                pygame.draw.line(surf, WHITE, (string_x, y+4), (string_x, y+18), 1)
            for i in range(4):
                string_y = y + 5 + i * 3
                pygame.draw.line(surf, WHITE, (x+10, string_y), (x+24, string_y), 1)
                
        elif self.enemy_type == "shower":
            # Enhanced shower head
            # Shower head body (metallic look)
            pygame.draw.rect(surf, (180, 180, 180), (x+5, y+5, 24, 15))
            pygame.draw.rect(surf, (220, 220, 220), (x+6, y+6, 22, 13))  # Metallic highlight
            pygame.draw.rect(surf, (140, 140, 140), (x+26, y+6, 2, 13))   # Shadow edge
            
            # Shower holes
            for i in range(3):
                for j in range(6):
                    hole_x = x + 8 + j * 3
                    hole_y = y + 8 + i * 3
                    pygame.draw.circle(surf, (100, 100, 100), (hole_x, hole_y), 1)
            
            # Water drops (animated)
            import random
            for i in range(6):
                drop_x = x + 8 + i * 3
                drop_y = y + 22 + random.randint(0, 8)  # Animated falling
                # Water drop shape
                pygame.draw.circle(surf, BLUE, (drop_x, drop_y), 2)
                pygame.draw.circle(surf, (150, 200, 255), (drop_x-1, drop_y-1), 1)  # Highlight
                
        else:
            # Enhanced default enemy with better shading
            # Body (shirt)
            pygame.draw.ellipse(surf, BROWN, (x, y, w, h//2+6))
            pygame.draw.ellipse(surf, (180, 120, 70), (x+2, y+2, w-4, h//2+2))  # Shirt highlight
            
            # Head
            pygame.draw.ellipse(surf, SKIN, (x+5, y+h//2-4, w-10, h//2-2))
            pygame.draw.ellipse(surf, (240, 200, 160), (x+7, y+h//2-2, w-14, h//2-6))  # Face highlight
            
            # Eyes with pupils
            pygame.draw.ellipse(surf, WHITE, (x+11, y+13, 7, 9))  # Left eye white
            pygame.draw.ellipse(surf, WHITE, (x+20, y+13, 7, 9))  # Right eye white
            pygame.draw.circle(surf, BLACK, (x+14, y+16), 2)     # Left pupil
            pygame.draw.circle(surf, BLACK, (x+23, y+16), 2)     # Right pupil

class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
    def draw(self, surf, camera_x):
        # Enhanced platform with brick texture and 3D effect
        x = self.rect.x - camera_x
        y = self.rect.y
        w = self.rect.w
        h = self.rect.h
        
        # Main platform body (darker blue)
        pygame.draw.rect(surf, (0, 100, 180), (x+8, y, w-16, h), border_radius=9)
        
        # Brick pattern
        brick_width = 24
        brick_height = 8
        for row in range(0, h, brick_height):
            for col in range(0, w-16, brick_width):
                # Alternate brick offset for realistic pattern
                offset = (brick_width // 2) if (row // brick_height) % 2 else 0
                brick_x = x + 8 + col + offset
                brick_y = y + row
                
                if brick_x + brick_width <= x + w - 8:  # Don't draw outside platform
                    # Brick body
                    pygame.draw.rect(surf, BLUE, (brick_x, brick_y, brick_width-2, brick_height-1))
                    # Brick highlight (3D effect)
                    pygame.draw.line(surf, (100, 150, 255), (brick_x, brick_y), (brick_x + brick_width-2, brick_y))
                    pygame.draw.line(surf, (100, 150, 255), (brick_x, brick_y), (brick_x, brick_y + brick_height-1))
                    # Brick shadow
                    pygame.draw.line(surf, (0, 80, 160), (brick_x + brick_width-2, brick_y), (brick_x + brick_width-2, brick_y + brick_height-1))
                    pygame.draw.line(surf, (0, 80, 160), (brick_x, brick_y + brick_height-1), (brick_x + brick_width-2, brick_y + brick_height-1))
        
        # Rounded end caps with 3D shading
        # Left cap
        pygame.draw.ellipse(surf, BLUE, (x, y, 16, h))
        pygame.draw.ellipse(surf, (100, 150, 255), (x+2, y+1, 12, h-2))  # Highlight
        
        # Right cap  
        pygame.draw.ellipse(surf, BLUE, (x+w-16, y, 16, h))
        pygame.draw.ellipse(surf, (0, 80, 160), (x+w-14, y+1, 12, h-2))  # Shadow

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.rotation = 0  # For spinning animation
    def draw(self, surf, camera_x):
        # Animated spinning coin with 3D effect
        self.rotation += 3  # Spin speed
        
        x = self.rect.x + 10 - camera_x
        y = self.rect.y + 10
        
        # Create spinning effect by varying the ellipse width
        import math
        spin_width = int(10 * abs(math.cos(self.rotation * 0.1)))
        
        # Coin shadow
        pygame.draw.ellipse(surf, (180, 150, 30), (x-11, y-9, spin_width + 2, 18))
        
        # Main coin body
        pygame.draw.ellipse(surf, GOLDEN, (x-10, y-10, spin_width, 20))
        
        # Coin highlight (3D effect)
        if spin_width > 3:
            pygame.draw.ellipse(surf, (255, 240, 100), (x-8, y-8, max(1, spin_width-4), 16))
        
        # Inner detail (dollar sign or star when face-on)
        if spin_width > 6:
            # Draw a star when coin is facing forward
            star_points = []
            for i in range(5):
                angle = i * 2 * math.pi / 5 - math.pi/2
                star_x = x + 3 * math.cos(angle)
                star_y = y + 3 * math.sin(angle)
                star_points.append((star_x, star_y))
            if len(star_points) >= 3:
                pygame.draw.polygon(surf, (200, 160, 20), star_points)

class Pipe:
    def __init__(self, x, y, width=50, height=70, is_warp_pipe=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_warp_pipe = is_warp_pipe
        self.warp_timer = 0  # For animation when player can enter
        
    def draw(self, surf, camera_x):
        # Enhanced pipe with better 3D effect and textures
        x = self.rect.x - camera_x
        y = self.rect.y
        w = self.rect.w
        h = self.rect.h
        
        # Base pipe color - special glow for warp pipes
        base_color = PIPE_GREEN
        rim_color = PIPE_GREEN
        highlight_color = (40, 180, 80)
        shadow_color = (0, 100, 40)
        
        if self.is_warp_pipe:
            # Magical glowing effect for warp pipes
            import math
            glow_intensity = int(50 + 30 * math.sin(self.warp_timer * 0.1))
            base_color = (0, 140 + glow_intensity//2, 51 + glow_intensity//3)
            rim_color = (0 + glow_intensity//4, 140 + glow_intensity//2, 51 + glow_intensity//2)
            highlight_color = (40 + glow_intensity//3, 180 + glow_intensity//4, 80 + glow_intensity//3)
            shadow_color = (0, 100 + glow_intensity//6, 40 + glow_intensity//4)
            self.warp_timer += 1
        
        # Main pipe body with 3D shading
        pygame.draw.rect(surf, base_color, (x, y+15, w, h-15))
        # Highlight on left side
        pygame.draw.rect(surf, highlight_color, (x, y+15, 8, h-15))
        # Shadow on right side
        pygame.draw.rect(surf, shadow_color, (x+w-8, y+15, 8, h-15))
        
        # Pipe rim (3D ellipse effect)
        pygame.draw.ellipse(surf, rim_color, (x-8, y, w+16, 28))
        # Rim highlight
        pygame.draw.ellipse(surf, highlight_color, (x-6, y+2, w+12, 24), 3)
        # Rim shadow
        pygame.draw.ellipse(surf, shadow_color, (x-6, y+4, w+12, 20), 2)
        
        # Inner pipe detail
        pygame.draw.rect(surf, highlight_color, (x+9, y+25, 8, h-31))
        # Inner pipe shadow
        pygame.draw.rect(surf, shadow_color, (x+w-17, y+25, 8, h-31))
        
        # Pipe segments (horizontal lines for texture)
        for i in range(y+30, y+h-10, 12):
            pygame.draw.line(surf, shadow_color, (x+3, i), (x+w-3, i), 1)
            pygame.draw.line(surf, highlight_color, (x+3, i+1), (x+w-3, i+1), 1)
        
        # Draw magical sparkles for warp pipes
        if self.is_warp_pipe:
            import random
            for i in range(5):  # More sparkles
                if random.randint(1, 8) == 1:  # More frequent sparkles
                    sparkle_x = x + random.randint(5, w-5)
                    sparkle_y = y + random.randint(10, h-10)
                    # Multi-colored sparkles
                    sparkle_colors = [YELLOW, WHITE, (255, 200, 255), (200, 255, 255)]
                    color = random.choice(sparkle_colors)
                    pygame.draw.circle(surf, color, (sparkle_x, sparkle_y), 3)
                    pygame.draw.circle(surf, WHITE, (sparkle_x, sparkle_y), 1)

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

class PowerUp:
    def __init__(self, x, y, power_type):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.power_type = power_type  # 'speed', 'jump', 'life', 'nintendo', 'drums', 'soccer'
        self.collected = False
        self.float_timer = 0
        self.original_y = y
        
    def update(self):
        # Floating animation
        self.float_timer += 0.1
        self.rect.y = self.original_y + int(3 * pygame.math.Vector2(0, 1).rotate(self.float_timer * 10).y)
        
    def draw(self, surf, camera_x):
        if self.collected:
            return
            
        if self.power_type == 'speed':
            # Draw pizza slice (speed boost - favorite Italian food)
            # Crust
            pygame.draw.polygon(surf, (255, 206, 84), [
                (self.rect.x - camera_x + 2, self.rect.y + 20),
                (self.rect.x - camera_x + 23, self.rect.y + 20),
                (self.rect.x - camera_x + 12, self.rect.y + 2)
            ])
            # Cheese
            pygame.draw.polygon(surf, (255, 255, 153), [
                (self.rect.x - camera_x + 4, self.rect.y + 18),
                (self.rect.x - camera_x + 21, self.rect.y + 18),
                (self.rect.x - camera_x + 12, self.rect.y + 4)
            ])
            # Pepperoni
            pygame.draw.circle(surf, (139, 0, 0), (self.rect.x - camera_x + 10, self.rect.y + 12), 2)
            pygame.draw.circle(surf, (139, 0, 0), (self.rect.x - camera_x + 16, self.rect.y + 15), 2)
            
        elif self.power_type == 'jump':
            # Draw donut (jump boost)
            # Outer circle
            pygame.draw.circle(surf, (139, 69, 19), (self.rect.x - camera_x + 12, self.rect.y + 12), 11)
            # Inner hole
            pygame.draw.circle(surf, (92, 192, 255), (self.rect.x - camera_x + 12, self.rect.y + 12), 5)
            # Glaze
            pygame.draw.circle(surf, (255, 182, 193), (self.rect.x - camera_x + 12, self.rect.y + 12), 9, 2)
            # Sprinkles
            pygame.draw.rect(surf, RED, (self.rect.x - camera_x + 8, self.rect.y + 8, 2, 6))
            pygame.draw.rect(surf, GREEN, (self.rect.x - camera_x + 15, self.rect.y + 10, 6, 2))
            pygame.draw.rect(surf, BLUE, (self.rect.x - camera_x + 10, self.rect.y + 15, 2, 4))
            
        elif self.power_type == 'life':
            # Draw candy (extra life)
            # Wrapper
            pygame.draw.ellipse(surf, RED, (self.rect.x - camera_x + 2, self.rect.y + 8, 20, 10))
            # Candy
            pygame.draw.ellipse(surf, (255, 182, 193), (self.rect.x - camera_x + 4, self.rect.y + 9, 16, 8))
            # Wrapper ends
            pygame.draw.polygon(surf, (255, 215, 0), [
                (self.rect.x - camera_x + 2, self.rect.y + 8),
                (self.rect.x - camera_x, self.rect.y + 5),
                (self.rect.x - camera_x, self.rect.y + 12),
                (self.rect.x - camera_x + 2, self.rect.y + 18)
            ])
            pygame.draw.polygon(surf, (255, 215, 0), [
                (self.rect.x - camera_x + 22, self.rect.y + 8),
                (self.rect.x - camera_x + 24, self.rect.y + 5),
                (self.rect.x - camera_x + 24, self.rect.y + 12),
                (self.rect.x - camera_x + 22, self.rect.y + 18)
            ])
            
        elif self.power_type == 'nintendo':
            # Draw Nintendo Switch (gaming device - Ahaan's interest)
            pygame.draw.rect(surf, BLACK, (self.rect.x - camera_x + 3, self.rect.y + 6, 18, 12))
            pygame.draw.rect(surf, (100, 100, 100), (self.rect.x - camera_x + 5, self.rect.y + 8, 14, 8))
            # Joy-Con controllers
            pygame.draw.rect(surf, BLUE, (self.rect.x - camera_x, self.rect.y + 8, 4, 8))
            pygame.draw.rect(surf, RED, (self.rect.x - camera_x + 20, self.rect.y + 8, 4, 8))
            
        elif self.power_type == 'drums':
            # Draw drum set (music - Ahaan's interest)
            pygame.draw.ellipse(surf, (139, 69, 19), (self.rect.x - camera_x + 5, self.rect.y + 10, 15, 10))
            pygame.draw.ellipse(surf, (160, 82, 45), (self.rect.x - camera_x + 6, self.rect.y + 11, 13, 8))
            # Drumsticks
            pygame.draw.line(surf, BROWN, (self.rect.x - camera_x + 8, self.rect.y + 5), 
                           (self.rect.x - camera_x + 10, self.rect.y + 12), 2)
            pygame.draw.line(surf, BROWN, (self.rect.x - camera_x + 14, self.rect.y + 5), 
                           (self.rect.x - camera_x + 16, self.rect.y + 12), 2)
                           
        elif self.power_type == 'soccer':
            # Draw soccer ball (sports - Ahaan's interest)
            pygame.draw.circle(surf, WHITE, (self.rect.x - camera_x + 12, self.rect.y + 12), 10)
            pygame.draw.circle(surf, BLACK, (self.rect.x - camera_x + 12, self.rect.y + 12), 10, 2)
            # Soccer ball pattern
            pygame.draw.polygon(surf, BLACK, [
                (self.rect.x - camera_x + 12, self.rect.y + 6),
                (self.rect.x - camera_x + 8, self.rect.y + 10),
                (self.rect.x - camera_x + 10, self.rect.y + 15),
                (self.rect.x - camera_x + 14, self.rect.y + 15),
                (self.rect.x - camera_x + 16, self.rect.y + 10)
            ])

def create_normal_level(level_num=1):
    # Determine level pattern based on level number
    level_pattern = level_num % 4
    
    if level_pattern == 1:
        # Homework Avoidance Theme - scattered platforms like a chaotic study session
        platforms = [
            Platform(0, HEIGHT - 50, LEVEL_END_X+100, 50),  # Ground
            Platform(250, 450, 100, 20),   # Study desk
            Platform(450, 380, 120, 20),   # Bookshelf
            Platform(650, 320, 80, 20),    # Homework pile
            Platform(850, 280, 140, 20),   # Teacher's desk
            Platform(1100, 350, 100, 20),  # More homework
            Platform(1350, 420, 120, 20),  # Escape platform
            Platform(1600, 380, 100, 20),  # Freedom ahead
            Platform(1850, 320, 120, 20)   # Final stretch
        ]

        enemies = [
            Enemy(270, 450-34, "homework", platforms[1].rect),   # Homework on study desk
            Enemy(470, 380-34, "homework", platforms[2].rect),   # More homework
            Enemy(870, 280-34, "homework", platforms[4].rect),   # Teacher homework
            Enemy(1120, 350-34, "homework", platforms[5].rect),  # Even more homework
            Enemy(1370, 420-34, "homework", platforms[6].rect),  # Endless homework
        ]

        coins = [
            Coin(300, 430), Coin(500, 360), Coin(700, 300),
            Coin(900, 260), Coin(1150, 330), Coin(1400, 400), Coin(1650, 360)
        ]

        # Power-ups that represent Ahaan's interests as escape from homework
        powerups = [
            PowerUp(380, 450, 'nintendo'),   # Gaming break
            PowerUp(720, 300, 'drums'),      # Music therapy
            PowerUp(980, 260, 'soccer'),     # Sports escape
            PowerUp(1520, 360, 'speed')      # Pizza reward
        ]
        
    elif level_pattern == 2:
        # Chore Escape Theme - platforms like household items
        platforms = [
            Platform(0, HEIGHT - 50, LEVEL_END_X+100, 50),  # Ground
            Platform(200, 420, 140, 20),   # Kitchen counter
            Platform(400, 350, 100, 20),   # Washing machine
            Platform(600, 280, 120, 20),   # Vacuum storage
            Platform(800, 400, 100, 20),   # Laundry basket
            Platform(1000, 320, 140, 20),  # Cleaning cabinet
            Platform(1250, 380, 100, 20),  # Mop closet
            Platform(1450, 300, 120, 20),  # Dish rack
            Platform(1700, 420, 140, 20)   # Freedom zone
        ]

        enemies = [
            Enemy(220, 420-34, "chores", platforms[1].rect),    # Kitchen chores
            Enemy(420, 350-34, "chores", platforms[2].rect),    # Laundry chores
            Enemy(820, 400-34, "chores", platforms[4].rect),    # Cleaning chores
            Enemy(1270, 380-34, "chores", platforms[6].rect),   # More cleaning
            Enemy(1470, 300-34, "chores", platforms[7].rect)    # Dish washing
        ]

        coins = [
            Coin(270, 400), Coin(450, 330), Coin(650, 260),
            Coin(850, 380), Coin(1100, 300), Coin(1300, 360), Coin(1550, 280)
        ]

        powerups = [
            PowerUp(320, 400, 'drums'),      # Music while cleaning
            PowerUp(680, 260, 'nintendo'),   # Gaming break
            PowerUp(1180, 300, 'jump'),      # Donut treat
            PowerUp(1620, 400, 'life')       # Candy reward
        ]
        
    elif level_pattern == 3:
        # Sports Challenge Theme - athletic course layout
        platforms = [
            Platform(0, HEIGHT - 50, LEVEL_END_X+100, 50),  # Ground
            Platform(300, 400, 80, 20),    # Starting blocks
            Platform(480, 320, 100, 20),   # Hurdle 1
            Platform(680, 240, 80, 20),    # High jump
            Platform(880, 360, 120, 20),   # Balance beam
            Platform(1100, 280, 100, 20),  # Vault box
            Platform(1350, 400, 140, 20),  # Finish line platform
            Platform(1600, 320, 100, 20),  # Victory stand
            Platform(1800, 380, 120, 20)   # Medal ceremony
        ]

        enemies = [
            Enemy(320, 400-34, "badminton", platforms[1].rect), # Forced badminton
            Enemy(500, 320-34, "badminton", platforms[2].rect), # More badminton
            Enemy(900, 360-34, "badminton", platforms[4].rect), # Even more badminton
            Enemy(1120, 280-34, "badminton", platforms[5].rect) # Endless badminton
        ]

        coins = [
            Coin(340, 380), Coin(520, 300), Coin(720, 220),
            Coin(920, 340), Coin(1140, 260), Coin(1400, 380), Coin(1640, 300)
        ]

        powerups = [
            PowerUp(580, 300, 'soccer'),     # Real sports fun
            PowerUp(760, 220, 'nintendo'),   # Gaming instead
            PowerUp(1020, 340, 'drums'),     # Music over sports
            PowerUp(1720, 360, 'speed')      # Pizza celebration
        ]
        
    else:  # level_pattern == 0
        # Shower Avoidance Theme - slippery, water-like platforms
        platforms = [
            Platform(0, HEIGHT - 50, LEVEL_END_X+100, 50),  # Ground
            Platform(180, 450, 90, 15),    # Bathroom mat
            Platform(350, 380, 70, 15),    # Soap dish
            Platform(520, 320, 100, 15),   # Shower ledge
            Platform(720, 280, 80, 15),    # Towel rack
            Platform(900, 370, 110, 15),   # Bathtub edge
            Platform(1150, 300, 90, 15),   # Shampoo shelf
            Platform(1350, 420, 120, 15),  # Dry zone
            Platform(1550, 350, 100, 15),  # Exit door
            Platform(1750, 400, 140, 15)   # Freedom!
        ]

        enemies = [
            Enemy(200, 450-34, "shower", platforms[1].rect),   # Shower time
            Enemy(370, 380-34, "shower", platforms[2].rect),   # Bath time
            Enemy(540, 320-34, "shower", platforms[3].rect),   # Wash hair
            Enemy(920, 370-34, "shower", platforms[5].rect),   # Soap up
            Enemy(1170, 300-34, "shower", platforms[6].rect),  # Rinse off
            Enemy(1570, 350-34, "shower", platforms[8].rect)   # Final rinse
        ]

        coins = [
            Coin(220, 430), Coin(390, 360), Coin(560, 300),
            Coin(750, 260), Coin(950, 350), Coin(1190, 280), Coin(1590, 330)
        ]

        powerups = [
            PowerUp(450, 360, 'nintendo'),   # Gaming to avoid shower
            PowerUp(820, 260, 'drums'),      # Music distraction
            PowerUp(1070, 350, 'life'),      # Candy comfort
            PowerUp(1470, 400, 'jump')       # Donut escape
        ]

    # Mix of regular pipes and special warp pipes
    pipes = [
        Pipe(170, HEIGHT-120, 60, 70),  # Regular pipe
        Pipe(570, HEIGHT-120, 60, 70, is_warp_pipe=True),  # SECRET WARP PIPE!
        Pipe(980, HEIGHT-120, 60, 70),  # Regular pipe
        Pipe(1380, HEIGHT-120, 60, 70, is_warp_pipe=True)  # SECRET WARP PIPE!
    ]

    flag = Flag(LEVEL_END_X+35, HEIGHT-50)
    
    # No mom in normal levels - she only appears in boss fights
    mom = None
    
    return platforms, enemies, coins, pipes, flag, powerups, mom

def create_secret_level(secret_type=1):
    """Create exciting secret worlds with special surprises for Ahaanio!"""
    
    if secret_type == 1:
        # SECRET WORLD 1: "Ultimate Gaming Paradise"
        platforms = [
            Platform(0, HEIGHT - 50, LEVEL_END_X+100, 50),  # Ground
            Platform(200, 450, 120, 20),   # Nintendo Switch platform
            Platform(400, 380, 140, 20),   # PS5 platform
            Platform(600, 320, 100, 20),   # Gaming chair
            Platform(800, 260, 160, 20),   # Ultimate gaming setup
            Platform(1100, 320, 120, 20),  # VR world
            Platform(1350, 380, 140, 20),  # Arcade machines
            Platform(1600, 300, 120, 20),  # Gaming trophy room
            Platform(1850, 420, 200, 20)   # Victory gaming lounge
        ]
        
        # No enemies in this paradise! Only power-ups and coins
        enemies = []
        
        # TONS of gaming-related coins scattered everywhere
        coins = [
            Coin(230, 430), Coin(260, 430), Coin(290, 430),  # Switch coins
            Coin(430, 360), Coin(460, 360), Coin(490, 360), Coin(520, 360),  # PS5 coins
            Coin(630, 300), Coin(660, 300), Coin(690, 300),  # Gaming chair coins
            Coin(820, 240), Coin(850, 240), Coin(880, 240), Coin(910, 240), Coin(940, 240),  # Setup coins
            Coin(1130, 300), Coin(1160, 300), Coin(1190, 300), Coin(1220, 300),  # VR coins
            Coin(1380, 360), Coin(1410, 360), Coin(1440, 360), Coin(1470, 360),  # Arcade coins
            Coin(1630, 280), Coin(1660, 280), Coin(1690, 280), Coin(1720, 280),  # Trophy coins
            Coin(1900, 400), Coin(1930, 400), Coin(1960, 400), Coin(1990, 400), Coin(2020, 400)  # Victory coins
        ]
        
        # AMAZING power-ups - all of Ahaan's favorite things!
        powerups = [
            PowerUp(320, 430, 'nintendo'),   # Gaming heaven
            PowerUp(520, 360, 'nintendo'),   # More gaming
            PowerUp(880, 240, 'drums'),      # Music paradise  
            PowerUp(1180, 300, 'soccer'),    # Sports fun
            PowerUp(1420, 360, 'nintendo'),  # Even more gaming
            PowerUp(1670, 280, 'drums'),     # Music everywhere
            PowerUp(1950, 400, 'life'),      # Candy celebration
            PowerUp(750, 240, 'speed'),      # Pizza party
            PowerUp(1250, 300, 'jump'),      # Donut delight
            PowerUp(1550, 280, 'soccer')     # Sports galore
        ]
        
    elif secret_type == 2:
        # SECRET WORLD 2: "Music & Sports Wonderland"
        platforms = [
            Platform(0, HEIGHT - 50, LEVEL_END_X+100, 50),  # Ground
            Platform(180, 420, 100, 20),   # Drum kit platform
            Platform(350, 350, 120, 20),   # Rock band stage
            Platform(550, 280, 140, 20),   # Concert hall
            Platform(780, 380, 100, 20),   # Soccer field
            Platform(980, 320, 120, 20),   # Basketball court
            Platform(1200, 260, 100, 20),  # Swimming pool deck
            Platform(1400, 350, 140, 20),  # Tennis court
            Platform(1650, 400, 180, 20)   # Championship podium
        ]
        
        enemies = []  # No enemies in paradise!
        
        # Musical and sports themed coins
        coins = [
            Coin(210, 400), Coin(240, 400),  # Drum coins
            Coin(380, 330), Coin(410, 330), Coin(440, 330),  # Band coins
            Coin(580, 260), Coin(610, 260), Coin(640, 260), Coin(670, 260),  # Concert coins
            Coin(810, 360), Coin(840, 360),  # Soccer coins
            Coin(1010, 300), Coin(1040, 300), Coin(1070, 300),  # Basketball coins
            Coin(1230, 240), Coin(1260, 240),  # Swimming coins
            Coin(1430, 330), Coin(1460, 330), Coin(1490, 330),  # Tennis coins
            Coin(1700, 380), Coin(1730, 380), Coin(1760, 380), Coin(1790, 380)  # Champion coins
        ]
        
        powerups = [
            PowerUp(220, 400, 'drums'),      # Drum paradise
            PowerUp(420, 330, 'drums'),      # Rock band power
            PowerUp(620, 260, 'drums'),      # Concert energy
            PowerUp(820, 360, 'soccer'),     # Soccer skills
            PowerUp(1020, 300, 'soccer'),    # Basketball power
            PowerUp(1240, 240, 'nintendo'),  # Gaming break
            PowerUp(1470, 330, 'soccer'),    # Tennis power
            PowerUp(1750, 380, 'life'),      # Victory candy
            PowerUp(600, 260, 'speed'),      # Pizza celebration
            PowerUp(1100, 300, 'jump')       # Champion donut
        ]
    
    else:  # secret_type == 3
        # SECRET WORLD 3: "Food & Family Paradise"
        platforms = [
            Platform(0, HEIGHT - 50, LEVEL_END_X+100, 50),  # Ground
            Platform(200, 440, 120, 20),   # Pizza restaurant
            Platform(400, 370, 100, 20),   # Mediterranean cafe
            Platform(600, 300, 140, 20),   # Italian bistro
            Platform(850, 380, 120, 20),   # Family dining room
            Platform(1100, 320, 100, 20),  # Chess & carrom table
            Platform(1300, 260, 140, 20),  # Dessert paradise
            Platform(1550, 350, 120, 20),  # Family game night
            Platform(1800, 420, 200, 20)   # Ultimate feast table
        ]
        
        enemies = []  # Pure happiness, no enemies!
        
        # Food and family themed coins
        coins = [
            Coin(230, 420), Coin(260, 420), Coin(290, 420),  # Pizza coins
            Coin(430, 350), Coin(460, 350),  # Mediterranean coins
            Coin(630, 280), Coin(660, 280), Coin(690, 280), Coin(720, 280),  # Italian coins
            Coin(880, 360), Coin(910, 360), Coin(940, 360),  # Family coins
            Coin(1130, 300), Coin(1160, 300),  # Game coins
            Coin(1330, 240), Coin(1360, 240), Coin(1390, 240), Coin(1420, 240),  # Dessert coins
            Coin(1580, 330), Coin(1610, 330), Coin(1640, 330),  # Game night coins
            Coin(1850, 400), Coin(1880, 400), Coin(1910, 400), Coin(1940, 400), Coin(1970, 400)  # Feast coins
        ]
        
        powerups = [
            PowerUp(270, 420, 'speed'),      # Pizza power!
            PowerUp(450, 350, 'speed'),      # Mediterranean energy
            PowerUp(670, 280, 'speed'),      # Italian strength
            PowerUp(920, 360, 'life'),       # Family love (candy)
            PowerUp(1150, 300, 'nintendo'),  # Family gaming
            PowerUp(1370, 240, 'life'),      # Dessert delight
            PowerUp(1370, 240, 'jump'),      # Sweet donut
            PowerUp(1620, 330, 'drums'),     # Family music time
            PowerUp(1920, 400, 'life'),      # Ultimate feast candy
            PowerUp(750, 280, 'soccer')      # Active family fun
        ]
    
    # Special warp pipes to return to normal world
    pipes = [
        Pipe(100, HEIGHT-120, 60, 70, is_warp_pipe=True),   # Return pipe at start
        Pipe(LEVEL_END_X-100, HEIGHT-120, 60, 70, is_warp_pipe=True)  # Return pipe at end
    ]
    
    # Special victory flag
    flag = Flag(LEVEL_END_X+35, HEIGHT-50)
    
    # No mom in secret world - it's pure paradise!
    mom = None
    
    return platforms, enemies, coins, pipes, flag, powerups, mom

def create_boss_level(boss_level):
    # Boss level design with platforms leading up to the boss
    platforms = [
        Platform(0, HEIGHT - 50, LEVEL_END_X+100, 50),  # Ground platform
        Platform(200, 480, 120, 20),   # First step up
        Platform(380, 420, 120, 20),   # Second step up  
        Platform(560, 360, 120, 20),   # Third step up
        Platform(480, 250, 160, 30),   # Boss platform (wider and thicker)
        Platform(720, 360, 120, 20),   # Platform on the other side
        Platform(900, 420, 120, 20),   # Step down on right side
        Platform(150, 380, 80, 20),    # Additional platform for maneuvering
        Platform(800, 300, 80, 20)     # Additional platform for maneuvering
    ]
    
    # No regular enemies in boss level
    enemies = []
    
    # Coins placed strategically around the platforms
    coins = [
        Coin(230, 460), Coin(410, 400), Coin(590, 340),  # On the way up
        Coin(750, 340), Coin(930, 400), Coin(180, 360)   # On platforms
    ]
    
    # Power-ups for boss level (fewer but strategic) - Ahaan's favorite things for strength
    powerups = [
        PowerUp(260, 460, 'nintendo'),   # Gaming power for first platform
        PowerUp(830, 280, 'drums'),      # Music power on side platform
        PowerUp(450, 400, 'soccer')      # Sports power on second platform
    ]
    
    # No pipes in boss level
    pipes = []
    
    # No flag, boss serves as level end
    flag = None
    
    # Create the boss on the central elevated platform
    boss = Boss(520, 250 - 80, boss_level)  # Position boss on the boss platform
    
    return platforms, enemies, coins, pipes, flag, powerups, boss
    # Boss level design with platforms leading up to the boss
    platforms = [
        Platform(0, HEIGHT - 50, LEVEL_END_X+100, 50),  # Ground platform
        Platform(200, 480, 120, 20),   # First step up
        Platform(380, 420, 120, 20),   # Second step up  
        Platform(560, 360, 120, 20),   # Third step up
        Platform(480, 250, 160, 30),   # Boss platform (wider and thicker)
        Platform(720, 360, 120, 20),   # Platform on the other side
        Platform(900, 420, 120, 20),   # Step down on right side
        Platform(150, 380, 80, 20),    # Additional platform for maneuvering
        Platform(800, 300, 80, 20)     # Additional platform for maneuvering
    ]
    
    # No regular enemies in boss level
    enemies = []
    
    # Coins placed strategically around the platforms
    coins = [
        Coin(230, 460), Coin(410, 400), Coin(590, 340),  # On the way up
        Coin(750, 340), Coin(930, 400), Coin(180, 360)   # On platforms
    ]
    
    # Power-ups for boss level (fewer but strategic) - Ahaan's favorite things for strength
    powerups = [
        PowerUp(260, 460, 'nintendo'),   # Gaming power for first platform
        PowerUp(830, 280, 'drums'),      # Music power on side platform
        PowerUp(450, 400, 'soccer')      # Sports power on second platform
    ]
    
    # No pipes in boss level
    pipes = []
    
    # No flag, boss serves as level end
    flag = None
    
    # Create the boss on the central elevated platform
    boss = Boss(520, 250 - 80, boss_level)  # Position boss on the boss platform
    
    return platforms, enemies, coins, pipes, flag, powerups, boss

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    player = Player()
    score = 0
    camera_x = 0
    current_level = 1
    boss = None
    mom = None
    music_playing = False
    music_volume = 0.15  # Reduced default volume from 0.3
    
    # Secret world state
    in_secret_world = False
    secret_world_type = 1
    return_level = 1  # Which level to return to
    return_score = 0  # Score before entering secret world
    pipe_entry_timer = 0  # Cooldown for pipe entry

    # STORY PAGES as list of strings
    story_pages = [
        "In the world of Super Ahaanio, a cheerful boy named Ahaan explores a world filled with awesome friends and mischievous foes.",
        "Ahaan LOVES gadgets: Nintendo Switch, PS5, Apple Watch, Laptops. He jams on his drums and performs with his rock band.",
        "He is an energetic sportsman: playing soccer, swimming, basketball, ping-pong, tennis, riding skateboards and rip-sticks, cycling, and more! He enjoys chess and carrom with family, and feasts on his favorite Mediterranean and Italian food.",
        "But he also faces many challenges: endless homework, chores, parents asking him to study, cleaning his room, forced badminton and showers, and parents yelling like villains!",
        "On this journey, you help Ahaan collect power-ups (gadgets, music, food, family time) and avoid pesky foes (homework, chores, nagging) as he adventures toward happiness.",
        "Are you ready to join Ahaan on his adventure? Press SPACE to begin! (Press S anytime to SKIP STORY)"
    ]
    story_page = 0

    # Initialize first level
    platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)

    running = True
    state = "START"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if state == "START":
            if not music_playing:
                start_background_music()
                music_playing = True
            screen.fill(BLACK)
            title = pygame.font.Font(None, 64).render("Super Ahaanio", True, YELLOW)
            prompt = pygame.font.Font(None, 36).render("Press SPACE to Start", True, WHITE)
            story_prompt = pygame.font.Font(None, 28).render("Press ENTER for Story", True, (180,180,255))
            screen.blit(title, ((WIDTH-title.get_width())//2, HEIGHT//2-70))
            screen.blit(prompt, ((WIDTH-prompt.get_width())//2, HEIGHT//2))
            screen.blit(story_prompt, ((WIDTH-story_prompt.get_width())//2, HEIGHT//2+60))
            pygame.display.flip()
            if keys[pygame.K_RETURN]:
                state = "STORY"
                story_page = 0
            elif keys[pygame.K_SPACE]:
                # Reset player and level when starting game directly
                player.__init__()
                current_level = 1
                boss = None
                platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)
                score = 0
                state = "PLAY"
            clock.tick(FPS)
            continue
        if state == "STORY":
            # Wrap text for the story, and ensure neat adaptive placement
            def render_multiline(text, font, color, pos_y, max_width):
                words = text.replace("\n", " \n ").split(' ')
                lines = []
                line = ""
                for word in words:
                    future = line + word + " "
                    if word == "\n":
                        lines.append(line)
                        line = ""
                    elif font.size(future)[0] > max_width:
                        lines.append(line)
                        line = word + " "
                    else:
                        line = future
                if line:
                    lines.append(line)
                for idx, l in enumerate(lines):
                    rend = font.render(l.strip(), True, color)
                    screen.blit(rend, (60, pos_y + idx * (font.get_height() + 3)))

            screen.fill((40,32,60))
            font = pygame.font.Font(None, 34)
            # Adaptive width, about 80% of WIDTH
            page_text = story_pages[story_page]
            color = YELLOW if story_page != len(story_pages)-1 else (255,255,255)
            render_multiline(page_text, font, color, 100, int(WIDTH * 0.8))
            skip = pygame.font.Font(None, 24).render("Press S to skip story", True, WHITE)
            screen.blit(skip, (WIDTH-240, HEIGHT-34))
            pygame.display.flip()
            
            # Debounce space key: advance only on new press
            if not hasattr(main, 'story_last_space'):
                main.story_last_space = False
            if keys[pygame.K_SPACE]:
                if not main.story_last_space:
                    if story_page < len(story_pages)-1:
                        story_page += 1
                    else:
                        state = "PLAY"
                main.story_last_space = True
            else:
                main.story_last_space = False
            if keys[pygame.K_s]:
                # Reset player and level when skipping story
                player.__init__()
                current_level = 1
                boss = None
                platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)
                score = 0
                state = "PLAY"
            clock.tick(FPS)
            continue
        if state == "GAMEOVER":
            play_sound(GAME_OVER_SOUND)
            screen.fill(BLACK)
            msg = pygame.font.Font(None, 64).render("Game Over!", True, RED)
            score_display = pygame.font.Font(None, 36).render(f"Score: {score}", True, YELLOW)
            level_display = pygame.font.Font(None, 36).render(f"Level: {current_level}", True, WHITE)
            prompt = pygame.font.Font(None, 36).render("Press SPACE to Restart", True, WHITE)
            screen.blit(msg, ((WIDTH-msg.get_width())//2, HEIGHT//2-70))
            screen.blit(score_display, ((WIDTH-score_display.get_width())//2, HEIGHT//2-20))
            screen.blit(level_display, ((WIDTH-level_display.get_width())//2, HEIGHT//2+20))
            screen.blit(prompt, ((WIDTH-prompt.get_width())//2, HEIGHT//2+70))
            pygame.display.flip()
            if keys[pygame.K_SPACE]:
                player.__init__()
                current_level = 1
                boss = None
                platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)
                state = "PLAY"
                score = 0
            clock.tick(FPS)
            continue
        if state == "COMPLETE":
            play_sound(LEVEL_COMPLETE_SOUND)
            screen.fill(BLACK)
            if current_level % 5 == 0:
                msg = pygame.font.Font(None, 64).render("Boss Defeated!", True, YELLOW)
            else:
                msg = pygame.font.Font(None, 64).render("Level Complete!", True, YELLOW)
            score_display = pygame.font.Font(None, 36).render(f"Score: {score}", True, GOLDEN)
            level_display = pygame.font.Font(None, 36).render(f"Level: {current_level}", True, WHITE)
            prompt = pygame.font.Font(None, 36).render("Press SPACE for Next Level", True, WHITE)
            screen.blit(msg, ((WIDTH-msg.get_width())//2, HEIGHT//2-70))
            screen.blit(score_display, ((WIDTH-score_display.get_width())//2, HEIGHT//2-20))
            screen.blit(level_display, ((WIDTH-level_display.get_width())//2, HEIGHT//2+20))
            screen.blit(prompt, ((WIDTH-prompt.get_width())//2, HEIGHT//2+70))
            pygame.display.flip()
            if keys[pygame.K_SPACE]:
                # Save power-up state before resetting player
                saved_lives = player.lives
                saved_speed_boost = player.speed_boost
                saved_jump_boost = player.jump_boost
                saved_immunity_timer = player.immunity_timer
                saved_speed_timer = player.speed_timer
                saved_jump_timer = player.jump_timer
                
                player.__init__()
                
                # Restore power-up state
                player.lives = saved_lives
                player.speed_boost = saved_speed_boost
                player.jump_boost = saved_jump_boost
                player.immunity_timer = saved_immunity_timer
                player.speed_timer = saved_speed_timer
                player.jump_timer = saved_jump_timer
                
                current_level += 1
                
                # Check if next level is a boss level
                if current_level % 5 == 0:
                    boss_level = current_level // 5
                    platforms, enemies, coins, pipes, flag, powerups, boss = create_boss_level(boss_level)
                    mom = None  # No mom in boss levels
                    # Lower music volume for boss fights to hear sound effects better
                    set_music_volume(0.08)  # Even quieter for boss fights
                else:
                    boss = None
                    platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)
                    # Normal volume for regular levels
                    set_music_volume(0.15)  # Reduced from 0.3
                
                state = "PLAY"
            clock.tick(FPS)
            continue

        # --- Game Play ---
        # Handle music volume controls
        if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:
            music_volume = min(1.0, music_volume + 0.01)
            set_music_volume(music_volume)
        if keys[pygame.K_MINUS]:
            music_volume = max(0.0, music_volume - 0.01)
            set_music_volume(music_volume)
        if keys[pygame.K_m]:
            if music_volume > 0:
                set_music_volume(0)
            else:
                set_music_volume(0.15)  # Restore to new default volume
                music_volume = 0.15
        
        player.move(platforms)
        
        # Handle mom enemy if exists (only in boss levels, not normal levels)
        if mom:
            mom.update()
            
            # Check collision with mom's slippers
            for slipper in mom.slippers[:]:
                if player.rect.colliderect(slipper.rect) and not player.is_immune():
                    if player.die():  # Returns True if game over
                        state = "GAMEOVER"
                    else:
                        # Player respawned with immunity
                        play_sound(BOSS_HIT_SOUND)
                    break
        
        # Handle boss fight if boss exists
        if boss:
            boss.update(player)
            
            # Check collision with boss slippers
            for slipper in boss.slippers[:]:
                if player.rect.colliderect(slipper.rect) and not player.is_immune():
                    if player.die():  # Returns True if game over
                        state = "GAMEOVER"
                    else:
                        # Player respawned with immunity
                        play_sound(BOSS_HIT_SOUND)
                    break
            
            # Check if player can stomp on boss
            if player.rect.colliderect(boss.rect):
                if player.vy > 0 and player.rect.bottom - boss.rect.top < 40 and player.rect.top < boss.rect.top + 10:  # More forgiving stomp detection
                    if boss.take_damage():
                        player.vy = JUMP_HEIGHT // 2
                        score += 500  # Bonus for hitting boss
                        play_sound(BOSS_HIT_SOUND)
                        
                        if boss.is_defeated():
                            score += 1000  # Big bonus for defeating boss
                            state = "COMPLETE"
                elif not player.is_immune():
                    # Player touched boss but didn't stomp
                    if player.die():  # Returns True if game over
                        state = "GAMEOVER"
                    else:
                        # Player respawned with immunity
                        play_sound(BOSS_HIT_SOUND)
        
        # Handle regular enemies
        stomped = False
        remove_enemies = []
        for enemy in enemies:
            enemy.move(platforms)
        for i,enemy in enumerate(enemies):
            if player.rect.colliderect(enemy.rect) and not player.is_immune():
                if player.vy > 0 and player.rect.bottom - enemy.rect.top < 24 and player.rect.top < enemy.rect.top:
                    remove_enemies.append(i)
                    player.vy = JUMP_HEIGHT // 2
                    stomped = True
                    score += 100
                    play_sound(STOMP_SOUND)  # Use the satisfying stomp sound
                else:
                    # Player was killed by enemy
                    if player.die():  # Returns True if game over
                        state = "GAMEOVER"
                    else:
                        # Player respawned with immunity, play a sound
                        play_sound(BOSS_HIT_SOUND)  # Reuse boss hit sound for respawn
                    break
        for idx in sorted(remove_enemies, reverse=True):
            del enemies[idx]
            
        # Handle coin collection
        for coin in coins[:]:
            if player.rect.colliderect(coin.rect):
                coins.remove(coin)
                score += 1
                play_sound(COIN_SOUND)
                
        # Handle power-up collection
        for powerup in powerups[:]:
            if not powerup.collected and player.rect.colliderect(powerup.rect):
                powerup.collected = True
                player.apply_powerup(powerup.power_type)
                powerups.remove(powerup)
                score += 50  # Bonus points for power-ups
                play_sound(LEVEL_COMPLETE_SOUND)  # Special sound for power-ups
                
        # Update power-ups
        for powerup in powerups:
            powerup.update()
                
        # Handle pipe collisions and secret world entry
        pipe_entered = False
        for pipe in pipes:
            if player.rect.colliderect(pipe.rect):
                if player.rect.bottom > pipe.rect.top and player.vy >= 0:
                    player.rect.bottom = pipe.rect.top
                    player.vy = 0
                    player.on_ground = True
                
                # Check for warp pipe entry (DOWN key + on warp pipe + not in cooldown)
                if (pipe.is_warp_pipe and keys[pygame.K_DOWN] and 
                    player.on_ground and pipe_entry_timer <= 0 and not pipe_entered):
                    
                    if not in_secret_world:
                        # Entering secret world
                        pipe_entered = True
                        in_secret_world = True
                        return_level = current_level
                        return_score = score
                        
                        # Choose secret world type based on current level
                        import random
                        secret_world_type = ((current_level - 1) % 3) + 1
                        
                        # Create secret level
                        platforms, enemies, coins, pipes, flag, powerups, mom = create_secret_level(secret_world_type)
                        boss = None
                        
                        # Reset player position for secret world
                        player.rect.x = 150
                        player.rect.y = HEIGHT - 100
                        player.vy = 0
                        
                        # Bonus score for finding secret world!
                        score += 500
                        
                        # Play special sound
                        play_sound(LEVEL_COMPLETE_SOUND)
                        
                        # Reset camera
                        camera_x = 0
                        
                        # Set pipe entry cooldown
                        pipe_entry_timer = 60  # 1 second cooldown
                        
                    else:
                        # Returning from secret world
                        pipe_entered = True
                        in_secret_world = False
                        current_level = return_level
                        
                        # Keep the score gained in secret world, don't reset it
                        
                        # Recreate the original level
                        if current_level % 5 == 0:
                            boss_level = current_level // 5
                            platforms, enemies, coins, pipes, flag, powerups, boss = create_boss_level(boss_level)
                            mom = None
                        else:
                            boss = None
                            platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)
                        
                        # Reset player position
                        player.rect.x = 150
                        player.rect.y = HEIGHT - 100
                        player.vy = 0
                        
                        # Play return sound
                        play_sound(JUMP_SOUND)
                        
                        # Reset camera
                        camera_x = 0
                        
                        # Set pipe entry cooldown
                        pipe_entry_timer = 60  # 1 second cooldown
                    
                    break  # Exit pipe loop after entering
        
        # Update pipe entry cooldown
        if pipe_entry_timer > 0:
            pipe_entry_timer -= 1

        # Handle flag collision (only for non-boss levels)
        if flag and player.rect.colliderect(flag.rect):
            if in_secret_world:
                # Completing secret world gives bonus but returns to normal world
                score += 1000  # Big bonus for completing secret world!
                in_secret_world = False
                current_level = return_level
                
                # Recreate the original level
                if current_level % 5 == 0:
                    boss_level = current_level // 5
                    platforms, enemies, coins, pipes, flag, powerups, boss = create_boss_level(boss_level)
                    mom = None
                else:
                    boss = None
                    platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)
                
                # Reset player position
                player.rect.x = 150
                player.rect.y = HEIGHT - 100
                player.vy = 0
                camera_x = 0
                
                # Play special completion sound
                play_sound(LEVEL_COMPLETE_SOUND)
            else:
                # Normal level completion
                state = "COMPLETE"

        camera_x = player.rect.centerx - WIDTH // 2
        if camera_x < 0:
            camera_x = 0
        max_cam = LEVEL_END_X + 100 - WIDTH
        if camera_x > max_cam:
            camera_x = max_cam

        # Enhanced background with gradient sky
        if in_secret_world:
            # Magical rainbow background for secret worlds
            import math
            import time
            warp_timer = time.time() * 100  # Use time for animation
            for y in range(HEIGHT):
                ratio = y / HEIGHT
                # Rainbow gradient effect
                r = int(128 + 127 * math.sin(ratio * 2 + warp_timer * 0.05))
                g = int(128 + 127 * math.sin(ratio * 2 + 2 + warp_timer * 0.05))
                b = int(128 + 127 * math.sin(ratio * 2 + 4 + warp_timer * 0.05))
                pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
        else:
            # Beautiful sky gradient for normal levels
            for y in range(HEIGHT):
                ratio = y / HEIGHT
                # Sky blue to lighter blue gradient
                r = int(92 + ratio * 50)   # 92 to 142
                g = int(192 + ratio * 40)  # 192 to 232  
                b = int(255)               # Pure blue
                pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
            
            # Add some clouds
            import random
            random.seed(42)  # Consistent cloud positions
            for i in range(8):
                cloud_x = (i * 250 + random.randint(-50, 50) - camera_x // 3) % (WIDTH + 200) - 100
                cloud_y = 50 + random.randint(-20, 40)
                # Cloud made of circles
                for j in range(4):
                    circle_x = cloud_x + j * 15 + random.randint(-5, 5)
                    circle_y = cloud_y + random.randint(-8, 8)
                    circle_size = 15 + random.randint(-3, 8)
                    pygame.draw.circle(screen, WHITE, (int(circle_x), int(circle_y)), circle_size)
                    pygame.draw.circle(screen, (240, 240, 255), (int(circle_x-2), int(circle_y-2)), circle_size-2)
        
        # Draw level elements
        for platform in platforms:
            platform.draw(screen, camera_x)
        for pipe in pipes:
            pipe.draw(screen, camera_x)
        for enemy in enemies:
            enemy.draw(screen, camera_x)
        for coin in coins:
            coin.draw(screen, camera_x)
        for powerup in powerups:
            powerup.draw(screen, camera_x)
        
        # Draw flag only if it exists (not in boss levels)
        if flag:
            flag.draw(screen, camera_x)
            
        # Draw mom if it exists (normal levels)
        if mom:
            mom.draw(screen, camera_x)
            
        # Draw boss if it exists
        if boss:
            boss.draw(screen, camera_x)
            
        player.draw(screen, camera_x)
        
        # UI elements
        font = pygame.font.Font(None, 36)
        text = font.render(f'Score: {score}', True, BLACK)
        screen.blit(text, (10, 10))
        
        # Show secret world indicator
        if in_secret_world:
            level_text = font.render(f'SECRET WORLD {secret_world_type}!', True, GOLDEN)
            screen.blit(level_text, (10, 50))
            secret_hint = pygame.font.Font(None, 24).render('Find warp pipes to return!', True, YELLOW)
            screen.blit(secret_hint, (10, 90))
        else:
            level_text = font.render(f'Level: {current_level}', True, BLACK)
            screen.blit(level_text, (10, 50))
        
        lives_text = font.render(f'Lives: {player.lives}', True, BLACK)
        screen.blit(lives_text, (10, 130 if in_secret_world else 90))
        
        # Show pipe entry hint when near warp pipes
        near_warp_pipe = False
        for pipe in pipes:
            if pipe.is_warp_pipe and player.rect.colliderect(pygame.Rect(pipe.rect.x - 30, pipe.rect.y - 30, pipe.rect.w + 60, pipe.rect.h + 60)):
                near_warp_pipe = True
                break
        
        if near_warp_pipe and pipe_entry_timer <= 0:
            if in_secret_world:
                hint_text = pygame.font.Font(None, 28).render('Press DOWN to return to normal world!', True, YELLOW)
            else:
                hint_text = pygame.font.Font(None, 28).render('Press DOWN to enter SECRET WORLD!', True, GOLDEN)
            screen.blit(hint_text, (WIDTH//2 - hint_text.get_width()//2, HEIGHT - 80))
        
        # Show power-up status
        ui_y_offset = 170 if in_secret_world else 130
        
        if player.speed_boost > 0:
            speed_text = pygame.font.Font(None, 24).render(f'Speed Boost: {player.speed_timer // 60 + 1}s', True, GREEN)
            screen.blit(speed_text, (10, ui_y_offset))
        
        if player.jump_boost < 0:
            jump_text = pygame.font.Font(None, 24).render(f'Jump Boost: {player.jump_timer // 60 + 1}s', True, BLUE)
            screen.blit(jump_text, (10, ui_y_offset + 20))
            
        if player.is_immune():
            immune_text = pygame.font.Font(None, 24).render(f'Immune: {player.immunity_timer // 60 + 1}s', True, YELLOW)
            screen.blit(immune_text, (10, ui_y_offset + 40))
        
        # Show boss stage if in boss fight
        if boss:
            stage_text = pygame.font.Font(None, 28).render(f'Boss Stage: {boss.stage}/3', True, RED)
            screen.blit(stage_text, (10, ui_y_offset + 70))
        
        # Show music controls
        controls_text = pygame.font.Font(None, 20).render('Music: +/- Volume, M Mute', True, BLACK)
        screen.blit(controls_text, (WIDTH - 200, 10))
        
        volume_text = pygame.font.Font(None, 20).render(f'Vol: {int(music_volume * 100)}%', True, BLACK)
        screen.blit(volume_text, (WIDTH - 200, 30))
            
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    