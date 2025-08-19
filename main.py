import pygame
import sys
import numpy as np
import os
import json
import math
import random
import time

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# High Score Management
HIGHSCORE_FILE = "highscore.json"

def load_high_score():
    """Load the high score from file"""
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
    except:
        pass
    return 0

def save_high_score(score):
    """Save the high score to file"""
    try:
        data = {'high_score': score}
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def update_high_score(current_score):
    """Check if current score is a new high score and save if it is"""
    high_score = load_high_score()
    if current_score > high_score:
        save_high_score(current_score)
        return True, current_score
    return False, high_score

# Load music files
try:
    pygame.mixer.music.load("bgm.mp3")
    MUSIC_AVAILABLE = True
except pygame.error:
    print("Music file not found, continuing without music")
    MUSIC_AVAILABLE = False

# Music state tracking
current_music_type = "normal"  # "normal" or "boss"

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

def create_boss_music():
    """Create intense boss fight music using procedural generation"""
    if not MUSIC_AVAILABLE:
        return None
    try:
        import numpy as np
        import pygame.sndarray
        
        sample_rate = 22050
        duration = 8.0  # 8-second loop
        frames = int(duration * sample_rate)
        
        # Create intense bass line
        t = np.linspace(0, duration, frames, False)
        bass_freq = 65.4  # Low C
        bass = np.sin(2 * np.pi * bass_freq * t) * 0.3
        
        # Add driving drum beat pattern
        drum_freq = 2.0  # 2 beats per second
        drum_pattern = np.sin(2 * np.pi * drum_freq * t) * 0.4
        drum_pattern = np.where(drum_pattern > 0.2, 0.8, 0.0)
        
        # Add intense melody
        melody_freqs = [261.6, 293.7, 329.6, 392.0, 440.0]  # C major scale higher octave
        melody = np.zeros_like(t)
        for i, freq in enumerate(melody_freqs):
            phase_offset = i * duration / len(melody_freqs)
            melody += np.sin(2 * np.pi * freq * (t + phase_offset)) * 0.15
        
        # Add tension with dissonant harmonics
        tension = np.sin(2 * np.pi * 185.0 * t) * 0.2  # Dissonant frequency
        
        # Combine all elements
        boss_music = bass + drum_pattern + melody + tension
        
        # Normalize to prevent clipping
        boss_music = boss_music / np.max(np.abs(boss_music)) * 0.7
        
        # Convert to 16-bit integers
        boss_music = (boss_music * 32767).astype(np.int16)
        
        # Create stereo array
        stereo_music = np.zeros((frames, 2), dtype=np.int16)
        stereo_music[:, 0] = boss_music  # Left channel
        stereo_music[:, 1] = boss_music  # Right channel
        
        return pygame.sndarray.make_sound(stereo_music)
    except:
        return None

def start_background_music():
    """Start playing background music"""
    global current_music_type
    if MUSIC_AVAILABLE:
        try:
            pygame.mixer.music.load("bgm.mp3")
            pygame.mixer.music.play(-1, 0.0)  # Loop indefinitely
            pygame.mixer.music.set_volume(0.15)  # Reduced from 0.3 to 0.15 (50% quieter)
            current_music_type = "normal"
        except:
            pass

def start_boss_music():
    """Start playing intense boss fight music"""
    global current_music_type
    if MUSIC_AVAILABLE and current_music_type != "boss":
        try:
            # Simply increase the volume for boss fights (simpler and more reliable)
            pygame.mixer.music.set_volume(0.35)  # Much louder for boss intensity
            current_music_type = "boss"
            print("Boss music started - volume increased!")  # Debug message
        except Exception as e:
            print(f"Error starting boss music: {e}")
            current_music_type = "boss"

def stop_background_music():
    """Stop background music"""
    global current_music_type
    if MUSIC_AVAILABLE:
        try:
            pygame.mixer.music.stop()
            current_music_type = "normal"
        except:
            pass

def return_to_normal_music():
    """Return to normal background music after boss fight"""
    global current_music_type
    if MUSIC_AVAILABLE and current_music_type == "boss":
        try:
            pygame.mixer.music.set_volume(0.15)  # Back to normal volume
            current_music_type = "normal"
            print("Returned to normal music - volume decreased!")  # Debug message
        except Exception as e:
            print(f"Error returning to normal music: {e}")
            current_music_type = "normal"

def set_music_volume(volume):
    """Set music volume (0.0 to 1.0)"""
    if MUSIC_AVAILABLE:
        try:
            pygame.mixer.music.set_volume(volume)
        except:
            pass

class Shuttlecock:
    def __init__(self, x, y, direction, speed=4):
        self.rect = pygame.Rect(x, y, 12, 20)
        self.direction = direction  # -1 for left, 1 for right
        self.speed = speed
        self.rotation = 0
        self.gravity = 0.3  # Shuttlecocks fall slowly due to feathers
        self.vy = -2  # Initial upward velocity
        
    def update(self):
        # Horizontal movement
        self.rect.x += self.speed * self.direction
        
        # Vertical movement with gravity
        self.vy += self.gravity
        self.rect.y += self.vy
        
        # Rotation for visual effect
        self.rotation += 5
        
        # Remove if off screen or hit ground
        should_remove = (self.rect.x < -100 or self.rect.x > LEVEL_END_X + 100 or 
                        self.rect.y > HEIGHT + 50)
        return should_remove
    
    def draw(self, surf, camera_x):
        # Draw shuttlecock (birdie)
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y
        
        # Only draw if on screen
        if screen_x > -50 and screen_x < WIDTH + 50 and screen_y > -50 and screen_y < HEIGHT + 50:
            # Feather part (white)
            pygame.draw.ellipse(surf, WHITE, (int(screen_x), int(screen_y), 12, 8))
            pygame.draw.ellipse(surf, (240, 240, 240), (int(screen_x + 1), int(screen_y + 1), 10, 6))  # Highlight
            
            # Rubber tip (black)
            pygame.draw.ellipse(surf, BLACK, (int(screen_x + 2), int(screen_y + 8), 8, 12))
            pygame.draw.ellipse(surf, (60, 60, 60), (int(screen_x + 3), int(screen_y + 9), 6, 10))  # Highlight
            
            # Feather lines for detail
            for i in range(3):
                line_x = screen_x + 3 + i * 2
                pygame.draw.line(surf, (200, 200, 200), (int(line_x), int(screen_y + 2)), 
                               (int(line_x), int(screen_y + 6)), 1)

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

            # Move horizontally with improved boundaries
            self.rect.x += self.speed * self.direction
            
            # Better boundary checking to keep boss on screen
            # Left boundary - keep boss at least 100 pixels from left edge
            if self.rect.left <= 100:
                self.rect.left = 100
                self.direction = 1
            # Right boundary - keep boss at least 100 pixels from right edge
            elif self.rect.right >= LEVEL_END_X - 100:
                self.rect.right = LEVEL_END_X - 100
                self.direction = -1
                
            # Additional safety check to prevent going off level completely
            if self.rect.centerx < 150:
                self.rect.centerx = 150
                self.direction = 1
            elif self.rect.centerx > LEVEL_END_X - 150:
                self.rect.centerx = LEVEL_END_X - 150
                self.direction = -1
                
            # Vertical boundary checking to keep boss above ground
            if self.rect.bottom > HEIGHT - 80:  # Keep boss above ground level
                self.rect.bottom = HEIGHT - 80
            if self.rect.top < 100:  # Don't let boss go too high
                self.rect.top = 100

            # Throw slippers
            self.slipper_timer += 1
            if self.slipper_timer >= int(self.slipper_cooldown * 0.6):  # Faster than stage 2, but not overwhelming
                self.throw_targeted_slipper(player)
                self.slipper_timer = 0
                # Mom yells when throwing slippers
                self.shout_frames = 30  # Show "AHAAAAN!!" for 30 frames

        # Update slippers
        self.slippers = [s for s in self.slippers if not s.update()]
        
        # Global boundary enforcement for all stages
        # Ensure boss never goes outside level bounds regardless of stage
        if self.rect.left < 50:
            self.rect.left = 50
        if self.rect.right > LEVEL_END_X - 50:
            self.rect.right = LEVEL_END_X - 50
        if self.rect.bottom > HEIGHT - 60:
            self.rect.bottom = HEIGHT - 60
        if self.rect.top < 80:
            self.rect.top = 80

    def throw_random_slippers(self):
        # Throw 3-4 slippers in different directions (reduced from 4-6)
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
        
        # Badminton-specific attributes
        if self.enemy_type == "badminton":
            self.shoot_timer = 0
            self.shoot_cooldown = 120  # 2 seconds at 60 FPS
            self.shuttlecocks = []

    def move(self, platforms):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= self.platform.left:
            self.rect.left = self.platform.left
            self.direction = 1
        if self.rect.right >= self.platform.right:
            self.rect.right = self.platform.right
            self.direction = -1
            
        # Badminton enemy shooting logic
        if self.enemy_type == "badminton":
            self.shoot_timer += 1
            if self.shoot_timer >= self.shoot_cooldown:
                self.shoot_timer = 0
                # Shoot shuttlecock in the direction the enemy is facing
                shuttlecock = Shuttlecock(self.rect.centerx, self.rect.y - 10, self.direction)
                self.shuttlecocks.append(shuttlecock)
            
            # Update shuttlecocks
            self.shuttlecocks = [s for s in self.shuttlecocks if not s.update()]

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
            
            # Draw shuttlecocks
            for shuttlecock in self.shuttlecocks:
                shuttlecock.draw(surf, camera_x)
                
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

class MovingPlatform(Platform):
    def __init__(self, x, y, w, h, move_type="horizontal", distance=100, speed=2):
        super().__init__(x, y, w, h)
        self.start_x = x
        self.start_y = y
        self.move_type = move_type  # "horizontal", "vertical", or "circular"
        self.distance = distance  # Maximum distance to move
        self.speed = speed  # Movement speed
        self.direction = 1  # 1 or -1 for direction
        self.angle = 0  # For circular movement
        
    def update(self):
        """Update platform position based on movement type"""
        if self.move_type == "horizontal":
            # Move horizontally back and forth
            self.rect.x += self.speed * self.direction
            
            # Reverse direction at boundaries
            if self.rect.x >= self.start_x + self.distance:
                self.direction = -1
                self.rect.x = self.start_x + self.distance
            elif self.rect.x <= self.start_x:
                self.direction = 1
                self.rect.x = self.start_x
                
        elif self.move_type == "vertical":
            # Move vertically up and down
            self.rect.y += self.speed * self.direction
            
            # Reverse direction at boundaries
            if self.rect.y >= self.start_y + self.distance:
                self.direction = -1
                self.rect.y = self.start_y + self.distance
            elif self.rect.y <= self.start_y:
                self.direction = 1
                self.rect.y = self.start_y
                
        elif self.move_type == "circular":
            # Move in a circular pattern
            self.angle += self.speed * 0.05  # Adjust speed for circular motion
            radius = self.distance // 2
            center_x = self.start_x + radius
            center_y = self.start_y + radius
            
            import math
            self.rect.x = int(center_x + radius * math.cos(self.angle))
            self.rect.y = int(center_y + radius * math.sin(self.angle))
    
    def draw(self, surf, camera_x):
        # Draw the moving platform with a special visual effect
        # Call parent draw method first
        super().draw(surf, camera_x)
        
        # Add visual indicators for moving platform
        x = self.rect.x - camera_x
        y = self.rect.y
        w = self.rect.w
        h = self.rect.h
        
        # Add animated arrows or dots to show it's moving
        if self.move_type == "horizontal":
            # Draw horizontal arrows
            pygame.draw.polygon(surf, YELLOW, [
                (x + w//2 - 8, y - 8), (x + w//2 - 2, y - 5), (x + w//2 - 8, y - 2)
            ])
            pygame.draw.polygon(surf, YELLOW, [
                (x + w//2 + 8, y - 8), (x + w//2 + 2, y - 5), (x + w//2 + 8, y - 2)
            ])
        elif self.move_type == "vertical":
            # Draw vertical arrows
            pygame.draw.polygon(surf, YELLOW, [
                (x + w//2 - 3, y - 8), (x + w//2, y - 2), (x + w//2 + 3, y - 8)
            ])
            pygame.draw.polygon(surf, YELLOW, [
                (x + w//2 - 3, y + h + 2), (x + w//2, y + h + 8), (x + w//2 + 3, y + h + 2)
            ])
        elif self.move_type == "circular":
            # Draw circular indicator
            pygame.draw.circle(surf, YELLOW, (x + w//2, y - 6), 3)
            pygame.draw.circle(surf, YELLOW, (x + w//2, y - 6), 6, 2)

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
    # Special case: Level 5 - Badminton Court Challenge
    if level_num == 5:
        # BADMINTON COURT THEME - Forced badminton class nightmare!
        platforms = [
            Platform(0, HEIGHT - 50, LEVEL_END_X+100, 50),  # Ground (court floor)
            Platform(200, 420, 120, 20),   # Badminton net post
            Platform(400, 350, 100, 20),   # Court bench
            MovingPlatform(580, 280, 80, 20, "vertical", 60, 1.5),   # Moving shuttlecock platform
            Platform(750, 380, 140, 20),   # Equipment rack
            MovingPlatform(950, 320, 100, 20, "horizontal", 80, 2),  # Moving racket platform
            Platform(1150, 250, 120, 20),  # Coach's platform
            MovingPlatform(1350, 400, 100, 20, "vertical", 70, 1),   # Moving training equipment
            Platform(1550, 330, 110, 20),  # Court sideline
            MovingPlatform(1750, 280, 120, 20, "horizontal", 100, 1.5),  # Moving exit platform
            Platform(1950, 390, 150, 20)   # Freedom zone (exit from badminton class)
        ]

        # Lots of badminton enemies - representing the forced badminton class
        enemies = [
            Enemy(220, 420-34, "badminton", platforms[1].rect),    # Net area badminton
            Enemy(420, 350-34, "badminton", platforms[2].rect),    # Bench area badminton
            Enemy(770, 380-34, "badminton", platforms[4].rect),    # Equipment rack badminton
            Enemy(1170, 250-34, "badminton", platforms[6].rect),   # Coach area (extra challenging)
            Enemy(1570, 330-34, "badminton", platforms[8].rect),   # Sideline badminton
            Enemy(1970, 390-34, "badminton", platforms[10].rect)   # Final badminton challenge
        ]

        # Coins scattered around the badminton court
        coins = [
            Coin(250, 400), Coin(280, 400), Coin(310, 400),     # Net area coins
            Coin(450, 330), Coin(480, 330),                     # Bench coins
            Coin(620, 260), Coin(650, 260),                     # Moving platform coins
            Coin(800, 360), Coin(830, 360), Coin(860, 360),     # Equipment rack coins
            Coin(1000, 300), Coin(1030, 300),                   # Moving racket coins
            Coin(1200, 230), Coin(1230, 230), Coin(1260, 230),  # Coach platform coins
            Coin(1400, 380), Coin(1430, 380),                   # Training equipment coins
            Coin(1600, 310), Coin(1630, 310), Coin(1660, 310),  # Sideline coins
            Coin(1800, 260), Coin(1830, 260),                   # Moving exit coins
            Coin(2000, 370), Coin(2030, 370), Coin(2060, 370)   # Freedom zone coins
        ]

        # Power-ups representing Ahaan's preferred activities (escapes from badminton)
        powerups = [
            PowerUp(350, 400, 'nintendo'),   # Gaming escape from badminton
            PowerUp(540, 330, 'drums'),      # Music instead of badminton
            PowerUp(890, 360, 'soccer'),     # Real sports fun vs forced badminton
            PowerUp(1100, 300, 'life'),      # Candy comfort from badminton stress
            PowerUp(1300, 230, 'speed'),     # Pizza reward for surviving coach
            PowerUp(1500, 310, 'jump'),      # Donut boost to escape sideline
            PowerUp(1890, 370, 'nintendo')   # Final gaming reward for escaping badminton class
        ]

        # Special badminton court pipes
        pipes = [
            Pipe(120, HEIGHT-120, 60, 70),    # Locker room pipe
            Pipe(500, HEIGHT-120, 60, 70, is_warp_pipe=True),   # SECRET ESCAPE PIPE!
            Pipe(1000, HEIGHT-120, 60, 70),   # Equipment storage pipe
            Pipe(1450, HEIGHT-120, 60, 70, is_warp_pipe=True),  # SECRET FREEDOM PIPE!
            Pipe(1850, HEIGHT-120, 60, 70)    # Exit pipe
        ]

        flag = Flag(LEVEL_END_X+35, HEIGHT-50)
        mom = None
        
        return platforms, enemies, coins, pipes, flag, powerups, mom
    
    # Determine level pattern based on level number (for all other levels)
    level_pattern = level_num % 4
    
    if level_pattern == 1:
        # Homework Avoidance Theme - scattered platforms like a chaotic study session
        platforms = [
            Platform(0, HEIGHT - 50, LEVEL_END_X+100, 50),  # Ground
            Platform(250, 450, 100, 20),   # Study desk
            Platform(450, 380, 120, 20),   # Bookshelf
            MovingPlatform(650, 320, 80, 20, "vertical", 80, 1),    # Moving homework pile
            Platform(850, 280, 140, 20),   # Teacher's desk
            MovingPlatform(1100, 350, 100, 20, "horizontal", 120, 2),  # Moving homework platform
            Platform(1350, 420, 120, 20),  # Escape platform
            MovingPlatform(1600, 380, 100, 20, "vertical", 60, 1.5),  # Moving freedom platform
            Platform(1850, 320, 120, 20)   # Final stretch
        ]

        enemies = [
            Enemy(270, 450-34, "homework", platforms[1].rect),   # Homework on study desk
            Enemy(470, 380-34, "homework", platforms[2].rect),   # More homework
            Enemy(870, 280-34, "homework", platforms[4].rect),   # Teacher homework
            Enemy(1370, 420-34, "homework", platforms[6].rect),  # Homework on stable platform
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
            MovingPlatform(400, 350, 100, 20, "horizontal", 100, 1.5),   # Moving washing machine
            Platform(600, 280, 120, 20),   # Vacuum storage
            MovingPlatform(800, 400, 100, 20, "vertical", 70, 1),   # Moving laundry basket
            Platform(1000, 320, 140, 20),  # Cleaning cabinet
            Platform(1250, 380, 100, 20),  # Mop closet
            MovingPlatform(1450, 300, 120, 20, "horizontal", 80, 2),  # Moving dish rack
            Platform(1700, 420, 140, 20)   # Freedom zone
        ]

        enemies = [
            Enemy(220, 420-34, "chores", platforms[1].rect),    # Kitchen chores
            Enemy(820, 400-34, "chores", platforms[4].rect),    # Laundry chores (will move with platform)
            Enemy(1020, 320-34, "chores", platforms[5].rect),   # Cleaning chores
            Enemy(1270, 380-34, "chores", platforms[6].rect),   # More cleaning
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
            MovingPlatform(480, 320, 100, 20, "vertical", 60, 1.5),   # Moving hurdle 1
            Platform(680, 240, 80, 20),    # High jump
            MovingPlatform(880, 360, 120, 20, "horizontal", 100, 1),   # Moving balance beam
            Platform(1100, 280, 100, 20),  # Vault box
            Platform(1350, 400, 140, 20),  # Finish line platform
            MovingPlatform(1600, 320, 100, 20, "circular", 60, 1),  # Victory stand (circular motion)
            Platform(1800, 380, 120, 20)   # Medal ceremony
        ]

        enemies = [
            Enemy(320, 400-34, "badminton", platforms[1].rect), # Forced badminton
            Enemy(700, 240-34, "badminton", platforms[3].rect), # More badminton on stable platform
            Enemy(1120, 280-34, "badminton", platforms[5].rect), # Badminton on vault box
            Enemy(1820, 380-34, "badminton", platforms[8].rect) # Final badminton challenge
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
    high_score = load_high_score()  # Load high score at start
    camera_x = 0
    current_level = 1
    boss = None
    mom = None
    music_playing = False
    music_volume = 0.15  # Reduced default volume from 0.3
    
    # Nintendo Switch Parts Collection
    switch_parts = {
        'left_controller': False,
        'right_controller': False, 
        'screen': False
    }
    switch_parts_count = 0
    
    # Secret world state
    in_secret_world = False
    secret_world_type = 1
    return_level = 1  # Which level to return to
    return_score = 0  # Score before entering secret world
    pipe_entry_timer = 0  # Cooldown for pipe entry
    
    # Pause menu state
    game_paused = False
    pause_menu_selection = 0  # 0=Resume, 1=Restart, 2=Home

    # STORY PAGES as list of strings
    # CUTSCENE STORY SEGMENTS
    cutscene_segments = [
        "INTRO_WORLD",
        "INTRO_AHAAN_INTERESTS", 
        "INTRO_AHAAN_SPORTS",
        "INTRO_CHALLENGES",
        "SWITCH_GAMING",
        "MOM_APPEARS",
        "SWITCH_BREAKS",
        "CHASE_BEGINS",
        "READY_TO_PLAY"
    ]
    story_page = 0
    cutscene_timer = 0  # Timer for animations within cutscenes

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
            high_score_display = pygame.font.Font(None, 32).render(f"High Score: {high_score}", True, GOLDEN)
            screen.blit(title, ((WIDTH-title.get_width())//2, HEIGHT//2-100))
            screen.blit(prompt, ((WIDTH-prompt.get_width())//2, HEIGHT//2-20))
            screen.blit(story_prompt, ((WIDTH-story_prompt.get_width())//2, HEIGHT//2+30))
            screen.blit(high_score_display, ((WIDTH-high_score_display.get_width())//2, HEIGHT//2+80))
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
                switch_parts = {'left_controller': False, 'right_controller': False, 'screen': False}
                switch_parts_count = 0
                state = "PLAY"
            clock.tick(FPS)
            continue
        if state == "STORY":
            cutscene_timer += 1
            current_cutscene = cutscene_segments[story_page]
            
            # Common cutscene background
            screen.fill((20, 20, 40))  # Dark blue background
            
            # Add animated stars background
            import math
            for i in range(20):
                star_x = (i * 137 + cutscene_timer) % WIDTH
                star_y = (i * 89 + cutscene_timer // 2) % HEIGHT
                star_brightness = int(128 + 127 * math.sin(cutscene_timer * 0.05 + i))
                pygame.draw.circle(screen, (star_brightness, star_brightness, 255), (star_x, star_y), 2)
            
            # Render specific cutscene
            if current_cutscene == "INTRO_WORLD":
                # Scene 1: Introduction to Super Ahaanio world
                title = pygame.font.Font(None, 72).render("Super Ahaanio", True, GOLDEN)
                subtitle = pygame.font.Font(None, 48).render("The Adventure Begins", True, YELLOW)
                
                # Animated world elements
                bounce = int(10 * math.sin(cutscene_timer * 0.1))
                
                # Draw floating platforms
                for i in range(3):
                    plat_x = 100 + i * 250 + int(20 * math.sin(cutscene_timer * 0.05 + i))
                    plat_y = 400 + bounce + i * 20
                    pygame.draw.rect(screen, BLUE, (plat_x, plat_y, 80, 20))
                    pygame.draw.rect(screen, (100, 150, 255), (plat_x + 2, plat_y + 2, 76, 16))
                
                # Draw Ahaan character
                ahaan_x = 200 + int(30 * math.sin(cutscene_timer * 0.08))
                ahaan_y = 350 + bounce
                pygame.draw.ellipse(screen, SKIN, (ahaan_x, ahaan_y, 30, 40))  # Head
                pygame.draw.rect(screen, BLUE, (ahaan_x - 5, ahaan_y + 40, 40, 50))  # Body
                pygame.draw.rect(screen, SKIN, (ahaan_x, ahaan_y + 80, 15, 30))  # Left leg
                pygame.draw.rect(screen, SKIN, (ahaan_x + 20, ahaan_y + 80, 15, 30))  # Right leg
                
                screen.blit(title, ((WIDTH - title.get_width()) // 2, 100))
                screen.blit(subtitle, ((WIDTH - subtitle.get_width()) // 2, 180))
                
                text = pygame.font.Font(None, 36).render("In a world filled with adventure...", True, WHITE)
                screen.blit(text, ((WIDTH - text.get_width()) // 2, HEIGHT - 150))
                
            elif current_cutscene == "INTRO_AHAAN_INTERESTS":
                # Scene 2: Ahaan's interests and gadgets
                title = pygame.font.Font(None, 56).render("Meet Ahaan!", True, GOLDEN)
                screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
                
                # Draw enhanced Ahaan in center with more detail
                ahaan_center_x, ahaan_center_y = WIDTH // 2, 220
                
                # Head with facial features
                pygame.draw.ellipse(screen, SKIN, (ahaan_center_x - 20, 150, 40, 50))  # Head
                pygame.draw.ellipse(screen, (240, 200, 160), (ahaan_center_x - 18, 152, 36, 46))  # Face highlight
                
                # Hair
                pygame.draw.ellipse(screen, BROWN, (ahaan_center_x - 25, 145, 50, 25))
                pygame.draw.circle(screen, (120, 80, 40), (ahaan_center_x - 15, 150), 8)  # Hair tuft left
                pygame.draw.circle(screen, (120, 80, 40), (ahaan_center_x + 15, 150), 8)  # Hair tuft right
                
                # Eyes with sparkle
                pygame.draw.ellipse(screen, WHITE, (ahaan_center_x - 12, 165, 8, 10))  # Left eye
                pygame.draw.ellipse(screen, WHITE, (ahaan_center_x + 4, 165, 8, 10))  # Right eye
                pygame.draw.circle(screen, BLACK, (ahaan_center_x - 8, 169), 3)  # Left pupil
                pygame.draw.circle(screen, BLACK, (ahaan_center_x + 8, 169), 3)  # Right pupil
                pygame.draw.circle(screen, WHITE, (ahaan_center_x - 7, 168), 1)  # Left shine
                pygame.draw.circle(screen, WHITE, (ahaan_center_x + 9, 168), 1)  # Right shine
                
                # Smile
                pygame.draw.arc(screen, BLACK, (ahaan_center_x - 8, 175, 16, 10), 0, math.pi, 3)
                
                # Body with shirt details
                pygame.draw.rect(screen, GREEN, (ahaan_center_x - 25, 200, 50, 60))  # Body
                pygame.draw.rect(screen, (100, 200, 100), (ahaan_center_x - 22, 202, 44, 56))  # Shirt highlight
                pygame.draw.circle(screen, BLACK, (ahaan_center_x - 15, 210), 2)  # Button
                pygame.draw.circle(screen, BLACK, (ahaan_center_x - 15, 225), 2)  # Button
                pygame.draw.circle(screen, BLACK, (ahaan_center_x - 15, 240), 2)  # Button
                
                # Arms and legs with better proportions
                pygame.draw.rect(screen, SKIN, (ahaan_center_x - 45, 220, 20, 40))  # Left arm
                pygame.draw.rect(screen, SKIN, (ahaan_center_x + 25, 220, 20, 40))  # Right arm
                pygame.draw.rect(screen, BLUE, (ahaan_center_x - 15, 260, 18, 40))  # Left leg (jeans)
                pygame.draw.rect(screen, BLUE, (ahaan_center_x - 3, 260, 18, 40))  # Right leg (jeans)
                
                # Shoes
                pygame.draw.ellipse(screen, BLACK, (ahaan_center_x - 18, 295, 22, 10))  # Left shoe
                pygame.draw.ellipse(screen, BLACK, (ahaan_center_x - 6, 295, 22, 10))  # Right shoe
                
                # Rotating gadgets around Ahaan with enhanced graphics
                gadget_radius = 120
                
                gadgets = [
                    ("Nintendo Switch", BLUE, RED),
                    ("PS5", BLACK, WHITE),
                    ("Drums", (139, 69, 19), (160, 82, 45)),
                    ("Apple Watch", BLACK, GREEN)
                ]
                
                for i, (name, color1, color2) in enumerate(gadgets):
                    angle = cutscene_timer * 0.02 + i * (math.pi / 2)
                    gadget_x = ahaan_center_x + int(gadget_radius * math.cos(angle))
                    gadget_y = ahaan_center_y + int(gadget_radius * math.sin(angle))
                    
                    # Add floating sparkles around gadgets
                    sparkle_offset = cutscene_timer * 0.1 + i
                    for j in range(3):
                        sparkle_angle = sparkle_offset + j * (2 * math.pi / 3)
                        sparkle_x = gadget_x + int(25 * math.cos(sparkle_angle))
                        sparkle_y = gadget_y + int(25 * math.sin(sparkle_angle))
                        pygame.draw.circle(screen, YELLOW, (sparkle_x, sparkle_y), 2)
                    
                    if name == "Nintendo Switch":
                        # Main screen (black bezel)
                        pygame.draw.rect(screen, BLACK, (gadget_x - 18, gadget_y - 12, 36, 24))
                        # Screen (blue-gray)
                        pygame.draw.rect(screen, (100, 120, 140), (gadget_x - 15, gadget_y - 9, 30, 18))
                        # Screen reflection
                        pygame.draw.rect(screen, (150, 170, 190), (gadget_x - 13, gadget_y - 7, 8, 4))
                        # Left Joy-Con (blue)
                        pygame.draw.rect(screen, color1, (gadget_x - 25, gadget_y - 15, 12, 30))
                        pygame.draw.circle(screen, (50, 100, 200), (gadget_x - 19, gadget_y - 5), 4)  # Analog stick
                        pygame.draw.rect(screen, (100, 150, 255), (gadget_x - 23, gadget_y + 5, 8, 3))  # D-pad
                        # Right Joy-Con (red)
                        pygame.draw.rect(screen, color2, (gadget_x + 13, gadget_y - 15, 12, 30))
                        pygame.draw.circle(screen, (200, 100, 100), (gadget_x + 19, gadget_y - 5), 4)  # Analog stick
                        # ABXY buttons
                        pygame.draw.circle(screen, YELLOW, (gadget_x + 17, gadget_y + 2), 2)  # Y
                        pygame.draw.circle(screen, GREEN, (gadget_x + 21, gadget_y + 6), 2)   # A
                        pygame.draw.circle(screen, RED, (gadget_x + 21, gadget_y - 2), 2)     # X
                        pygame.draw.circle(screen, BLUE, (gadget_x + 25, gadget_y + 2), 2)   # B
                        
                    elif name == "PS5":
                        # PS5 controller shape (more detailed)
                        pygame.draw.ellipse(screen, color1, (gadget_x - 15, gadget_y - 10, 30, 20))
                        pygame.draw.ellipse(screen, (50, 50, 50), (gadget_x - 13, gadget_y - 8, 26, 16))
                        # Analog sticks
                        pygame.draw.circle(screen, (80, 80, 80), (gadget_x - 8, gadget_y - 2), 3)
                        pygame.draw.circle(screen, (80, 80, 80), (gadget_x + 8, gadget_y + 2), 3)
                        # D-pad
                        pygame.draw.rect(screen, (120, 120, 120), (gadget_x - 10, gadget_y + 2, 6, 2))
                        pygame.draw.rect(screen, (120, 120, 120), (gadget_x - 9, gadget_y + 1, 2, 6))
                        # Face buttons (colored)
                        pygame.draw.circle(screen, BLUE, (gadget_x + 6, gadget_y - 4), 2)    # X (blue)
                        pygame.draw.circle(screen, GREEN, (gadget_x + 10, gadget_y), 2)      # Square (green)
                        pygame.draw.circle(screen, RED, (gadget_x + 6, gadget_y + 4), 2)     # Circle (red)
                        pygame.draw.circle(screen, (255, 100, 200), (gadget_x + 2, gadget_y), 2)  # Triangle (pink)
                        # PlayStation logo
                        pygame.draw.circle(screen, color2, (gadget_x, gadget_y), 4)
                        
                    elif name == "Drums":
                        # Drum set with multiple drums
                        # Main snare drum
                        pygame.draw.ellipse(screen, color1, (gadget_x - 12, gadget_y - 8, 24, 16))
                        pygame.draw.ellipse(screen, color2, (gadget_x - 10, gadget_y - 6, 20, 12))
                        pygame.draw.ellipse(screen, (200, 180, 120), (gadget_x - 8, gadget_y - 4, 16, 8))  # Drum head
                        # Rim
                        pygame.draw.ellipse(screen, (100, 50, 20), (gadget_x - 10, gadget_y - 6, 20, 12), 2)
                        # Hi-hat (smaller drum)
                        pygame.draw.ellipse(screen, (180, 180, 100), (gadget_x - 18, gadget_y - 12, 12, 8))
                        # Drumsticks
                        pygame.draw.line(screen, (160, 120, 80), (gadget_x - 5, gadget_y - 15), (gadget_x + 2, gadget_y - 8), 2)
                        pygame.draw.line(screen, (160, 120, 80), (gadget_x + 5, gadget_y - 15), (gadget_x - 2, gadget_y - 8), 2)
                        # Drumstick tips
                        pygame.draw.circle(screen, (200, 160, 120), (gadget_x - 5, gadget_y - 15), 2)
                        pygame.draw.circle(screen, (200, 160, 120), (gadget_x + 5, gadget_y - 15), 2)
                        
                    elif name == "Apple Watch":
                        # Watch body (rounded rectangle)
                        pygame.draw.rect(screen, color1, (gadget_x - 10, gadget_y - 8, 20, 16))
                        # Rounded corners effect
                        pygame.draw.circle(screen, color1, (gadget_x - 6, gadget_y - 4), 4)
                        pygame.draw.circle(screen, color1, (gadget_x + 6, gadget_y - 4), 4)
                        pygame.draw.circle(screen, color1, (gadget_x - 6, gadget_y + 4), 4)
                        pygame.draw.circle(screen, color1, (gadget_x + 6, gadget_y + 4), 4)
                        # Screen with green activity rings
                        pygame.draw.rect(screen, BLACK, (gadget_x - 8, gadget_y - 6, 16, 12))
                        pygame.draw.circle(screen, color2, (gadget_x, gadget_y), 4, 2)      # Green ring
                        pygame.draw.circle(screen, RED, (gadget_x, gadget_y), 6, 1)        # Red ring
                        pygame.draw.circle(screen, BLUE, (gadget_x, gadget_y), 7, 1)       # Blue ring
                        # Digital crown
                        pygame.draw.rect(screen, (150, 150, 150), (gadget_x + 8, gadget_y - 2, 3, 4))
                        # Watch band
                        pygame.draw.rect(screen, (80, 80, 80), (gadget_x - 12, gadget_y - 2, 4, 4))
                        pygame.draw.rect(screen, (80, 80, 80), (gadget_x + 8, gadget_y - 2, 4, 4))
                
                text1 = pygame.font.Font(None, 32).render("He LOVES gadgets and music!", True, WHITE)
                text2 = pygame.font.Font(None, 28).render("Nintendo Switch • PS5 • Drums • Apple Watch", True, YELLOW)
                screen.blit(text1, ((WIDTH - text1.get_width()) // 2, HEIGHT - 120))
                screen.blit(text2, ((WIDTH - text2.get_width()) // 2, HEIGHT - 80))
                
            elif current_cutscene == "INTRO_AHAAN_SPORTS":
                # Scene 3: Ahaan's sports activities
                title = pygame.font.Font(None, 48).render("Ahaan the Athlete!", True, GOLDEN)
                screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
                
                # Animated sports equipment
                sports_y = 200
                bounce_offset = cutscene_timer * 0.1
                
                # Soccer ball
                ball_x = 100 + int(20 * math.sin(bounce_offset))
                pygame.draw.circle(screen, WHITE, (ball_x, sports_y), 25)
                pygame.draw.circle(screen, BLACK, (ball_x, sports_y), 25, 3)
                for i in range(5):
                    angle = i * (2 * math.pi / 5)
                    line_end_x = ball_x + int(20 * math.cos(angle))
                    line_end_y = sports_y + int(20 * math.sin(angle))
                    pygame.draw.line(screen, BLACK, (ball_x, sports_y), (line_end_x, line_end_y), 2)
                
                # Basketball
                ball_x = 300 + int(15 * math.sin(bounce_offset + 1))
                pygame.draw.circle(screen, (255, 140, 0), (ball_x, sports_y), 25)
                pygame.draw.line(screen, BLACK, (ball_x - 20, sports_y), (ball_x + 20, sports_y), 3)
                pygame.draw.line(screen, BLACK, (ball_x, sports_y - 20), (ball_x, sports_y + 20), 3)
                
                # Swimming pool
                pool_x = 500 + int(10 * math.sin(bounce_offset + 2))
                pygame.draw.rect(screen, (0, 150, 255), (pool_x, sports_y, 60, 30))
                # Water waves
                for i in range(3):
                    wave_y = sports_y + 10 + i * 8 + int(5 * math.sin(cutscene_timer * 0.2 + i))
                    pygame.draw.line(screen, (100, 200, 255), (pool_x + 5, wave_y), (pool_x + 55, wave_y), 2)
                
                # Skateboard
                board_x = 650 + int(25 * math.sin(bounce_offset + 3))
                pygame.draw.rect(screen, (139, 69, 19), (board_x, sports_y + 10, 40, 8))
                pygame.draw.circle(screen, BLACK, (board_x + 5, sports_y + 20), 5)
                pygame.draw.circle(screen, BLACK, (board_x + 35, sports_y + 20), 5)
                
                text1 = pygame.font.Font(None, 32).render("He's an energetic sportsman!", True, WHITE)
                text2 = pygame.font.Font(None, 28).render("Soccer • Basketball • Swimming • Skateboarding", True, YELLOW)
                screen.blit(text1, ((WIDTH - text1.get_width()) // 2, HEIGHT - 120))
                screen.blit(text2, ((WIDTH - text2.get_width()) // 2, HEIGHT - 80))
                
            elif current_cutscene == "INTRO_CHALLENGES":
                # Scene 4: The challenges Ahaan faces
                title = pygame.font.Font(None, 48).render("But Ahaan faces challenges...", True, RED)
                screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
                
                # Dark, ominous background with storm clouds
                for i in range(0, WIDTH, 50):
                    cloud_y = 80 + int(15 * math.sin(cutscene_timer * 0.05 + i * 0.01))
                    pygame.draw.ellipse(screen, (60, 60, 80), (i, cloud_y, 60, 30))
                    pygame.draw.ellipse(screen, (40, 40, 60), (i + 20, cloud_y + 5, 40, 20))
                
                # Lightning flashes occasionally
                if int(cutscene_timer / 60) % 4 == 0 and (cutscene_timer % 60) < 10:
                    # Lightning bolt
                    lightning_points = [
                        (WIDTH//2 - 20, 100),
                        (WIDTH//2 - 10, 140),
                        (WIDTH//2 + 5, 120),
                        (WIDTH//2 + 15, 180),
                        (WIDTH//2 + 25, 160),
                        (WIDTH//2 + 35, 200)
                    ]
                    pygame.draw.lines(screen, YELLOW, False, lightning_points, 3)
                    pygame.draw.lines(screen, WHITE, False, lightning_points, 1)
                
                # Animated challenge icons floating menacingly with enhanced details
                challenges_y = 200
                float_offset = cutscene_timer * 0.08
                
                # Enhanced Homework stack with perspective and shadows
                homework_x = 100 + int(15 * math.sin(float_offset))
                # Shadow
                pygame.draw.ellipse(screen, (50, 50, 50), (homework_x + 5, challenges_y + 45, 65, 15))
                
                for i in range(4):
                    stack_offset = i * 4
                    # Book spine (3D effect)
                    pygame.draw.rect(screen, (180, 140, 100), (homework_x + stack_offset, challenges_y + stack_offset, 60, 40))
                    pygame.draw.rect(screen, WHITE, (homework_x + 3 + stack_offset, challenges_y + 3 + stack_offset, 54, 34))
                    pygame.draw.rect(screen, BLACK, (homework_x + stack_offset, challenges_y + stack_offset, 60, 40), 2)
                    
                    # Book details
                    pygame.draw.rect(screen, RED, (homework_x + 5 + stack_offset, challenges_y + 5 + stack_offset, 50, 8))  # Title bar
                    
                    # Scribbled text lines with more detail
                    for j in range(3):
                        line_y = challenges_y + stack_offset + 18 + j * 6
                        # Main text line
                        pygame.draw.line(screen, BLACK, (homework_x + 8 + stack_offset, line_y), 
                                       (homework_x + 45 + stack_offset, line_y), 1)
                        # Squiggly underlines for difficulty
                        for k in range(0, 35, 3):
                            under_y = line_y + 2 + int(2 * math.sin((k + cutscene_timer) * 0.3))
                            pygame.draw.circle(screen, RED, (homework_x + 10 + k + stack_offset, under_y), 1)
                
                # Math symbols floating around homework
                for i in range(3):
                    symbol_angle = cutscene_timer * 0.1 + i * 2
                    symbol_x = homework_x + 30 + int(25 * math.cos(symbol_angle))
                    symbol_y = challenges_y + 20 + int(15 * math.sin(symbol_angle))
                    symbols = ["∑", "∫", "π"]
                    symbol_font = pygame.font.Font(None, 24)
                    symbol_surf = symbol_font.render(symbols[i], True, RED)
                    screen.blit(symbol_surf, (symbol_x, symbol_y))
                
                # Enhanced Chores (mop and bucket) with cleaning supplies
                chore_x = 300 + int(20 * math.sin(float_offset + 1))
                # Shadow
                pygame.draw.ellipse(screen, (50, 50, 50), (chore_x - 5, challenges_y + 65, 40, 10))
                
                # Mop handle with wood grain
                pygame.draw.rect(screen, (120, 80, 40), (chore_x, challenges_y, 8, 60))
                for grain in range(challenges_y, challenges_y + 60, 8):
                    pygame.draw.line(screen, (100, 60, 20), (chore_x + 1, grain), (chore_x + 6, grain), 1)
                
                # Mop head with individual strands
                pygame.draw.ellipse(screen, (220, 220, 200), (chore_x - 10, challenges_y + 50, 28, 20))
                for strand in range(8):
                    strand_x = chore_x - 8 + strand * 3
                    strand_sway = int(3 * math.sin(cutscene_timer * 0.2 + strand))
                    pygame.draw.line(screen, (200, 200, 180), 
                                   (strand_x, challenges_y + 55), 
                                   (strand_x + strand_sway, challenges_y + 68), 2)
                
                # Bucket with water and bubbles
                pygame.draw.rect(screen, (100, 150, 200), (chore_x + 20, challenges_y + 40, 25, 30))
                pygame.draw.rect(screen, (80, 120, 180), (chore_x + 20, challenges_y + 40, 25, 5))  # Rim
                # Water surface
                pygame.draw.rect(screen, (150, 200, 255), (chore_x + 22, challenges_y + 45, 21, 20))
                # Bubbles
                for bubble in range(4):
                    bubble_x = chore_x + 25 + bubble * 4
                    bubble_y = challenges_y + 50 + int(3 * math.sin(cutscene_timer * 0.3 + bubble))
                    pygame.draw.circle(screen, WHITE, (bubble_x, bubble_y), 2)
                
                # Soap bottle
                pygame.draw.rect(screen, (255, 200, 100), (chore_x + 48, challenges_y + 50, 8, 15))
                pygame.draw.rect(screen, (200, 150, 50), (chore_x + 49, challenges_y + 48, 6, 4))  # Cap
                
                # Enhanced Badminton racket with more detail
                racket_x = 500 + int(12 * math.sin(float_offset + 2))
                # Shadow
                pygame.draw.ellipse(screen, (50, 50, 50), (racket_x - 10, challenges_y + 45, 25, 8))
                
                # Handle with grip texture
                pygame.draw.rect(screen, (120, 80, 40), (racket_x, challenges_y, 6, 40))
                # Grip bands
                for band in range(challenges_y + 5, challenges_y + 35, 4):
                    pygame.draw.rect(screen, (80, 50, 20), (racket_x, band, 6, 2))
                
                # Racket head frame with metallic look
                pygame.draw.ellipse(screen, (200, 180, 160), (racket_x - 15, challenges_y - 25, 36, 50))
                pygame.draw.ellipse(screen, (160, 140, 120), (racket_x - 13, challenges_y - 23, 32, 46), 3)
                
                # String pattern (more detailed crosshatch)
                for i in range(5):
                    string_x = racket_x - 10 + i * 5
                    pygame.draw.line(screen, WHITE, (string_x, challenges_y - 20), (string_x, challenges_y + 5), 1)
                for i in range(6):
                    string_y = challenges_y - 18 + i * 4
                    pygame.draw.line(screen, WHITE, (racket_x - 12, string_y), (racket_x + 18, string_y), 1)
                
                # Shuttlecock in mid-air
                shuttle_x = racket_x + 25 + int(10 * math.cos(cutscene_timer * 0.2))
                shuttle_y = challenges_y - 35 + int(8 * math.sin(cutscene_timer * 0.15))
                pygame.draw.ellipse(screen, WHITE, (shuttle_x, shuttle_y, 8, 12))
                # Feathers
                for feather in range(4):
                    feather_angle = feather * (math.pi / 2)
                    feather_end_x = shuttle_x + 4 + int(6 * math.cos(feather_angle))
                    feather_end_y = shuttle_y + int(6 * math.sin(feather_angle))
                    pygame.draw.line(screen, WHITE, (shuttle_x + 4, shuttle_y), (feather_end_x, feather_end_y), 1)
                
                # Enhanced Shower head with realistic water effects
                shower_x = 650 + int(18 * math.sin(float_offset + 3))
                # Shadow
                pygame.draw.ellipse(screen, (50, 50, 50), (shower_x + 5, challenges_y + 85, 45, 10))
                
                # Shower head body with metallic shine
                pygame.draw.rect(screen, (180, 180, 180), (shower_x, challenges_y, 40, 20))
                pygame.draw.rect(screen, (220, 220, 220), (shower_x + 2, challenges_y + 2, 36, 4))  # Top highlight
                pygame.draw.rect(screen, (140, 140, 140), (shower_x, challenges_y + 16, 40, 4))     # Bottom shadow
                
                # Shower holes in a realistic pattern
                for row in range(3):
                    for col in range(6):
                        hole_x = shower_x + 6 + col * 5
                        hole_y = challenges_y + 5 + row * 4
                        pygame.draw.circle(screen, (100, 100, 100), (hole_x, hole_y), 1)
                
                # Realistic water stream with varying droplet sizes
                for i in range(8):
                    drop_x = shower_x + 5 + i * 4
                    for j in range(6):
                        # Vary droplet fall speed and size
                        fall_speed = 8 + j * 4
                        drop_y = challenges_y + 25 + j * fall_speed + int(5 * math.sin(cutscene_timer * 0.4 + i))
                        drop_size = max(1, 3 - j // 2)  # Smaller drops as they fall
                        # Water color with transparency effect
                        water_alpha = max(100, 255 - j * 30)
                        pygame.draw.circle(screen, (100, 180, 255), (drop_x, drop_y), drop_size)
                        # Add white highlight to drops
                        if drop_size > 1:
                            pygame.draw.circle(screen, WHITE, (drop_x - 1, drop_y - 1), 1)
                
                # Steam effect
                for steam in range(12):
                    steam_x = shower_x + 10 + steam * 3 + int(5 * math.sin(cutscene_timer * 0.1 + steam))
                    steam_y = challenges_y + 80 + int(20 * math.cos(cutscene_timer * 0.05 + steam))
                    steam_size = 3 + int(2 * math.sin(cutscene_timer * 0.08 + steam))
                    pygame.draw.circle(screen, (220, 220, 255), (steam_x, steam_y), steam_size)
                
                # Add threatening red glow around all challenges
                glow_intensity = int(50 + 30 * math.sin(cutscene_timer * 0.1))
                glow_color = (255, 100, 100)
                
                # Create ominous aura around each challenge
                challenge_positions = [
                    (homework_x + 30, challenges_y + 20),
                    (chore_x + 15, challenges_y + 30),
                    (racket_x, challenges_y),
                    (shower_x + 20, challenges_y + 10)
                ]
                
                for pos_x, pos_y in challenge_positions:
                    for radius in range(60, 40, -5):
                        alpha = max(0, glow_intensity - (60 - radius) * 3)
                        # Create glowing ring effect
                        for angle in range(0, 360, 15):
                            ring_x = pos_x + int(radius * math.cos(math.radians(angle)))
                            ring_y = pos_y + int(radius * math.sin(math.radians(angle)))
                            if 0 <= ring_x < WIDTH and 0 <= ring_y < HEIGHT:
                                # Use lighter colors instead of alpha
                                bright_color = (min(255, glow_color[0] + alpha//8), 
                                              min(255, glow_color[1] + alpha//8), 
                                              min(255, glow_color[2] + alpha//8))
                                pygame.draw.circle(screen, bright_color, (ring_x, ring_y), 2)
                
                text1 = pygame.font.Font(None, 32).render("Homework, chores, forced badminton, showers...", True, WHITE)
                text2 = pygame.font.Font(None, 28).render("Parents yelling like villains!", True, RED)
                screen.blit(text1, ((WIDTH - text1.get_width()) // 2, HEIGHT - 120))
                screen.blit(text2, ((WIDTH - text2.get_width()) // 2, HEIGHT - 80))
                
            elif current_cutscene == "SWITCH_GAMING":
                # Scene 5: Ahaan gaming peacefully
                title = pygame.font.Font(None, 48).render("One peaceful day...", True, GREEN)
                screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
                
                # Enhanced room background with depth and details
                # Floor with wood planks
                floor_y = HEIGHT - 50
                for plank in range(0, WIDTH, 60):
                    pygame.draw.rect(screen, (120, 90, 60), (plank, floor_y, 58, 50))
                    pygame.draw.rect(screen, (100, 70, 40), (plank, floor_y, 58, 50), 2)
                    # Wood grain lines
                    for grain in range(floor_y + 5, floor_y + 45, 8):
                        pygame.draw.line(screen, (80, 50, 20), (plank + 5, grain), (plank + 53, grain), 1)
                
                # Walls with texture
                pygame.draw.rect(screen, (140, 120, 100), (50, 150, WIDTH - 100, floor_y - 150))  # Main wall
                pygame.draw.rect(screen, (120, 100, 80), (50, 150, WIDTH - 100, floor_y - 150), 5)   # Wall border
                
                # Wall decorations
                # Picture frame
                pygame.draw.rect(screen, (80, 60, 40), (WIDTH - 150, 170, 80, 60))
                pygame.draw.rect(screen, (200, 180, 160), (WIDTH - 145, 175, 70, 50))
                pygame.draw.rect(screen, (50, 100, 200), (WIDTH - 140, 180, 60, 40))  # Picture (sky)
                pygame.draw.circle(screen, YELLOW, (WIDTH - 120, 190), 8)             # Sun in picture
                
                # Window with curtains
                pygame.draw.rect(screen, (150, 200, 255), (100, 160, 60, 80))  # Window (sky view)
                pygame.draw.rect(screen, (80, 60, 40), (100, 160, 60, 80), 4)  # Window frame
                # Window cross
                pygame.draw.line(screen, (80, 60, 40), (130, 160), (130, 240), 3)
                pygame.draw.line(screen, (80, 60, 40), (100, 200), (160, 200), 3)
                # Curtains
                pygame.draw.rect(screen, (200, 100, 100), (85, 155, 15, 90))   # Left curtain
                pygame.draw.rect(screen, (200, 100, 100), (160, 155, 15, 90))  # Right curtain
                
                # Bookshelf
                pygame.draw.rect(screen, (100, 70, 40), (600, 180, 80, 120))
                for shelf in range(200, 280, 25):
                    pygame.draw.rect(screen, (80, 50, 20), (600, shelf, 80, 3))
                # Books on shelves
                book_colors = [(200, 100, 100), (100, 200, 100), (100, 100, 200), (200, 200, 100)]
                for i, shelf_y in enumerate([185, 210, 235, 260]):
                    for j in range(5):
                        book_x = 605 + j * 14
                        book_color = book_colors[(i + j) % len(book_colors)]
                        pygame.draw.rect(screen, book_color, (book_x, shelf_y, 12, 20))
                        pygame.draw.rect(screen, (50, 50, 50), (book_x, shelf_y, 12, 20), 1)
                
                # Gaming setup - TV/Monitor
                pygame.draw.rect(screen, BLACK, (WIDTH//2 - 80, 180, 160, 90))      # TV screen
                pygame.draw.rect(screen, (40, 40, 40), (WIDTH//2 - 85, 175, 170, 100))  # TV bezel
                pygame.draw.rect(screen, (20, 20, 20), (WIDTH//2 - 10, 270, 20, 15))     # TV stand
                
                # Game on TV screen (Mario-style game)
                pygame.draw.rect(screen, (100, 150, 255), (WIDTH//2 - 75, 185, 150, 80))  # Sky background
                # Clouds on TV
                for cloud in range(3):
                    cloud_x = WIDTH//2 - 60 + cloud * 40 + int(5 * math.sin(cutscene_timer * 0.1 + cloud))
                    pygame.draw.ellipse(screen, WHITE, (cloud_x, 190 + cloud * 5, 25, 15))
                # Ground on TV
                pygame.draw.rect(screen, GREEN, (WIDTH//2 - 75, 245, 150, 20))
                # Mario character on TV
                mario_x = WIDTH//2 - 30 + int(10 * math.sin(cutscene_timer * 0.2))
                pygame.draw.rect(screen, RED, (mario_x, 235, 12, 10))        # Mario body
                pygame.draw.circle(screen, SKIN, (mario_x + 6, 230), 4)     # Mario head
                pygame.draw.rect(screen, BLUE, (mario_x + 2, 240, 8, 5))    # Mario legs
                
                # Cozy lighting - lamp
                pygame.draw.rect(screen, (120, 100, 80), (520, 200, 8, 40))   # Lamp post
                pygame.draw.ellipse(screen, (255, 240, 200), (510, 185, 28, 20))  # Lamp shade
                # Light glow effect
                for radius in range(40, 20, -4):
                    glow_alpha = max(0, 60 - (40 - radius) * 3)
                    # Create soft glow around lamp
                    pygame.draw.circle(screen, (255, 240, 150), (524, 195), radius, 1)
                
                # Carpet/rug under gaming area
                pygame.draw.ellipse(screen, (150, 100, 200), (WIDTH//2 - 120, floor_y - 40, 240, 60))
                pygame.draw.ellipse(screen, (130, 80, 180), (WIDTH//2 - 115, floor_y - 35, 230, 50))
                # Rug pattern
                for ring in range(3):
                    ring_radius = 80 + ring * 15
                    pygame.draw.ellipse(screen, (100 + ring * 20, 60 + ring * 10, 160 + ring * 10), 
                                      (WIDTH//2 - ring_radius//2, floor_y - 20 - ring * 2, ring_radius, 30), 2)
                
                # Enhanced Ahaan sitting and gaming with better proportions
                ahaan_x, ahaan_y = WIDTH // 2 - 20, 250
                
                # Gaming chair/cushion
                pygame.draw.ellipse(screen, (80, 60, 40), (ahaan_x - 25, ahaan_y + 45, 90, 45))  # Chair base
                pygame.draw.rect(screen, (100, 80, 60), (ahaan_x - 20, ahaan_y + 30, 80, 20))    # Chair back
                
                # Ahaan's body with more detail
                # Head with detailed features
                pygame.draw.ellipse(screen, SKIN, (ahaan_x, ahaan_y, 40, 50))
                pygame.draw.ellipse(screen, (240, 200, 160), (ahaan_x + 2, ahaan_y + 2, 36, 46))  # Face highlight
                
                # Hair
                pygame.draw.ellipse(screen, BROWN, (ahaan_x - 5, ahaan_y - 5, 50, 30))
                pygame.draw.circle(screen, (120, 80, 40), (ahaan_x + 5, ahaan_y), 8)    # Hair tuft left
                pygame.draw.circle(screen, (120, 80, 40), (ahaan_x + 35, ahaan_y), 8)   # Hair tuft right
                
                # Concentrated gaming expression
                pygame.draw.ellipse(screen, WHITE, (ahaan_x + 8, ahaan_y + 15, 8, 10))   # Left eye
                pygame.draw.ellipse(screen, WHITE, (ahaan_x + 24, ahaan_y + 15, 8, 10))  # Right eye
                pygame.draw.circle(screen, BLACK, (ahaan_x + 11, ahaan_y + 19), 3)       # Left pupil
                pygame.draw.circle(screen, BLACK, (ahaan_x + 27, ahaan_y + 19), 3)       # Right pupil
                pygame.draw.circle(screen, WHITE, (ahaan_x + 12, ahaan_y + 18), 1)       # Left eye shine
                pygame.draw.circle(screen, WHITE, (ahaan_x + 28, ahaan_y + 18), 1)       # Right eye shine
                
                # Concentrated expression - slightly furrowed brow
                pygame.draw.line(screen, (200, 160, 120), (ahaan_x + 6, ahaan_y + 12), (ahaan_x + 12, ahaan_y + 14), 2)
                pygame.draw.line(screen, (200, 160, 120), (ahaan_x + 28, ahaan_y + 14), (ahaan_x + 34, ahaan_y + 12), 2)
                
                # Slight smile of contentment
                pygame.draw.arc(screen, BLACK, (ahaan_x + 12, ahaan_y + 28, 16, 8), 0, math.pi, 2)
                
                # Body in relaxed gaming position
                pygame.draw.rect(screen, BLUE, (ahaan_x - 10, ahaan_y + 50, 60, 70))     # Main shirt
                pygame.draw.rect(screen, (100, 150, 255), (ahaan_x - 8, ahaan_y + 52, 56, 66))  # Shirt highlight
                
                # Arms holding the Nintendo Switch
                pygame.draw.rect(screen, SKIN, (ahaan_x - 15, ahaan_y + 60, 20, 35))     # Left arm
                pygame.draw.rect(screen, SKIN, (ahaan_x + 35, ahaan_y + 60, 20, 35))     # Right arm
                
                # Legs in comfortable position
                pygame.draw.rect(screen, BLUE, (ahaan_x - 5, ahaan_y + 110, 25, 40))     # Left leg (jeans)
                pygame.draw.rect(screen, BLUE, (ahaan_x + 20, ahaan_y + 110, 25, 40))    # Right leg (jeans)
                
                # Socks and feet
                pygame.draw.rect(screen, WHITE, (ahaan_x - 3, ahaan_y + 145, 21, 15))    # Left sock
                pygame.draw.rect(screen, WHITE, (ahaan_x + 22, ahaan_y + 145, 21, 15))   # Right sock
                
                # Enhanced Nintendo Switch with detailed design
                switch_x, switch_y = ahaan_x + 10, ahaan_y + 75
                
                # Switch main body (more detailed)
                pygame.draw.rect(screen, BLACK, (switch_x, switch_y, 40, 25))
                pygame.draw.rect(screen, (40, 40, 40), (switch_x + 1, switch_y + 1, 38, 23))  # Bezel
                
                # Left Joy-Con with enhanced detail
                pygame.draw.rect(screen, BLUE, (switch_x - 12, switch_y + 1, 14, 23))
                pygame.draw.rect(screen, (100, 150, 255), (switch_x - 11, switch_y + 2, 12, 21))  # Highlight
                pygame.draw.circle(screen, (50, 100, 200), (switch_x - 6, switch_y + 8), 3)       # Analog stick
                pygame.draw.rect(screen, (80, 120, 255), (switch_x - 9, switch_y + 15, 6, 2))     # D-pad horizontal
                pygame.draw.rect(screen, (80, 120, 255), (switch_x - 7, switch_y + 13, 2, 6))     # D-pad vertical
                
                # Right Joy-Con with enhanced detail  
                pygame.draw.rect(screen, RED, (switch_x + 38, switch_y + 1, 14, 23))
                pygame.draw.rect(screen, (255, 100, 100), (switch_x + 39, switch_y + 2, 12, 21))  # Highlight
                pygame.draw.circle(screen, (200, 50, 50), (switch_x + 45, switch_y + 8), 3)       # Analog stick
                # ABXY buttons with proper colors
                pygame.draw.circle(screen, YELLOW, (switch_x + 43, switch_y + 13), 1.5)  # Y button
                pygame.draw.circle(screen, GREEN, (switch_x + 47, switch_y + 16), 1.5)   # A button  
                pygame.draw.circle(screen, BLUE, (switch_x + 49, switch_y + 13), 1.5)    # X button
                pygame.draw.circle(screen, RED, (switch_x + 47, switch_y + 10), 1.5)     # B button
                
                # Animated game screen with realistic game graphics
                game_colors = [
                    (100, 200, 100),  # Green (grass level)
                    (100, 150, 255),  # Blue (water level)  
                    (255, 200, 100),  # Orange (desert level)
                    (200, 100, 255)   # Purple (night level)
                ]
                current_color = game_colors[int(cutscene_timer / 60) % len(game_colors)]
                
                # Game screen background
                pygame.draw.rect(screen, current_color, (switch_x + 3, switch_y + 3, 34, 19))
                
                # Mini game character on screen
                char_x = switch_x + 8 + int(8 * math.sin(cutscene_timer * 0.1))
                pygame.draw.rect(screen, RED, (char_x, switch_y + 12, 4, 6))      # Game character body
                pygame.draw.circle(screen, SKIN, (char_x + 2, switch_y + 10), 2)  # Game character head
                
                # Game UI elements on screen
                pygame.draw.rect(screen, WHITE, (switch_x + 25, switch_y + 5, 12, 3))  # Health bar background
                pygame.draw.rect(screen, GREEN, (switch_x + 26, switch_y + 6, 8, 1))   # Health bar
                
                # Screen reflection effect
                pygame.draw.rect(screen, (200, 200, 255), (switch_x + 4, switch_y + 4, 8, 3))  # Screen glare
                
                # Soft glow from the Switch screen
                for glow in range(3):
                    glow_color = (*current_color, 30 + glow * 10)
                    # Create subtle glow effect around the switch
                    pygame.draw.rect(screen, current_color, 
                                   (switch_x - 2 - glow, switch_y - 2 - glow, 
                                    44 + glow * 2, 29 + glow * 2), 1)
                
                # Content expression showing gaming enjoyment
                # Add slight head movement for immersion
                head_sway = int(2 * math.sin(cutscene_timer * 0.05))
                
                # Peaceful room ambiance - floating dust particles in light
                for particle in range(15):
                    particle_x = 100 + (particle * 47 + cutscene_timer) % (WIDTH - 200)
                    particle_y = 160 + int(30 * math.sin(cutscene_timer * 0.03 + particle))
                    pygame.draw.circle(screen, (255, 255, 200), (particle_x, particle_y), 1)
                
                text1 = pygame.font.Font(None, 36).render("Ahaan was gaming on his Nintendo Switch", True, WHITE)
                text2 = pygame.font.Font(None, 32).render("Peaceful and happy...", True, GREEN)
                screen.blit(text1, ((WIDTH - text1.get_width()) // 2, HEIGHT - 120))
                screen.blit(text2, ((WIDTH - text2.get_width()) // 2, HEIGHT - 80))
                
            elif current_cutscene == "MOM_APPEARS":
                # Scene 6: Mom suddenly appears
                title = pygame.font.Font(None, 48).render("Suddenly...", True, RED)
                screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
                
                # Room background (same as before)
                pygame.draw.rect(screen, (100, 80, 60), (50, 150, WIDTH - 100, HEIGHT - 200))
                pygame.draw.rect(screen, (80, 60, 40), (50, 150, WIDTH - 100, HEIGHT - 200), 5)
                
                # Ahaan (now scared)
                ahaan_x, ahaan_y = WIDTH // 2 - 20, 250
                pygame.draw.ellipse(screen, SKIN, (ahaan_x, ahaan_y, 40, 50))  # Head
                pygame.draw.rect(screen, BLUE, (ahaan_x - 10, ahaan_y + 50, 60, 70))  # Body
                
                # Scared expression
                pygame.draw.circle(screen, BLACK, (ahaan_x + 10, ahaan_y + 15), 4)  # Wide eyes
                pygame.draw.circle(screen, BLACK, (ahaan_x + 30, ahaan_y + 15), 4)
                pygame.draw.ellipse(screen, BLACK, (ahaan_x + 15, ahaan_y + 30, 10, 8))  # Open mouth
                
                # Mom appearing with dramatic effect
                mom_entrance = min(cutscene_timer / 60.0, 1.0)
                mom_x = int(100 - 50 + mom_entrance * 50)
                mom_y = 200
                
                # Mom character (larger and more imposing)
                pygame.draw.ellipse(screen, SKIN, (mom_x, mom_y, 50, 60))  # Head
                pygame.draw.rect(screen, (200, 100, 100), (mom_x - 10, mom_y + 60, 70, 90))  # Body
                pygame.draw.rect(screen, SKIN, (mom_x - 15, mom_y + 130, 30, 50))  # Left leg
                pygame.draw.rect(screen, SKIN, (mom_x + 55, mom_y + 130, 30, 50))  # Right leg
                
                # Angry expression
                pygame.draw.line(screen, BLACK, (mom_x + 15, mom_y + 20), (mom_x + 20, mom_y + 25), 3)  # Angry eyebrow
                pygame.draw.line(screen, BLACK, (mom_x + 35, mom_y + 25), (mom_x + 40, mom_y + 20), 3)
                pygame.draw.circle(screen, BLACK, (mom_x + 18, mom_y + 30), 3)  # Eyes
                pygame.draw.circle(screen, BLACK, (mom_x + 37, mom_y + 30), 3)
                pygame.draw.arc(screen, BLACK, (mom_x + 15, mom_y + 40, 20, 10), math.pi, 2 * math.pi, 3)  # Frown
                
                # Speech bubble with text
                if cutscene_timer > 60:
                    bubble_x, bubble_y = mom_x + 60, mom_y - 20
                    pygame.draw.ellipse(screen, WHITE, (bubble_x, bubble_y, 200, 60))
                    pygame.draw.ellipse(screen, BLACK, (bubble_x, bubble_y, 200, 60), 3)
                    
                    text = pygame.font.Font(None, 28).render("No more games!", True, RED)
                    text2 = pygame.font.Font(None, 24).render("You have homework!", True, BLACK)
                    screen.blit(text, (bubble_x + 10, bubble_y + 10))
                    screen.blit(text2, (bubble_x + 10, bubble_y + 35))
                
                # Action lines for dramatic effect
                for i in range(8):
                    line_angle = i * (2 * math.pi / 8) + cutscene_timer * 0.1
                    line_x = mom_x + 25 + int(80 * math.cos(line_angle))
                    line_y = mom_y + 75 + int(80 * math.sin(line_angle))
                    end_x = mom_x + 25 + int(100 * math.cos(line_angle))
                    end_y = mom_y + 75 + int(100 * math.sin(line_angle))
                    pygame.draw.line(screen, YELLOW, (line_x, line_y), (end_x, end_y), 2)
                
                instruction = pygame.font.Font(None, 32).render("Mom suddenly appears!", True, WHITE)
                screen.blit(instruction, ((WIDTH - instruction.get_width()) // 2, HEIGHT - 100))
                
            elif current_cutscene == "SWITCH_BREAKS":
                # Scene 7: Nintendo Switch breaks apart
                title = pygame.font.Font(None, 48).render("OH NO!", True, RED)
                screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
                
                # Mom running away with pieces
                mom_x = 150 + int(cutscene_timer * 2)
                mom_y = 200
                
                if mom_x < WIDTH:
                    # Mom character running
                    pygame.draw.ellipse(screen, SKIN, (mom_x, mom_y, 40, 50))  # Head
                    pygame.draw.rect(screen, (200, 100, 100), (mom_x - 5, mom_y + 50, 50, 70))  # Body
                    
                    # Running legs animation
                    leg_offset = int(10 * math.sin(cutscene_timer * 0.3))
                    pygame.draw.rect(screen, SKIN, (mom_x + 5, mom_y + 120, 15, 40 + leg_offset))  # Left leg
                    pygame.draw.rect(screen, SKIN, (mom_x + 25, mom_y + 120, 15, 40 - leg_offset))  # Right leg
                    
                    # Movement lines
                    for i in range(3):
                        line_x = mom_x - 20 - i * 10
                        pygame.draw.line(screen, WHITE, (line_x, mom_y + 60 + i * 5), (line_x + 15, mom_y + 65 + i * 5), 2)
                
                # Nintendo Switch pieces flying apart
                explosion_progress = cutscene_timer / 120.0
                center_x, center_y = WIDTH // 2, HEIGHT // 2
                
                # Left controller flying
                left_x = center_x - int(150 * explosion_progress) - 50
                left_y = center_y - int(100 * explosion_progress)
                pygame.draw.rect(screen, BLUE, (left_x, left_y, 25, 40))
                pygame.draw.circle(screen, BLACK, (left_x + 12, left_y + 15), 5)
                
                # Screen piece
                screen_x = center_x - 30
                screen_y = center_y - int(80 * explosion_progress)
                pygame.draw.rect(screen, BLACK, (screen_x, screen_y, 60, 35))
                pygame.draw.rect(screen, (100, 100, 100), (screen_x + 3, screen_y + 3, 54, 29))
                
                # Right controller flying
                right_x = center_x + int(150 * explosion_progress) + 25
                right_y = center_y - int(120 * explosion_progress)
                pygame.draw.rect(screen, RED, (right_x, right_y, 25, 40))
                pygame.draw.circle(screen, BLACK, (right_x + 12, right_y + 15), 5)
                
                # Explosion effect
                if explosion_progress < 0.5:
                    for i in range(12):
                        spark_angle = i * (2 * math.pi / 12)
                        spark_dist = int(60 * explosion_progress)
                        spark_x = center_x + int(spark_dist * math.cos(spark_angle))
                        spark_y = center_y + int(spark_dist * math.sin(spark_angle))
                        pygame.draw.circle(screen, YELLOW, (spark_x, spark_y), 3)
                
                text1 = pygame.font.Font(None, 36).render("The Nintendo Switch breaks apart!", True, WHITE)
                text2 = pygame.font.Font(None, 32).render("Three pieces scattered!", True, RED)
                screen.blit(text1, ((WIDTH - text1.get_width()) // 2, HEIGHT - 120))
                screen.blit(text2, ((WIDTH - text2.get_width()) // 2, HEIGHT - 80))
                
            elif current_cutscene == "CHASE_BEGINS":
                # Scene 8: The chase begins
                title = pygame.font.Font(None, 48).render("The Chase is On!", True, GOLDEN)
                screen.blit(title, ((WIDTH - title.get_width()) // 2, 50))
                
                # Dynamic background with motion blur effect
                # Ground with motion lines
                ground_y = 320
                for i in range(0, WIDTH + 50, 40):
                    motion_x = i - int(cutscene_timer * 2) % 40
                    pygame.draw.rect(screen, (80, 120, 80), (motion_x, ground_y, 35, 80))      # Grass patches
                    pygame.draw.rect(screen, (60, 100, 60), (motion_x + 2, ground_y + 2, 31, 76))  # Grass highlight
                    
                # Background hills with parallax effect
                for hill in range(3):
                    hill_speed = 0.5 + hill * 0.3
                    hill_x = WIDTH - 200 - int(cutscene_timer * hill_speed) % (WIDTH + 400)
                    hill_y = 200 + hill * 20
                    hill_color = (100 - hill * 20, 150 - hill * 15, 100 - hill * 10)
                    pygame.draw.ellipse(screen, hill_color, (hill_x, hill_y, 300, 100))
                
                # Fast-moving clouds
                for cloud in range(4):
                    cloud_speed = 1.5 + cloud * 0.5
                    cloud_x = WIDTH - int(cutscene_timer * cloud_speed) % (WIDTH + 100)
                    cloud_y = 100 + cloud * 15
                    pygame.draw.ellipse(screen, WHITE, (cloud_x, cloud_y, 60, 30))
                    pygame.draw.ellipse(screen, WHITE, (cloud_x + 20, cloud_y - 5, 40, 25))
                
                # Enhanced Ahaan running with detailed animation
                ahaan_x = 100 + int(cutscene_timer * 1.5)
                ahaan_y = 250
                
                # Motion blur trail effect
                for trail in range(5):
                    trail_alpha = 255 - trail * 50
                    trail_x = ahaan_x - trail * 8
                    if trail_alpha > 0:
                        # Faded body trail (using lighter colors instead of alpha)
                        trail_skin = (min(255, SKIN[0] + trail * 10), min(255, SKIN[1] + trail * 10), min(255, SKIN[2] + trail * 10))
                        trail_blue = (min(255, BLUE[0] + trail * 20), min(255, BLUE[1] + trail * 20), min(255, BLUE[2] + trail * 20))
                        pygame.draw.ellipse(screen, trail_skin, (trail_x + trail*2, ahaan_y + trail, 35-trail*2, 45-trail*2))
                        pygame.draw.rect(screen, trail_blue, (trail_x - 5 + trail*2, ahaan_y + 45 + trail, 45-trail*4, 60-trail*4))
                
                # Main character with enhanced detail
                # Head with hair flowing from speed
                pygame.draw.ellipse(screen, SKIN, (ahaan_x, ahaan_y, 35, 45))
                pygame.draw.ellipse(screen, (240, 200, 160), (ahaan_x + 2, ahaan_y + 2, 31, 41))  # Face highlight
                
                # Hair with wind effect
                hair_flow = int(8 * math.sin(cutscene_timer * 0.3))
                pygame.draw.ellipse(screen, BROWN, (ahaan_x - 8 - hair_flow, ahaan_y - 5, 45 + hair_flow, 25))
                pygame.draw.circle(screen, (120, 80, 40), (ahaan_x + 5 - hair_flow//2, ahaan_y), 8)   # Hair tuft
                pygame.draw.circle(screen, (120, 80, 40), (ahaan_x + 25 - hair_flow//3, ahaan_y + 2), 8)  # Hair tuft
                
                # Dynamic facial expression showing determination and effort
                # Eyes with focus
                pygame.draw.ellipse(screen, WHITE, (ahaan_x + 6, ahaan_y + 15, 8, 10))
                pygame.draw.ellipse(screen, WHITE, (ahaan_x + 21, ahaan_y + 15, 8, 10))
                pygame.draw.circle(screen, BLACK, (ahaan_x + 9, ahaan_y + 19), 3)
                pygame.draw.circle(screen, BLACK, (ahaan_x + 24, ahaan_y + 19), 3)
                # Intense gaze
                pygame.draw.circle(screen, WHITE, (ahaan_x + 10, ahaan_y + 18), 1)
                pygame.draw.circle(screen, WHITE, (ahaan_x + 25, ahaan_y + 18), 1)
                
                # Determined eyebrows
                pygame.draw.line(screen, (200, 160, 120), (ahaan_x + 4, ahaan_y + 12), (ahaan_x + 10, ahaan_y + 14), 2)
                pygame.draw.line(screen, (200, 160, 120), (ahaan_x + 25, ahaan_y + 14), (ahaan_x + 31, ahaan_y + 12), 2)
                
                # Open mouth showing effort
                pygame.draw.ellipse(screen, BLACK, (ahaan_x + 12, ahaan_y + 28, 8, 6))
                pygame.draw.ellipse(screen, (200, 100, 100), (ahaan_x + 13, ahaan_y + 29, 6, 4))  # Tongue
                
                # Body with athletic shirt
                pygame.draw.rect(screen, BLUE, (ahaan_x - 5, ahaan_y + 45, 45, 60))
                pygame.draw.rect(screen, (100, 150, 255), (ahaan_x - 3, ahaan_y + 47, 41, 56))  # Shirt highlight
                # Racing stripes on shirt
                pygame.draw.rect(screen, WHITE, (ahaan_x + 5, ahaan_y + 50, 3, 50))
                pygame.draw.rect(screen, RED, (ahaan_x + 27, ahaan_y + 50, 3, 50))
                
                # Enhanced running leg animation with realistic movement
                leg_cycle = cutscene_timer * 0.6  # Faster leg movement for urgency
                left_leg_offset = int(20 * math.sin(leg_cycle))
                right_leg_offset = int(20 * math.sin(leg_cycle + math.pi))
                
                # Left leg with knee bend
                left_thigh_angle = math.sin(leg_cycle) * 0.3
                left_leg_x = ahaan_x + 5 + int(5 * math.cos(left_thigh_angle))
                left_leg_y = ahaan_y + 105
                pygame.draw.rect(screen, BLUE, (left_leg_x, left_leg_y, 12, 25))  # Thigh
                pygame.draw.rect(screen, SKIN, (left_leg_x + 2, left_leg_y + 20, 8, 15 + max(0, left_leg_offset)))  # Shin
                
                # Right leg with knee bend
                right_thigh_angle = math.sin(leg_cycle + math.pi) * 0.3
                right_leg_x = ahaan_x + 23 + int(5 * math.cos(right_thigh_angle))
                right_leg_y = ahaan_y + 105
                pygame.draw.rect(screen, BLUE, (right_leg_x, right_leg_y, 12, 25))  # Thigh
                pygame.draw.rect(screen, SKIN, (right_leg_x + 2, right_leg_y + 20, 8, 15 + max(0, right_leg_offset)))  # Shin
                
                # Running shoes with motion
                shoe_bounce = int(3 * math.sin(leg_cycle * 2))
                pygame.draw.ellipse(screen, BLACK, (left_leg_x, left_leg_y + 35 + left_leg_offset + shoe_bounce, 15, 8))
                pygame.draw.ellipse(screen, BLACK, (right_leg_x, right_leg_y + 35 + right_leg_offset - shoe_bounce, 15, 8))
                # Shoe highlights
                pygame.draw.ellipse(screen, (80, 80, 80), (left_leg_x + 2, left_leg_y + 36 + left_leg_offset + shoe_bounce, 11, 4))
                pygame.draw.ellipse(screen, (80, 80, 80), (right_leg_x + 2, right_leg_y + 36 + right_leg_offset - shoe_bounce, 11, 4))
                
                # Enhanced arm pumping with realistic swing
                arm_cycle = cutscene_timer * 0.6
                left_arm_swing = int(15 * math.sin(arm_cycle))
                right_arm_swing = int(15 * math.sin(arm_cycle + math.pi))
                
                # Left arm with shoulder to hand
                left_arm_x = ahaan_x - 15 + int(5 * math.cos(arm_cycle))
                left_arm_y = ahaan_y + 55 + left_arm_swing
                pygame.draw.rect(screen, SKIN, (left_arm_x, left_arm_y, 15, 25))
                pygame.draw.ellipse(screen, SKIN, (left_arm_x + 12, left_arm_y + 20, 8, 8))  # Fist
                
                # Right arm with shoulder to hand
                right_arm_x = ahaan_x + 35 + int(5 * math.cos(arm_cycle + math.pi))
                right_arm_y = ahaan_y + 55 + right_arm_swing
                pygame.draw.rect(screen, SKIN, (right_arm_x, right_arm_y, 15, 25))
                pygame.draw.ellipse(screen, SKIN, (right_arm_x - 3, right_arm_y + 20, 8, 8))  # Fist
                
                # Dynamic speed lines with varying intensity
                for i in range(8):
                    line_intensity = 255 - i * 30
                    line_x = ahaan_x - 40 - i * 20
                    line_length = 25 + i * 3
                    line_thickness = max(1, 4 - i//2)
                    
                    # Multiple speed line layers
                    for j in range(3):
                        speed_line_y = ahaan_y + 40 + j * 15 + int(5 * math.sin(cutscene_timer * 0.2 + i + j))
                        pygame.draw.line(screen, (line_intensity, line_intensity, line_intensity), 
                                       (line_x, speed_line_y), (line_x + line_length, speed_line_y + 5), line_thickness)
                
                # Enhanced floating Nintendo Switch parts with particle effects
                for i, (color, offset_x, offset_y) in enumerate([(BLUE, -80, -30), (BLACK, 0, -50), (RED, 80, -20)]):
                    part_x = ahaan_x + 250 + offset_x + int(25 * math.sin(cutscene_timer * 0.12 + i))
                    part_y = 160 + offset_y + int(20 * math.cos(cutscene_timer * 0.08 + i))
                    
                    # Magical glow around parts
                    for glow_radius in range(20, 5, -3):
                        glow_alpha = max(0, 100 - (20 - glow_radius) * 8)
                        # Use lighter colors instead of alpha
                        if color != BLACK:
                            glow_color = (min(255, color[0] + glow_alpha//6), 
                                        min(255, color[1] + glow_alpha//6), 
                                        min(255, color[2] + glow_alpha//6))
                        else:
                            glow_color = (100 + glow_alpha//6, 100 + glow_alpha//6, 255)
                        pygame.draw.circle(screen, glow_color, (part_x + 15, part_y + 12), glow_radius, 1)
                    
                    # Sparkling particles around each part
                    for spark in range(6):
                        spark_angle = (cutscene_timer * 0.1 + spark + i) * (2 * math.pi / 6)
                        spark_distance = 30 + int(10 * math.sin(cutscene_timer * 0.15 + spark))
                        spark_x = part_x + 15 + int(spark_distance * math.cos(spark_angle))
                        spark_y = part_y + 12 + int(spark_distance * math.sin(spark_angle))
                        spark_size = 2 + int(2 * math.sin(cutscene_timer * 0.2 + spark))
                        pygame.draw.circle(screen, YELLOW, (spark_x, spark_y), spark_size)
                        pygame.draw.circle(screen, WHITE, (spark_x - 1, spark_y - 1), max(1, spark_size - 1))
                    
                    if color == BLACK:  # Enhanced Screen piece
                        pygame.draw.rect(screen, color, (part_x, part_y, 35, 25))
                        pygame.draw.rect(screen, (60, 60, 60), (part_x + 2, part_y + 2, 31, 21))  # Bezel
                        pygame.draw.rect(screen, (100, 150, 200), (part_x + 4, part_y + 4, 27, 17))  # Screen
                        # Screen glint
                        pygame.draw.rect(screen, WHITE, (part_x + 6, part_y + 6, 8, 3))
                        # Nintendo logo hint
                        pygame.draw.circle(screen, RED, (part_x + 17, part_y + 12), 3)
                        
                    else:  # Enhanced Controller pieces
                        pygame.draw.rect(screen, color, (part_x, part_y, 18, 30))
                        pygame.draw.rect(screen, (255, 255, 255) if color == BLUE else (255, 200, 200), 
                                       (part_x + 2, part_y + 2, 14, 26))  # Controller highlight
                        pygame.draw.circle(screen, (50, 50, 50), (part_x + 9, part_y + 12), 4)  # Analog stick
                        pygame.draw.circle(screen, (100, 100, 100), (part_x + 9, part_y + 12), 3)  # Stick top
                        
                        if color == BLUE:  # Left controller details
                            pygame.draw.rect(screen, (80, 120, 255), (part_x + 4, part_y + 20, 6, 2))  # D-pad horizontal
                            pygame.draw.rect(screen, (80, 120, 255), (part_x + 6, part_y + 18, 2, 6))  # D-pad vertical
                        else:  # Right controller details
                            pygame.draw.circle(screen, YELLOW, (part_x + 5, part_y + 18), 1)   # Y
                            pygame.draw.circle(screen, GREEN, (part_x + 13, part_y + 22), 1)   # A
                            pygame.draw.circle(screen, RED, (part_x + 13, part_y + 18), 1)     # X
                            pygame.draw.circle(screen, BLUE, (part_x + 9, part_y + 22), 1)    # B
                
                # Trail of dust kicked up by running
                for dust in range(12):
                    dust_x = ahaan_x - 20 - dust * 15 + int(5 * random.random())
                    dust_y = ground_y + 5 + int(8 * math.sin(cutscene_timer * 0.3 + dust))
                    dust_size = max(1, 4 - dust//3)
                    dust_color = (150 + dust * 5, 130 + dust * 4, 100 + dust * 3)
                    pygame.draw.circle(screen, dust_color, (dust_x, dust_y), dust_size)
                
                text1 = pygame.font.Font(None, 36).render("Ahaan must collect all three pieces!", True, WHITE)
                text2 = pygame.font.Font(None, 32).render("Defeat mom bosses to get them back!", True, YELLOW)
                screen.blit(text1, ((WIDTH - text1.get_width()) // 2, HEIGHT - 120))
                screen.blit(text2, ((WIDTH - text2.get_width()) // 2, HEIGHT - 80))
                
            elif current_cutscene == "READY_TO_PLAY":
                # Scene 9: Ready to start the adventure
                title = pygame.font.Font(None, 56).render("Are You Ready?", True, GOLDEN)
                screen.blit(title, ((WIDTH - title.get_width()) // 2, 100))
                
                # Large Ahaan character in hero pose
                ahaan_x, ahaan_y = WIDTH // 2 - 25, 200
                
                # Hero pose
                pygame.draw.ellipse(screen, SKIN, (ahaan_x, ahaan_y, 50, 60))  # Head
                pygame.draw.rect(screen, BLUE, (ahaan_x - 10, ahaan_y + 60, 70, 80))  # Body
                pygame.draw.rect(screen, SKIN, (ahaan_x - 20, ahaan_y + 80, 20, 40))  # Left arm (raised)
                pygame.draw.rect(screen, SKIN, (ahaan_x + 70, ahaan_y + 90, 20, 40))  # Right arm
                pygame.draw.rect(screen, SKIN, (ahaan_x + 10, ahaan_y + 140, 15, 50))  # Left leg
                pygame.draw.rect(screen, SKIN, (ahaan_x + 35, ahaan_y + 140, 15, 50))  # Right leg
                
                # Confident expression
                pygame.draw.circle(screen, BLACK, (ahaan_x + 18, ahaan_y + 25), 4)  # Eyes
                pygame.draw.circle(screen, BLACK, (ahaan_x + 32, ahaan_y + 25), 4)
                pygame.draw.arc(screen, BLACK, (ahaan_x + 15, ahaan_y + 35, 20, 15), 0, math.pi, 4)  # Smile
                
                # Glowing aura effect
                aura_radius = 80 + int(20 * math.sin(cutscene_timer * 0.1))
                for radius in range(aura_radius, aura_radius - 30, -5):
                    alpha = max(0, 255 - (aura_radius - radius) * 8)
                    color = (255, 215, 0, alpha // 4)  # Golden color with transparency effect
                    pygame.draw.circle(screen, (255, 215, 0), (ahaan_x + 25, ahaan_y + 100), radius, 2)
                
                # Floating Nintendo Switch parts around him
                for i in range(3):
                    angle = cutscene_timer * 0.05 + i * (2 * math.pi / 3)
                    orbit_x = ahaan_x + 25 + int(60 * math.cos(angle))
                    orbit_y = ahaan_y + 100 + int(40 * math.sin(angle))
                    
                    if i == 0:  # Left controller
                        pygame.draw.rect(screen, BLUE, (orbit_x, orbit_y, 20, 30))
                        pygame.draw.circle(screen, BLACK, (orbit_x + 10, orbit_y + 12), 4)
                    elif i == 1:  # Screen
                        pygame.draw.rect(screen, BLACK, (orbit_x, orbit_y, 35, 25))
                        pygame.draw.rect(screen, (100, 255, 100), (orbit_x + 3, orbit_y + 3, 29, 19))
                    else:  # Right controller
                        pygame.draw.rect(screen, RED, (orbit_x, orbit_y, 20, 30))
                        pygame.draw.circle(screen, BLACK, (orbit_x + 10, orbit_y + 12), 4)
                
                subtitle = pygame.font.Font(None, 40).render("Help Ahaan get his Nintendo Switch back!", True, WHITE)
                instruction1 = pygame.font.Font(None, 32).render("Press SPACE to begin the adventure!", True, YELLOW)
                instruction2 = pygame.font.Font(None, 24).render("(Press S to skip story)", True, (150, 150, 150))
                
                screen.blit(subtitle, ((WIDTH - subtitle.get_width()) // 2, HEIGHT - 150))
                screen.blit(instruction1, ((WIDTH - instruction1.get_width()) // 2, HEIGHT - 100))
                screen.blit(instruction2, ((WIDTH - instruction2.get_width()) // 2, HEIGHT - 60))
            
            # Common controls for all cutscenes
            controls = pygame.font.Font(None, 24).render("SPACE: Next | S: Skip Story", True, WHITE)
            screen.blit(controls, (10, HEIGHT - 30))
            
            pygame.display.flip()
            
            # Handle input
            if not hasattr(main, 'story_last_space'):
                main.story_last_space = False
            if keys[pygame.K_SPACE]:
                if not main.story_last_space:
                    if story_page < len(cutscene_segments) - 1:
                        story_page += 1
                        cutscene_timer = 0  # Reset timer for next cutscene
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
                switch_parts = {'left_controller': False, 'right_controller': False, 'screen': False}
                switch_parts_count = 0
                state = "PLAY"
            clock.tick(FPS)
            continue
        if state == "GAMEOVER":
            play_sound(GAME_OVER_SOUND)
            
            # Check for new high score
            is_new_high_score, current_high_score = update_high_score(score)
            high_score = current_high_score
            
            screen.fill(BLACK)
            msg = pygame.font.Font(None, 64).render("Game Over!", True, RED)
            score_display = pygame.font.Font(None, 36).render(f"Score: {score}", True, YELLOW)
            level_display = pygame.font.Font(None, 36).render(f"Level: {current_level}", True, WHITE)
            high_score_display = pygame.font.Font(None, 36).render(f"High Score: {high_score}", True, GOLDEN)
            prompt = pygame.font.Font(None, 36).render("Press SPACE to Restart", True, WHITE)
            
            # Show "NEW HIGH SCORE!" message if applicable
            if is_new_high_score:
                new_record_msg = pygame.font.Font(None, 48).render("NEW HIGH SCORE!", True, GOLDEN)
                screen.blit(new_record_msg, ((WIDTH-new_record_msg.get_width())//2, HEIGHT//2-120))
            
            screen.blit(msg, ((WIDTH-msg.get_width())//2, HEIGHT//2-70))
            screen.blit(score_display, ((WIDTH-score_display.get_width())//2, HEIGHT//2-20))
            screen.blit(high_score_display, ((WIDTH-high_score_display.get_width())//2, HEIGHT//2+10))
            screen.blit(level_display, ((WIDTH-level_display.get_width())//2, HEIGHT//2+40))
            screen.blit(prompt, ((WIDTH-prompt.get_width())//2, HEIGHT//2+90))
            pygame.display.flip()
            if keys[pygame.K_SPACE]:
                player.__init__()
                current_level = 1
                boss = None
                platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)
                state = "PLAY"
                score = 0
                switch_parts = {'left_controller': False, 'right_controller': False, 'screen': False}
                switch_parts_count = 0
            clock.tick(FPS)
            continue
        if state == "COMPLETE":
            play_sound(LEVEL_COMPLETE_SOUND)
            screen.fill(BLACK)
            if current_level % 3 == 0:
                msg = pygame.font.Font(None, 64).render("Boss Defeated!", True, YELLOW)
            else:
                msg = pygame.font.Font(None, 64).render("Level Complete!", True, YELLOW)
            score_display = pygame.font.Font(None, 36).render(f"Score: {score}", True, GOLDEN)
            level_display = pygame.font.Font(None, 36).render(f"Level: {current_level}", True, WHITE)
            high_score_display = pygame.font.Font(None, 32).render(f"High Score: {high_score}", True, GOLDEN)
            prompt = pygame.font.Font(None, 36).render("Press SPACE for Next Level", True, WHITE)
            screen.blit(msg, ((WIDTH-msg.get_width())//2, HEIGHT//2-70))
            screen.blit(score_display, ((WIDTH-score_display.get_width())//2, HEIGHT//2-20))
            screen.blit(level_display, ((WIDTH-level_display.get_width())//2, HEIGHT//2+10))
            screen.blit(high_score_display, ((WIDTH-high_score_display.get_width())//2, HEIGHT//2+40))
            screen.blit(prompt, ((WIDTH-prompt.get_width())//2, HEIGHT//2+80))
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
                if current_level % 3 == 0:
                    print(f"Entering boss level {current_level}!")  # Debug message
                    boss_level = current_level // 3
                    platforms, enemies, coins, pipes, flag, powerups, boss = create_boss_level(boss_level)
                    mom = None  # No mom in boss levels
                    # Start intense boss music
                    start_boss_music()
                else:
                    print(f"Entering normal level {current_level}")  # Debug message
                    boss = None
                    platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)
                    # Return to normal music for regular levels
                    return_to_normal_music()
                
                state = "PLAY"
            clock.tick(FPS)
            continue

        # --- Nintendo Switch Cutscenes ---
        if state == "CUTSCENE_LEFT_CONTROLLER":
            cutscene_timer += 1
            
            # Dynamic background with boss defeat atmosphere
            screen.fill((10, 10, 30))  # Dark blue background
            
            # Floating victory particles
            for i in range(20):
                particle_x = (i * 47 + cutscene_timer * 2) % WIDTH
                particle_y = 50 + int(30 * math.sin(cutscene_timer * 0.03 + i))
                particle_color = (100 + i * 5, 150 + i * 3, 255)
                pygame.draw.circle(screen, particle_color, (particle_x, particle_y), 2)
            
            # Title with dramatic entrance
            title_progress = min(cutscene_timer / 60.0, 1.0)
            title_scale = int(64 * title_progress)
            if title_scale > 0:
                title = pygame.font.Font(None, title_scale).render("FIRST PART RETRIEVED!", True, BLUE)
                # Glowing effect
                for glow in range(3):
                    glow_surface = pygame.font.Font(None, title_scale + glow * 2).render("FIRST PART RETRIEVED!", True, (50, 50, 150))
                    screen.blit(glow_surface, ((WIDTH-glow_surface.get_width())//2 - glow, HEIGHT//2-150 - glow))
                screen.blit(title, ((WIDTH-title.get_width())//2, HEIGHT//2-150))
            
            # Ahaan celebrating with enhanced detail
            if cutscene_timer > 30:
                ahaan_x, ahaan_y = WIDTH//2 - 100, HEIGHT//2 - 50
                
                # Victory pose with raised fist
                # Head with excited expression
                pygame.draw.ellipse(screen, SKIN, (ahaan_x, ahaan_y, 40, 50))
                pygame.draw.ellipse(screen, (240, 200, 160), (ahaan_x + 2, ahaan_y + 2, 36, 46))
                
                # Hair with wind effect from victory
                hair_flow = int(5 * math.sin(cutscene_timer * 0.2))
                pygame.draw.ellipse(screen, BROWN, (ahaan_x - 5 + hair_flow, ahaan_y - 5, 50, 25))
                
                # Excited eyes
                pygame.draw.ellipse(screen, WHITE, (ahaan_x + 8, ahaan_y + 15, 8, 10))
                pygame.draw.ellipse(screen, WHITE, (ahaan_x + 24, ahaan_y + 15, 8, 10))
                pygame.draw.circle(screen, BLACK, (ahaan_x + 11, ahaan_y + 19), 3)
                pygame.draw.circle(screen, BLACK, (ahaan_x + 27, ahaan_y + 19), 3)
                pygame.draw.circle(screen, WHITE, (ahaan_x + 12, ahaan_y + 18), 1)  # Eye shine
                pygame.draw.circle(screen, WHITE, (ahaan_x + 28, ahaan_y + 18), 1)
                
                # Big victorious smile
                pygame.draw.arc(screen, BLACK, (ahaan_x + 10, ahaan_y + 28, 20, 15), 0, math.pi, 3)
                
                # Body in victory pose
                pygame.draw.rect(screen, BLUE, (ahaan_x - 10, ahaan_y + 50, 60, 70))
                
                # Raised fist (left arm up in celebration)
                pygame.draw.rect(screen, SKIN, (ahaan_x - 25, ahaan_y + 40, 20, 40))
                pygame.draw.ellipse(screen, SKIN, (ahaan_x - 20, ahaan_y + 30, 10, 12))  # Raised fist
                
                # Right arm pointing to controller
                pygame.draw.rect(screen, SKIN, (ahaan_x + 55, ahaan_y + 60, 25, 15))
                
                # Legs in confident stance
                pygame.draw.rect(screen, BLUE, (ahaan_x + 5, ahaan_y + 110, 15, 40))
                pygame.draw.rect(screen, BLUE, (ahaan_x + 25, ahaan_y + 110, 15, 40))
                
                # Victory sparkles around Ahaan
                for spark in range(8):
                    spark_angle = cutscene_timer * 0.1 + spark * (2 * math.pi / 8)
                    spark_x = ahaan_x + 20 + int(40 * math.cos(spark_angle))
                    spark_y = ahaan_y + 75 + int(30 * math.sin(spark_angle))
                    spark_size = 2 + int(2 * math.sin(cutscene_timer * 0.3 + spark))
                    pygame.draw.circle(screen, YELLOW, (spark_x, spark_y), spark_size)
                    pygame.draw.circle(screen, WHITE, (spark_x - 1, spark_y - 1), max(1, spark_size - 1))
            
            # Left controller with dramatic entrance and glow
            if cutscene_timer > 60:
                controller_x = WIDTH//2 + 50
                controller_y = HEIGHT//2 - 20
                
                # Controller entrance animation
                entrance_progress = min((cutscene_timer - 60) / 60.0, 1.0)
                final_x = controller_x
                controller_x = int(WIDTH + (final_x - WIDTH) * entrance_progress)
                
                # Magical glow around controller
                glow_intensity = int(100 + 50 * math.sin(cutscene_timer * 0.15))
                for glow_radius in range(50, 20, -5):
                    glow_alpha = max(0, glow_intensity - (50 - glow_radius) * 4)
                    glow_color = (0, 0, 255, glow_alpha // 4)
                    pygame.draw.circle(screen, (50, 50, 255), (controller_x + 15, controller_y + 50), glow_radius, 2)
                
                # Enhanced left controller
                pygame.draw.rect(screen, BLUE, (controller_x, controller_y, 30, 100))
                pygame.draw.rect(screen, (100, 150, 255), (controller_x + 2, controller_y + 2, 26, 96))  # Highlight
                
                # Analog stick with detailed design
                pygame.draw.circle(screen, (50, 100, 200), (controller_x + 15, controller_y + 30), 8)
                pygame.draw.circle(screen, (80, 130, 255), (controller_x + 15, controller_y + 30), 6)
                pygame.draw.circle(screen, (200, 220, 255), (controller_x + 15, controller_y + 30), 3)
                
                # D-pad with proper Nintendo style
                pygame.draw.rect(screen, (80, 120, 255), (controller_x + 8, controller_y + 60, 14, 4))  # Horizontal
                pygame.draw.rect(screen, (80, 120, 255), (controller_x + 13, controller_y + 55, 4, 14))  # Vertical
                pygame.draw.circle(screen, (100, 140, 255), (controller_x + 15, controller_y + 62), 2)  # Center
                
                # Capture buttons
                pygame.draw.rect(screen, (150, 150, 150), (controller_x + 5, controller_y + 80, 6, 3))
                pygame.draw.rect(screen, (150, 150, 150), (controller_x + 5, controller_y + 90, 6, 3))
                
                # Energy particles floating around controller
                for particle in range(12):
                    particle_angle = cutscene_timer * 0.08 + particle * (2 * math.pi / 12)
                    particle_radius = 35 + int(10 * math.sin(cutscene_timer * 0.1 + particle))
                    particle_x = controller_x + 15 + int(particle_radius * math.cos(particle_angle))
                    particle_y = controller_y + 50 + int(particle_radius * math.sin(particle_angle))
                    particle_size = 1 + int(2 * math.sin(cutscene_timer * 0.2 + particle))
                    pygame.draw.circle(screen, (100, 200, 255), (particle_x, particle_y), particle_size)
            
            # Story text with typewriter effect
            if cutscene_timer > 90:
                text_progress = min((cutscene_timer - 90) / 3.0, 1.0)
                
                story_text = "Ahaan defeats the first Mom boss and retrieves the Left Joy-Con!"
                visible_chars = int(len(story_text) * text_progress)
                visible_text = story_text[:visible_chars]
                
                story1 = pygame.font.Font(None, 32).render(visible_text, True, WHITE)
                screen.blit(story1, ((WIDTH-story1.get_width())//2, HEIGHT//2+80))
            
            if cutscene_timer > 180:
                story2_text = "'One piece down, two to go!' Ahaan shouts with determination!"
                text_progress2 = min((cutscene_timer - 180) / 3.0, 1.0)
                visible_chars2 = int(len(story2_text) * text_progress2)
                visible_text2 = story2_text[:visible_chars2]
                
                story2 = pygame.font.Font(None, 28).render(visible_text2, True, YELLOW)
                screen.blit(story2, ((WIDTH-story2.get_width())//2, HEIGHT//2+110))
            
            # Controls
            if cutscene_timer > 240:
                controls = pygame.font.Font(None, 32).render("Press SPACE to continue the adventure!", True, (150, 255, 150))
                # Pulsing effect
                alpha_pulse = int(200 + 55 * math.sin(cutscene_timer * 0.2))
                screen.blit(controls, ((WIDTH-controls.get_width())//2, HEIGHT//2+150))
            
            pygame.display.flip()
            if keys[pygame.K_SPACE] and cutscene_timer > 240:
                cutscene_timer = 0  # Reset for next cutscene
                state = "COMPLETE"
            clock.tick(FPS)
            continue
            
        if state == "CUTSCENE_RIGHT_CONTROLLER":
            cutscene_timer += 1
            
            # Dynamic background with escalating intensity
            screen.fill((30, 10, 10))  # Dark red background
            
            # Intense victory particles with red theme
            for i in range(25):
                particle_x = (i * 31 + cutscene_timer * 3) % WIDTH
                particle_y = 40 + int(40 * math.sin(cutscene_timer * 0.04 + i))
                particle_color = (255, 100 + i * 3, 100 + i * 2)
                particle_size = 1 + int(2 * math.sin(cutscene_timer * 0.1 + i))
                pygame.draw.circle(screen, particle_color, (particle_x, particle_y), particle_size)
            
            # Title with explosive entrance
            title_progress = min(cutscene_timer / 45.0, 1.0)
            title_scale = int(72 * title_progress)
            if title_scale > 0:
                title = pygame.font.Font(None, title_scale).render("SECOND PART SECURED!", True, RED)
                # Multi-layered glow for intensity
                for glow in range(4):
                    glow_surface = pygame.font.Font(None, title_scale + glow * 3).render("SECOND PART SECURED!", True, (150 - glow * 20, 50, 50))
                    screen.blit(glow_surface, ((WIDTH-glow_surface.get_width())//2 - glow, HEIGHT//2-160 - glow))
                screen.blit(title, ((WIDTH-title.get_width())//2, HEIGHT//2-160))
            
            # Enhanced Ahaan with more confident pose
            if cutscene_timer > 25:
                ahaan_x, ahaan_y = WIDTH//2 - 120, HEIGHT//2 - 60
                
                # More heroic stance
                # Head with determined expression
                pygame.draw.ellipse(screen, SKIN, (ahaan_x, ahaan_y, 45, 55))
                pygame.draw.ellipse(screen, (240, 200, 160), (ahaan_x + 3, ahaan_y + 3, 39, 49))
                
                # Hair flowing with increased confidence
                hair_flow = int(8 * math.sin(cutscene_timer * 0.15))
                pygame.draw.ellipse(screen, BROWN, (ahaan_x - 8 + hair_flow, ahaan_y - 8, 60, 30))
                for tuft in range(3):
                    tuft_x = ahaan_x + 10 + tuft * 15 + int(3 * math.sin(cutscene_timer * 0.2 + tuft))
                    pygame.draw.circle(screen, (120, 80, 40), (tuft_x, ahaan_y - 2), 6)
                
                # Focused, determined eyes
                pygame.draw.ellipse(screen, WHITE, (ahaan_x + 10, ahaan_y + 18, 10, 12))
                pygame.draw.ellipse(screen, WHITE, (ahaan_x + 28, ahaan_y + 18, 10, 12))
                pygame.draw.circle(screen, BLACK, (ahaan_x + 14, ahaan_y + 23), 4)
                pygame.draw.circle(screen, BLACK, (ahaan_x + 32, ahaan_y + 23), 4)
                pygame.draw.circle(screen, WHITE, (ahaan_x + 15, ahaan_y + 22), 1.5)
                pygame.draw.circle(screen, WHITE, (ahaan_x + 33, ahaan_y + 22), 1.5)
                
                # Confident smile
                pygame.draw.arc(screen, BLACK, (ahaan_x + 12, ahaan_y + 32, 22, 18), 0, math.pi, 4)
                
                # Body in powerful stance
                pygame.draw.rect(screen, BLUE, (ahaan_x - 15, ahaan_y + 55, 75, 80))
                pygame.draw.rect(screen, (100, 150, 255), (ahaan_x - 13, ahaan_y + 57, 71, 76))
                
                # Both arms in victory pose
                # Left arm raised in triumph
                pygame.draw.rect(screen, SKIN, (ahaan_x - 30, ahaan_y + 50, 25, 45))
                pygame.draw.ellipse(screen, SKIN, (ahaan_x - 25, ahaan_y + 40, 12, 15))  # Raised fist
                
                # Right arm also raised
                pygame.draw.rect(screen, SKIN, (ahaan_x + 75, ahaan_y + 50, 25, 45))
                pygame.draw.ellipse(screen, SKIN, (ahaan_x + 80, ahaan_y + 40, 12, 15))  # Other raised fist
                
                # Strong stance legs
                pygame.draw.rect(screen, BLUE, (ahaan_x + 8, ahaan_y + 125, 18, 45))
                pygame.draw.rect(screen, BLUE, (ahaan_x + 30, ahaan_y + 125, 18, 45))
                
                # Enhanced victory aura
                aura_radius = 90 + int(25 * math.sin(cutscene_timer * 0.12))
                for ring in range(3):
                    ring_radius = aura_radius - ring * 15
                    ring_alpha = 255 - ring * 60
                    pygame.draw.circle(screen, (255, 100, 100), (ahaan_x + 22, ahaan_y + 90), ring_radius, 3)
                
                # Power sparkles with red theme
                for spark in range(12):
                    spark_angle = cutscene_timer * 0.15 + spark * (2 * math.pi / 12)
                    spark_distance = 50 + int(20 * math.sin(cutscene_timer * 0.1 + spark))
                    spark_x = ahaan_x + 22 + int(spark_distance * math.cos(spark_angle))
                    spark_y = ahaan_y + 90 + int(spark_distance * math.sin(spark_angle))
                    spark_size = 2 + int(3 * math.sin(cutscene_timer * 0.25 + spark))
                    pygame.draw.circle(screen, YELLOW, (spark_x, spark_y), spark_size)
                    pygame.draw.circle(screen, WHITE, (spark_x - 1, spark_y - 1), max(1, spark_size - 1))
                    pygame.draw.circle(screen, RED, (spark_x, spark_y), max(1, spark_size - 2))
            
            # Right controller with dramatic red entrance
            if cutscene_timer > 50:
                controller_x = WIDTH//2 + 80
                controller_y = HEIGHT//2 - 30
                
                # Controller entrance with rotation
                entrance_progress = min((cutscene_timer - 50) / 45.0, 1.0)
                final_x = controller_x
                controller_x = int(WIDTH + 100 + (final_x - WIDTH - 100) * entrance_progress)
                rotation_angle = (1 - entrance_progress) * math.pi * 2
                
                # Intense red glow
                glow_intensity = int(120 + 60 * math.sin(cutscene_timer * 0.18))
                for glow_radius in range(60, 25, -6):
                    glow_color = (255, 50, 50, max(0, glow_intensity - (60 - glow_radius) * 3))
                    pygame.draw.circle(screen, (255, 100, 100), (controller_x + 15, controller_y + 50), glow_radius, 2)
                
                # Enhanced right controller
                pygame.draw.rect(screen, RED, (controller_x, controller_y, 30, 100))
                pygame.draw.rect(screen, (255, 100, 100), (controller_x + 2, controller_y + 2, 26, 96))  # Highlight
                
                # Analog stick with enhanced detail
                pygame.draw.circle(screen, (200, 50, 50), (controller_x + 15, controller_y + 30), 8)
                pygame.draw.circle(screen, (255, 80, 80), (controller_x + 15, controller_y + 30), 6)
                pygame.draw.circle(screen, (255, 200, 200), (controller_x + 15, controller_y + 30), 3)
                
                # ABXY buttons with proper Nintendo colors
                pygame.draw.circle(screen, YELLOW, (controller_x + 8, controller_y + 55), 3)    # Y button
                pygame.draw.circle(screen, GREEN, (controller_x + 22, controller_y + 65), 3)    # A button  
                pygame.draw.circle(screen, BLUE, (controller_x + 22, controller_y + 45), 3)     # X button
                pygame.draw.circle(screen, RED, (controller_x + 8, controller_y + 65), 3)       # B button
                
                # Button labels
                button_font = pygame.font.Font(None, 16)
                y_label = button_font.render("Y", True, BLACK)
                a_label = button_font.render("A", True, BLACK)
                x_label = button_font.render("X", True, BLACK)
                b_label = button_font.render("B", True, BLACK)
                screen.blit(y_label, (controller_x + 6, controller_y + 52))
                screen.blit(a_label, (controller_x + 20, controller_y + 62))
                screen.blit(x_label, (controller_x + 20, controller_y + 42))
                screen.blit(b_label, (controller_x + 6, controller_y + 62))
                
                # Plus button and home button
                pygame.draw.rect(screen, (150, 150, 150), (controller_x + 18, controller_y + 80, 6, 2))
                pygame.draw.rect(screen, (150, 150, 150), (controller_x + 20, controller_y + 78, 2, 6))
                pygame.draw.circle(screen, (100, 100, 100), (controller_x + 15, controller_y + 90), 4)
                
                # Energy vortex around controller
                for particle in range(15):
                    particle_angle = cutscene_timer * 0.12 + particle * (2 * math.pi / 15)
                    particle_radius = 40 + int(15 * math.sin(cutscene_timer * 0.08 + particle))
                    particle_x = controller_x + 15 + int(particle_radius * math.cos(particle_angle))
                    particle_y = controller_y + 50 + int(particle_radius * math.sin(particle_angle))
                    particle_size = 1 + int(3 * math.sin(cutscene_timer * 0.22 + particle))
                    pygame.draw.circle(screen, (255, 150, 150), (particle_x, particle_y), particle_size)
                    pygame.draw.circle(screen, WHITE, (particle_x, particle_y), max(1, particle_size - 1))
            
            # Story text with enhanced typewriter effect
            if cutscene_timer > 80:
                text_progress = min((cutscene_timer - 80) / 2.5, 1.0)
                
                story_text = "Ahaan conquers the second Mom boss and claims the Right Joy-Con!"
                visible_chars = int(len(story_text) * text_progress)
                visible_text = story_text[:visible_chars]
                
                story1 = pygame.font.Font(None, 30).render(visible_text, True, WHITE)
                screen.blit(story1, ((WIDTH-story1.get_width())//2, HEIGHT//2+90))
            
            if cutscene_timer > 160:
                story2_text = "'Just the screen left!' he declares with unwavering confidence!"
                text_progress2 = min((cutscene_timer - 160) / 2.5, 1.0)
                visible_chars2 = int(len(story2_text) * text_progress2)
                visible_text2 = story2_text[:visible_chars2]
                
                story2 = pygame.font.Font(None, 26).render(visible_text2, True, YELLOW)
                screen.blit(story2, ((WIDTH-story2.get_width())//2, HEIGHT//2+120))
            
            # Controls with pulsing effect
            if cutscene_timer > 220:
                pulse_intensity = int(200 + 55 * math.sin(cutscene_timer * 0.25))
                controls = pygame.font.Font(None, 32).render("Press SPACE for the final showdown!", True, (255, pulse_intensity, pulse_intensity))
                screen.blit(controls, ((WIDTH-controls.get_width())//2, HEIGHT//2+160))
            
            pygame.display.flip()
            if keys[pygame.K_SPACE] and cutscene_timer > 220:
                cutscene_timer = 0  # Reset for next cutscene
                state = "COMPLETE"
            clock.tick(FPS)
            continue
            
        if state == "CUTSCENE_SCREEN":
            cutscene_timer += 1
            
            # Check if all parts are collected for different scenarios
            if switch_parts_count >= 3:
                # FINAL VICTORY CUTSCENE - Ultimate triumph!
                screen.fill((10, 30, 10))  # Dark green background for victory
                
                # Epic celebration particles
                for i in range(30):
                    particle_x = (i * 23 + cutscene_timer * 4) % WIDTH
                    particle_y = 30 + int(50 * math.sin(cutscene_timer * 0.05 + i))
                    particle_color = (100 + i * 3, 255, 100 + i * 2)
                    particle_size = 1 + int(3 * math.sin(cutscene_timer * 0.12 + i))
                    pygame.draw.circle(screen, particle_color, (particle_x, particle_y), particle_size)
                
                # Ultimate victory title with maximum impact
                title_progress = min(cutscene_timer / 30.0, 1.0)
                title_scale = int(96 * title_progress)
                if title_scale > 0:
                    title = pygame.font.Font(None, title_scale).render("NINTENDO SWITCH COMPLETE!", True, GREEN)
                    # Epic multi-layer glow
                    for glow in range(6):
                        glow_surface = pygame.font.Font(None, title_scale + glow * 4).render("NINTENDO SWITCH COMPLETE!", True, (50 + glow * 10, 255 - glow * 20, 50 + glow * 10))
                        screen.blit(glow_surface, ((WIDTH-glow_surface.get_width())//2 - glow * 2, HEIGHT//2-200 - glow * 2))
                    screen.blit(title, ((WIDTH-title.get_width())//2, HEIGHT//2-200))
                
                # Ahaan in ultimate victory pose
                if cutscene_timer > 20:
                    ahaan_x, ahaan_y = WIDTH//2 - 150, HEIGHT//2 - 80
                    
                    # Triumphant hero stance
                    # Head with pure joy expression
                    pygame.draw.ellipse(screen, SKIN, (ahaan_x, ahaan_y, 50, 60))
                    pygame.draw.ellipse(screen, (240, 200, 160), (ahaan_x + 3, ahaan_y + 3, 44, 54))
                    
                    # Hair flowing with victory wind
                    hair_flow = int(12 * math.sin(cutscene_timer * 0.1))
                    pygame.draw.ellipse(screen, BROWN, (ahaan_x - 10 + hair_flow, ahaan_y - 10, 70, 35))
                    for tuft in range(4):
                        tuft_x = ahaan_x + 8 + tuft * 12 + int(5 * math.sin(cutscene_timer * 0.15 + tuft))
                        pygame.draw.circle(screen, (120, 80, 40), (tuft_x, ahaan_y - 5), 8)
                    
                    # Eyes radiating pure happiness
                    pygame.draw.ellipse(screen, WHITE, (ahaan_x + 12, ahaan_y + 20, 12, 14))
                    pygame.draw.ellipse(screen, WHITE, (ahaan_x + 30, ahaan_y + 20, 12, 14))
                    pygame.draw.circle(screen, BLACK, (ahaan_x + 17, ahaan_y + 26), 5)
                    pygame.draw.circle(screen, BLACK, (ahaan_x + 35, ahaan_y + 26), 5)
                    # Eyes sparkling with joy
                    pygame.draw.circle(screen, WHITE, (ahaan_x + 18, ahaan_y + 24), 2)
                    pygame.draw.circle(screen, WHITE, (ahaan_x + 36, ahaan_y + 24), 2)
                    pygame.draw.circle(screen, YELLOW, (ahaan_x + 19, ahaan_y + 25), 1)
                    pygame.draw.circle(screen, YELLOW, (ahaan_x + 37, ahaan_y + 25), 1)
                    
                    # Biggest smile ever
                    pygame.draw.arc(screen, BLACK, (ahaan_x + 10, ahaan_y + 35, 30, 20), 0, math.pi, 5)
                    pygame.draw.arc(screen, (200, 100, 100), (ahaan_x + 12, ahaan_y + 37, 26, 16), 0, math.pi, 3)
                    
                    # Body in ultimate victory pose
                    pygame.draw.rect(screen, BLUE, (ahaan_x - 20, ahaan_y + 60, 90, 90))
                    pygame.draw.rect(screen, (100, 150, 255), (ahaan_x - 18, ahaan_y + 62, 86, 86))
                    
                    # Both arms raised high in victory
                    pygame.draw.rect(screen, SKIN, (ahaan_x - 40, ahaan_y + 40, 30, 50))  # Left arm up
                    pygame.draw.rect(screen, SKIN, (ahaan_x + 90, ahaan_y + 40, 30, 50))  # Right arm up
                    pygame.draw.ellipse(screen, SKIN, (ahaan_x - 35, ahaan_y + 25, 15, 18))  # Left fist
                    pygame.draw.ellipse(screen, SKIN, (ahaan_x + 95, ahaan_y + 25, 15, 18))  # Right fist
                    
                    # Strong victory stance
                    pygame.draw.rect(screen, BLUE, (ahaan_x + 10, ahaan_y + 140, 20, 50))
                    pygame.draw.rect(screen, BLUE, (ahaan_x + 35, ahaan_y + 140, 20, 50))
                    
                    # Ultimate victory aura
                    mega_aura_radius = 120 + int(40 * math.sin(cutscene_timer * 0.08))
                    for ring in range(5):
                        ring_radius = mega_aura_radius - ring * 20
                        ring_color = (100 + ring * 30, 255, 100 + ring * 30)
                        pygame.draw.circle(screen, ring_color, (ahaan_x + 25, ahaan_y + 100), ring_radius, 4)
                    
                    # Epic victory sparkles
                    for spark in range(20):
                        spark_angle = cutscene_timer * 0.2 + spark * (2 * math.pi / 20)
                        spark_distance = 60 + int(30 * math.sin(cutscene_timer * 0.05 + spark))
                        spark_x = ahaan_x + 25 + int(spark_distance * math.cos(spark_angle))
                        spark_y = ahaan_y + 100 + int(spark_distance * math.sin(spark_angle))
                        spark_size = 2 + int(4 * math.sin(cutscene_timer * 0.3 + spark))
                        pygame.draw.circle(screen, YELLOW, (spark_x, spark_y), spark_size)
                        pygame.draw.circle(screen, WHITE, (spark_x - 1, spark_y - 1), max(1, spark_size - 1))
                        pygame.draw.circle(screen, GREEN, (spark_x, spark_y), max(1, spark_size - 2))
                
                # Complete Nintendo Switch with assembly animation
                if cutscene_timer > 40:
                    switch_x = WIDTH//2 + 100
                    switch_y = HEIGHT//2 - 50
                    
                    # Assembly progress animation
                    assembly_progress = min((cutscene_timer - 40) / 60.0, 1.0)
                    
                    # Screen piece (arrives first)
                    screen_piece_x = switch_x
                    screen_piece_y = switch_y
                    pygame.draw.rect(screen, BLACK, (screen_piece_x, screen_piece_y, 80, 80))
                    pygame.draw.rect(screen, (40, 40, 40), (screen_piece_x + 3, screen_piece_y + 3, 74, 74))
                    # Screen content showing victory
                    pygame.draw.rect(screen, (100, 255, 100), (screen_piece_x + 8, screen_piece_y + 8, 64, 64))
                    pygame.draw.circle(screen, YELLOW, (screen_piece_x + 40, screen_piece_y + 30), 8)  # Happy face
                    pygame.draw.circle(screen, BLACK, (screen_piece_x + 35, screen_piece_y + 25), 2)
                    pygame.draw.circle(screen, BLACK, (screen_piece_x + 45, screen_piece_y + 25), 2)
                    pygame.draw.arc(screen, BLACK, (screen_piece_x + 32, screen_piece_y + 32, 16, 10), 0, math.pi, 2)
                    
                    # Left controller slides in from left
                    left_controller_target_x = switch_x - 20
                    left_controller_x = int(switch_x - 200 + (left_controller_target_x - (switch_x - 200)) * assembly_progress)
                    pygame.draw.rect(screen, BLUE, (left_controller_x, switch_y + 5, 25, 70))
                    pygame.draw.rect(screen, (100, 150, 255), (left_controller_x + 2, switch_y + 7, 21, 66))
                    pygame.draw.circle(screen, (50, 100, 200), (left_controller_x + 12, switch_y + 25), 6)
                    
                    # Right controller slides in from right
                    right_controller_target_x = switch_x + 75
                    right_controller_x = int(switch_x + 200 + (right_controller_target_x - (switch_x + 200)) * assembly_progress)
                    pygame.draw.rect(screen, RED, (right_controller_x, switch_y + 5, 25, 70))
                    pygame.draw.rect(screen, (255, 100, 100), (right_controller_x + 2, switch_y + 7, 21, 66))
                    pygame.draw.circle(screen, (200, 50, 50), (right_controller_x + 12, switch_y + 25), 6)
                    
                    # Assembly completion effects
                    if assembly_progress >= 1.0:
                        # Magical completion flash
                        flash_intensity = int(100 * math.sin(cutscene_timer * 0.4))
                        pygame.draw.circle(screen, (255, 255, 255), (switch_x + 40, switch_y + 40), 150, flash_intensity // 20)
                        
                        # Complete Nintendo Switch glow
                        for glow_radius in range(100, 40, -10):
                            glow_alpha = max(0, 255 - (100 - glow_radius) * 5)
                            pygame.draw.circle(screen, (150, 255, 150), (switch_x + 40, switch_y + 40), glow_radius, 2)
                
                # Epic story text
                if cutscene_timer > 70:
                    text_progress = min((cutscene_timer - 70) / 2.0, 1.0)
                    story_text = "Ahaan defeats the final Mom boss and claims the screen!"
                    visible_chars = int(len(story_text) * text_progress)
                    visible_text = story_text[:visible_chars]
                    story1 = pygame.font.Font(None, 32).render(visible_text, True, WHITE)
                    screen.blit(story1, ((WIDTH-story1.get_width())//2, HEIGHT//2+120))
                
                if cutscene_timer > 140:
                    text_progress2 = min((cutscene_timer - 140) / 2.0, 1.0)
                    story2_text = "He quickly assembles his Nintendo Switch - VICTORY IS HIS!"
                    visible_chars2 = int(len(story2_text) * text_progress2)
                    visible_text2 = story2_text[:visible_chars2]
                    story2 = pygame.font.Font(None, 28).render(visible_text2, True, GOLDEN)
                    screen.blit(story2, ((WIDTH-story2.get_width())//2, HEIGHT//2+150))
                
                if cutscene_timer > 200:
                    pulse_intensity = int(200 + 55 * math.sin(cutscene_timer * 0.3))
                    controls = pygame.font.Font(None, 36).render("Press SPACE to see the grand finale!", True, (pulse_intensity, 255, pulse_intensity))
                    screen.blit(controls, ((WIDTH-controls.get_width())//2, HEIGHT//2+190))
                
                state_after_space = "VICTORY_CUTSCENE"
                min_timer = 200
                
            else:
                # INTERMEDIATE SCREEN CUTSCENE - Getting just the screen piece
                screen.fill((20, 10, 30))  # Dark purple background
                
                # Mysterious victory particles
                for i in range(20):
                    particle_x = (i * 41 + cutscene_timer * 2.5) % WIDTH
                    particle_y = 40 + int(35 * math.sin(cutscene_timer * 0.04 + i))
                    particle_color = (150 + i * 2, 255, 150 + i * 3)
                    particle_size = 1 + int(2 * math.sin(cutscene_timer * 0.15 + i))
                    pygame.draw.circle(screen, particle_color, (particle_x, particle_y), particle_size)
                
                # Title with ominous undertone
                title_progress = min(cutscene_timer / 40.0, 1.0)
                title_scale = int(68 * title_progress)
                if title_scale > 0:
                    title = pygame.font.Font(None, title_scale).render("FINAL PIECE OBTAINED!", True, GREEN)
                    # Mysterious glow
                    for glow in range(3):
                        glow_surface = pygame.font.Font(None, title_scale + glow * 3).render("FINAL PIECE OBTAINED!", True, (100, 200 - glow * 30, 100))
                        screen.blit(glow_surface, ((WIDTH-glow_surface.get_width())//2 - glow, HEIGHT//2-140 - glow))
                    screen.blit(title, ((WIDTH-title.get_width())//2, HEIGHT//2-140))
                
                # Ahaan with determined but cautious expression
                if cutscene_timer > 30:
                    ahaan_x, ahaan_y = WIDTH//2 - 110, HEIGHT//2 - 50
                    
                    # Focused, determined stance
                    pygame.draw.ellipse(screen, SKIN, (ahaan_x, ahaan_y, 42, 52))
                    pygame.draw.ellipse(screen, (240, 200, 160), (ahaan_x + 2, ahaan_y + 2, 38, 48))
                    
                    # Hair with slight wind
                    hair_flow = int(6 * math.sin(cutscene_timer * 0.12))
                    pygame.draw.ellipse(screen, BROWN, (ahaan_x - 6 + hair_flow, ahaan_y - 6, 55, 28))
                    
                    # Determined but cautious eyes
                    pygame.draw.ellipse(screen, WHITE, (ahaan_x + 9, ahaan_y + 16, 9, 11))
                    pygame.draw.ellipse(screen, WHITE, (ahaan_x + 26, ahaan_y + 16, 9, 11))
                    pygame.draw.circle(screen, BLACK, (ahaan_x + 13, ahaan_y + 21), 3)
                    pygame.draw.circle(screen, BLACK, (ahaan_x + 30, ahaan_y + 21), 3)
                    
                    # Slight smile - victory but awareness of more challenges
                    pygame.draw.arc(screen, BLACK, (ahaan_x + 12, ahaan_y + 30, 18, 12), 0, math.pi, 3)
                    
                    # Body reaching for screen
                    pygame.draw.rect(screen, BLUE, (ahaan_x - 8, ahaan_y + 52, 58, 75))
                    pygame.draw.rect(screen, SKIN, (ahaan_x + 45, ahaan_y + 65, 22, 30))  # Reaching arm
                    
                    # Legs in ready stance
                    pygame.draw.rect(screen, BLUE, (ahaan_x + 8, ahaan_y + 120, 16, 42))
                    pygame.draw.rect(screen, BLUE, (ahaan_x + 28, ahaan_y + 120, 16, 42))
                    
                    # Cautious aura - success but more to come
                    aura_radius = 70 + int(15 * math.sin(cutscene_timer * 0.1))
                    for ring in range(2):
                        ring_radius = aura_radius - ring * 20
                        pygame.draw.circle(screen, (100, 200, 100), (ahaan_x + 21, ahaan_y + 85), ring_radius, 2)
                
                # Nintendo Switch screen with mysterious glow
                if cutscene_timer > 50:
                    screen_x = WIDTH//2 + 60
                    screen_y = HEIGHT//2 - 30
                    
                    # Entrance animation
                    entrance_progress = min((cutscene_timer - 50) / 40.0, 1.0)
                    final_x = screen_x
                    screen_x = int(WIDTH + 50 + (final_x - WIDTH - 50) * entrance_progress)
                    
                    # Mysterious glow around screen
                    glow_intensity = int(80 + 40 * math.sin(cutscene_timer * 0.16))
                    for glow_radius in range(50, 25, -5):
                        pygame.draw.circle(screen, (100, 255, 100), (screen_x + 40, screen_y + 40), glow_radius, 2)
                    
                    # Enhanced Nintendo Switch screen
                    pygame.draw.rect(screen, BLACK, (screen_x, screen_y, 80, 80))
                    pygame.draw.rect(screen, (40, 40, 40), (screen_x + 4, screen_y + 4, 72, 72))  # Bezel
                    pygame.draw.rect(screen, (50, 150, 50), (screen_x + 8, screen_y + 8, 64, 64))  # Screen glow
                    
                    # Question mark on screen - mystery remains
                    pygame.draw.circle(screen, YELLOW, (screen_x + 40, screen_y + 30), 8)
                    question_font = pygame.font.Font(None, 24)
                    question_mark = question_font.render("?", True, BLACK)
                    screen.blit(question_mark, (screen_x + 36, screen_y + 24))
                    
                    # Mysterious particles around screen
                    for particle in range(10):
                        particle_angle = cutscene_timer * 0.1 + particle * (2 * math.pi / 10)
                        particle_radius = 35 + int(8 * math.sin(cutscene_timer * 0.12 + particle))
                        particle_x = screen_x + 40 + int(particle_radius * math.cos(particle_angle))
                        particle_y = screen_y + 40 + int(particle_radius * math.sin(particle_angle))
                        particle_size = 1 + int(2 * math.sin(cutscene_timer * 0.18 + particle))
                        pygame.draw.circle(screen, (150, 255, 150), (particle_x, particle_y), particle_size)
                
                # Story with hint of mystery
                if cutscene_timer > 80:
                    text_progress = min((cutscene_timer - 80) / 2.5, 1.0)
                    story_text = "Ahaan retrieves the final piece - the Nintendo Switch screen!"
                    visible_chars = int(len(story_text) * text_progress)
                    visible_text = story_text[:visible_chars]
                    story1 = pygame.font.Font(None, 30).render(visible_text, True, WHITE)
                    screen.blit(story1, ((WIDTH-story1.get_width())//2, HEIGHT//2+100))
                
                if cutscene_timer > 150:
                    text_progress2 = min((cutscene_timer - 150) / 2.5, 1.0)
                    story2_text = "But something feels different... more challenges await!"
                    visible_chars2 = int(len(story2_text) * text_progress2)
                    visible_text2 = story2_text[:visible_chars2]
                    story2 = pygame.font.Font(None, 26).render(visible_text2, True, (255, 200, 100))
                    screen.blit(story2, ((WIDTH-story2.get_width())//2, HEIGHT//2+130))
                
                if cutscene_timer > 200:
                    pulse_intensity = int(150 + 105 * math.sin(cutscene_timer * 0.2))
                    controls = pygame.font.Font(None, 32).render("Press SPACE to continue the adventure!", True, (pulse_intensity, 255, pulse_intensity))
                    screen.blit(controls, ((WIDTH-controls.get_width())//2, HEIGHT//2+170))
                
                state_after_space = "COMPLETE"
                min_timer = 200
            
            pygame.display.flip()
            if keys[pygame.K_SPACE] and cutscene_timer > min_timer:
                cutscene_timer = 0  # Reset for next cutscene
                state = state_after_space
            clock.tick(FPS)
            continue
            
        if state == "VICTORY_CUTSCENE":
            screen.fill(BLACK)
            
            title = pygame.font.Font(None, 72).render("Victory!", True, GOLDEN)
            story1 = pygame.font.Font(None, 40).render("Ahaan assembles his Nintendo Switch and runs away!", True, WHITE)
            story2 = pygame.font.Font(None, 40).render("'Freedom at last!' he shouts with joy!", True, WHITE)
            story3 = pygame.font.Font(None, 32).render("Press SPACE for final congratulations!", True, YELLOW)
            
            # Draw Ahaan running away with complete Nintendo Switch (simple representation)
            # Ahaan
            pygame.draw.ellipse(screen, SKIN, (250, 250, 40, 50))  # Head
            pygame.draw.rect(screen, BLUE, (245, 300, 50, 60))     # Body
            pygame.draw.rect(screen, SKIN, (235, 350, 20, 40))     # Left leg
            pygame.draw.rect(screen, SKIN, (275, 350, 20, 40))     # Right leg
            
            # Nintendo Switch in his hands
            pygame.draw.rect(screen, BLACK, (320, 320, 60, 40))    # Switch body
            pygame.draw.rect(screen, BLUE, (315, 325, 15, 30))     # Left Joy-Con
            pygame.draw.rect(screen, RED, (385, 325, 15, 30))      # Right Joy-Con
            
            # Movement lines
            for i in range(5):
                pygame.draw.line(screen, WHITE, (200-i*10, 280+i*5), (230-i*10, 285+i*5), 2)
            
            screen.blit(title, ((WIDTH-title.get_width())//2, HEIGHT//2-150))
            screen.blit(story1, ((WIDTH-story1.get_width())//2, HEIGHT//2+100))
            screen.blit(story2, ((WIDTH-story2.get_width())//2, HEIGHT//2+140))
            screen.blit(story3, ((WIDTH-story3.get_width())//2, HEIGHT//2+180))
            
            pygame.display.flip()
            if keys[pygame.K_SPACE]:
                state = "CONGRATULATIONS"
            clock.tick(FPS)
            continue
            
        if state == "CONGRATULATIONS":
            screen.fill(BLACK)
            
            # Create a celebratory screen
            import math
            import time
            celebration_timer = time.time() * 2
            
            # Animated congratulations text with rainbow effect
            title = "Congratulations!"
            title_font = pygame.font.Font(None, 96)
            
            for i, letter in enumerate(title):
                # Rainbow color effect
                r = int(128 + 127 * math.sin(celebration_timer + i * 0.5))
                g = int(128 + 127 * math.sin(celebration_timer + i * 0.5 + 2))
                b = int(128 + 127 * math.sin(celebration_timer + i * 0.5 + 4))
                
                # Bouncing letters
                bounce = int(10 * math.sin(celebration_timer * 2 + i * 0.3))
                
                letter_surface = title_font.render(letter, True, (r, g, b))
                letter_x = (WIDTH - len(title) * 45) // 2 + i * 55
                letter_y = HEIGHT // 2 - 100 + bounce
                screen.blit(letter_surface, (letter_x, letter_y))
            
            # Final messages
            msg1 = pygame.font.Font(None, 48).render("Ahaan has his Nintendo Switch back!", True, WHITE)
            msg2 = pygame.font.Font(None, 36).render(f"Final Score: {score}", True, GOLDEN)
            msg3 = pygame.font.Font(None, 36).render(f"High Score: {high_score}", True, GOLDEN)
            msg4 = pygame.font.Font(None, 32).render("Thanks for playing Super Ahaanio!", True, YELLOW)
            msg5 = pygame.font.Font(None, 28).render("Press SPACE to return to main menu", True, WHITE)
            
            screen.blit(msg1, ((WIDTH-msg1.get_width())//2, HEIGHT//2))
            screen.blit(msg2, ((WIDTH-msg2.get_width())//2, HEIGHT//2+50))
            screen.blit(msg3, ((WIDTH-msg3.get_width())//2, HEIGHT//2+90))
            screen.blit(msg4, ((WIDTH-msg4.get_width())//2, HEIGHT//2+140))
            screen.blit(msg5, ((WIDTH-msg5.get_width())//2, HEIGHT//2+190))
            
            # Fireworks effect
            for i in range(10):
                firework_x = (i * 80 + int(50 * math.sin(celebration_timer + i))) % WIDTH
                firework_y = (i * 40 + int(30 * math.cos(celebration_timer * 1.5 + i))) % (HEIGHT//2) + 50
                firework_color = ((i * 50) % 255, ((i * 100) % 255), ((i * 150) % 255))
                pygame.draw.circle(screen, firework_color, (firework_x, firework_y), 3)
            
            pygame.display.flip()
            if keys[pygame.K_SPACE]:
                # Reset for new game
                player.__init__()
                current_level = 1
                boss = None
                score = 0
                switch_parts = {'left_controller': False, 'right_controller': False, 'screen': False}
                switch_parts_count = 0
                platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)
                state = "START"
            clock.tick(FPS)
            continue

        # --- Game Play ---
        # Handle pause menu
        if keys[pygame.K_ESCAPE] or keys[pygame.K_p]:
            if not hasattr(main, 'pause_key_pressed'):
                main.pause_key_pressed = False
            if not main.pause_key_pressed:
                game_paused = not game_paused
                pause_menu_selection = 0  # Reset to Resume
            main.pause_key_pressed = True
        else:
            if hasattr(main, 'pause_key_pressed'):
                main.pause_key_pressed = False
        
        if game_paused:
            # Handle pause menu navigation
            if keys[pygame.K_UP]:
                if not hasattr(main, 'up_key_pressed'):
                    main.up_key_pressed = False
                if not main.up_key_pressed:
                    pause_menu_selection = (pause_menu_selection - 1) % 3
                main.up_key_pressed = True
            else:
                if hasattr(main, 'up_key_pressed'):
                    main.up_key_pressed = False
                    
            if keys[pygame.K_DOWN]:
                if not hasattr(main, 'down_key_pressed'):
                    main.down_key_pressed = False
                if not main.down_key_pressed:
                    pause_menu_selection = (pause_menu_selection + 1) % 3
                main.down_key_pressed = True
            else:
                if hasattr(main, 'down_key_pressed'):
                    main.down_key_pressed = False
            
            if keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                if not hasattr(main, 'select_key_pressed'):
                    main.select_key_pressed = False
                if not main.select_key_pressed:
                    if pause_menu_selection == 0:  # Resume
                        game_paused = False
                    elif pause_menu_selection == 1:  # Restart Level
                        game_paused = False
                        # Save power-up state before resetting
                        saved_lives = player.lives
                        
                        player.__init__()
                        player.lives = saved_lives  # Keep lives but reset position
                        
                        # Recreate current level
                        if in_secret_world:
                            platforms, enemies, coins, pipes, flag, powerups, mom = create_secret_level(secret_world_type)
                            boss = None
                            return_to_normal_music()  # Normal music for secret world
                        elif current_level % 3 == 0:
                            boss_level = current_level // 3
                            platforms, enemies, coins, pipes, flag, powerups, boss = create_boss_level(boss_level)
                            mom = None
                            start_boss_music()  # Boss music for boss levels
                        else:
                            boss = None
                            platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)
                            return_to_normal_music()  # Normal music for regular levels
                        
                        camera_x = 0
                        pipe_entry_timer = 0
                        
                    elif pause_menu_selection == 2:  # Go to Home
                        game_paused = False
                        state = "START"
                        # Reset everything
                        player.__init__()
                        current_level = 1
                        score = 0
                        boss = None
                        mom = None
                        in_secret_world = False
                        platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)
                        camera_x = 0
                        pipe_entry_timer = 0
                main.select_key_pressed = True
            else:
                if hasattr(main, 'select_key_pressed'):
                    main.select_key_pressed = False
            
            # Draw pause menu and skip rest of game logic
            # (Drawing code will be added later in the rendering section)
        else:
            # Normal game logic continues only if not paused
            pass
        
        if not game_paused:  # Only process game logic if not paused
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
                                
                                # Collect Nintendo Switch part based on boss number
                                boss_number = current_level // 3
                                if boss_number == 1 and not switch_parts['left_controller']:
                                    switch_parts['left_controller'] = True
                                    switch_parts_count += 1
                                    state = "CUTSCENE_LEFT_CONTROLLER"
                                elif boss_number == 2 and not switch_parts['right_controller']:
                                    switch_parts['right_controller'] = True
                                    switch_parts_count += 1
                                    state = "CUTSCENE_RIGHT_CONTROLLER"
                                elif boss_number == 3 and not switch_parts['screen']:
                                    switch_parts['screen'] = True
                                    switch_parts_count += 1
                                    state = "CUTSCENE_SCREEN"
                                else:
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
                
                # Check shuttlecock collisions for badminton enemies
                if enemy.enemy_type == "badminton":
                    for shuttlecock in enemy.shuttlecocks[:]:
                        if player.rect.colliderect(shuttlecock.rect) and not player.is_immune():
                            if player.die():  # Returns True if game over
                                state = "GAMEOVER"
                            else:
                                # Player respawned with immunity
                                play_sound(BOSS_HIT_SOUND)
                            enemy.shuttlecocks.remove(shuttlecock)
                            break
                            
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
                            if current_level % 3 == 0:
                                boss_level = current_level // 3
                                platforms, enemies, coins, pipes, flag, powerups, boss = create_boss_level(boss_level)
                                mom = None
                                start_boss_music()  # Boss music when returning to boss level
                            else:
                                boss = None
                                platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)
                                return_to_normal_music()  # Normal music when returning to regular level
                            
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
                    if current_level % 3 == 0:
                        boss_level = current_level // 3
                        platforms, enemies, coins, pipes, flag, powerups, boss = create_boss_level(boss_level)
                        mom = None
                        start_boss_music()  # Boss music when returning to boss level from secret world
                    else:
                        boss = None
                        platforms, enemies, coins, pipes, flag, powerups, mom = create_normal_level(current_level)
                        return_to_normal_music()  # Normal music when returning to regular level from secret world
                    
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
        elif current_level == 5:
            # Special badminton court background
            # Indoor sports hall gradient (lighter colors for indoor feeling)
            for y in range(HEIGHT):
                ratio = y / HEIGHT
                # Light gray to white gradient (indoor court feeling)
                r = int(180 + ratio * 60)   # 180 to 240
                g = int(190 + ratio * 50)   # 190 to 240
                b = int(200 + ratio * 40)   # 200 to 240
                pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
            
            # Draw badminton court lines and net
            # Court floor (light brown/beige)
            pygame.draw.rect(screen, (210, 180, 140), (0 - camera_x, HEIGHT - 50, LEVEL_END_X + 200, 50))
            
            # Badminton court markings (white lines)
            court_lines = [
                # Outer court boundaries
                (100 - camera_x, HEIGHT - 45, LEVEL_END_X - 100, 3),  # Bottom line
                (100 - camera_x, HEIGHT - 200, 3, 155),              # Left line
                ((LEVEL_END_X - 100) - camera_x, HEIGHT - 200, 3, 155),  # Right line
                (100 - camera_x, HEIGHT - 200, LEVEL_END_X - 100, 3),    # Top line
                
                # Center line and service courts
                ((LEVEL_END_X // 2 - 50) - camera_x, HEIGHT - 200, 3, 155),  # Center line
                (200 - camera_x, HEIGHT - 120, LEVEL_END_X - 300, 3),       # Service line 1
                (200 - camera_x, HEIGHT - 80, LEVEL_END_X - 300, 3),        # Service line 2
            ]
            
            for line in court_lines:
                if len(line) == 4:  # Make sure we have x, y, width, height
                    pygame.draw.rect(screen, WHITE, line)
            
            # Badminton net in the center
            net_x = (LEVEL_END_X // 2) - camera_x
            net_y = HEIGHT - 200
            net_height = 100
            
            # Net posts
            pygame.draw.rect(screen, (100, 50, 20), (net_x - 5, net_y, 4, net_height))
            pygame.draw.rect(screen, (100, 50, 20), (net_x + 101, net_y, 4, net_height))
            
            # Net mesh pattern
            for i in range(0, 100, 8):
                pygame.draw.line(screen, WHITE, (net_x + i, net_y), (net_x + i, net_y + net_height), 1)
            for i in range(0, net_height, 6):
                pygame.draw.line(screen, WHITE, (net_x, net_y + i), (net_x + 100, net_y + i), 1)
            
            # Indoor lighting (ceiling lights)
            for light in range(3):
                light_x = 300 + light * 400 - camera_x // 4
                if light_x > -100 and light_x < WIDTH + 100:
                    # Light fixtures
                    pygame.draw.rect(screen, (220, 220, 220), (light_x, 20, 80, 15))
                    pygame.draw.rect(screen, (255, 255, 200), (light_x + 5, 22, 70, 11))
                    # Light rays
                    for ray in range(5):
                        ray_x = light_x + 15 + ray * 12
                        pygame.draw.line(screen, (255, 255, 200), (ray_x, 35), (ray_x, 80), 1)
            
            # Badminton equipment on walls (posters, scoreboards)
            # Equipment rack silhouettes
            for rack in range(2):
                rack_x = 50 + rack * (LEVEL_END_X - 200) - camera_x // 2
                if rack_x > -100 and rack_x < WIDTH + 100:
                    pygame.draw.rect(screen, (80, 60, 40), (rack_x, 150, 60, 80))
                    # Rackets on rack
                    for racket in range(4):
                        racket_y = 160 + racket * 15
                        pygame.draw.ellipse(screen, (200, 50, 50), (rack_x + 10 + racket * 12, racket_y, 8, 12))
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
        
        # Update moving platforms
        player_on_moving_platform = None
        player_bottom = player.rect.bottom
        player_was_on_platform = False
        
        for platform in platforms:
            if hasattr(platform, 'update'):  # Check if it's a MovingPlatform
                # Store old position
                old_x, old_y = platform.rect.x, platform.rect.y
                
                # Check if player is on this platform before moving it
                if (player.rect.bottom <= platform.rect.top + 10 and 
                    player.rect.bottom >= platform.rect.top - 5 and
                    player.rect.centerx >= platform.rect.left - 10 and 
                    player.rect.centerx <= platform.rect.right + 10):
                    player_on_moving_platform = platform
                    player_was_on_platform = True
                
                # Update platform position
                platform.update()
                
                # Move player with platform if they were on it
                if player_on_moving_platform == platform and player_was_on_platform:
                    dx = platform.rect.x - old_x
                    dy = platform.rect.y - old_y
                    player.rect.x += dx
                    player.rect.y += dy
                
                # Also move enemies that are on this moving platform
                for enemy in enemies:
                    if (hasattr(enemy, 'platform') and enemy.platform == platform.rect):
                        # Update enemy's platform reference
                        enemy.platform = platform.rect
                        # Move enemy with the platform
                        dx = platform.rect.x - old_x
                        dy = platform.rect.y - old_y
                        enemy.rect.x += dx
                        enemy.rect.y += dy
        
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
        elif current_level == 5:
            # Special display for badminton level
            level_text = font.render(f'Level 5: BADMINTON COURT!', True, RED)
            screen.blit(level_text, (10, 50))
            badminton_warning = pygame.font.Font(None, 24).render('⚠️ Forced Badminton Class! ⚠️', True, (255, 100, 100))
            screen.blit(badminton_warning, (10, 85))
        else:
            level_text = font.render(f'Level: {current_level}', True, BLACK)
            screen.blit(level_text, (10, 50))
            
            # Show boss music indicator
            if current_music_type == "boss":
                boss_music_indicator = pygame.font.Font(None, 28).render('♪ BOSS FIGHT ♪', True, RED)
                screen.blit(boss_music_indicator, (10, 85))
        
        lives_text = font.render(f'Lives: {player.lives}', True, BLACK)
        screen.blit(lives_text, (10, 130 if in_secret_world else (115 if current_music_type == "boss" and not in_secret_world else 90)))
        
        # Show Nintendo Switch parts collected
        parts_y = 160 if in_secret_world else (145 if current_music_type == "boss" and not in_secret_world else 120)
        parts_font = pygame.font.Font(None, 28)
        parts_text = parts_font.render(f'Switch Parts: {switch_parts_count}/3', True, BLACK)
        screen.blit(parts_text, (10, parts_y))
        
        # Draw visual Nintendo Switch parts indicators
        switch_x = 200
        switch_y = parts_y
        
        # Left controller
        if switch_parts['left_controller']:
            pygame.draw.rect(screen, BLUE, (switch_x, switch_y, 20, 25))
            pygame.draw.circle(screen, BLACK, (switch_x + 10, switch_y + 8), 3)
        else:
            pygame.draw.rect(screen, (100, 100, 100), (switch_x, switch_y, 20, 25))
            pygame.draw.rect(screen, BLACK, (switch_x, switch_y, 20, 25), 2)
        
        # Screen
        if switch_parts['screen']:
            pygame.draw.rect(screen, BLACK, (switch_x + 25, switch_y + 3, 30, 19))
            pygame.draw.rect(screen, (100, 255, 100), (switch_x + 27, switch_y + 5, 26, 15))
        else:
            pygame.draw.rect(screen, (100, 100, 100), (switch_x + 25, switch_y + 3, 30, 19))
            pygame.draw.rect(screen, BLACK, (switch_x + 25, switch_y + 3, 30, 19), 2)
        
        # Right controller
        if switch_parts['right_controller']:
            pygame.draw.rect(screen, RED, (switch_x + 60, switch_y, 20, 25))
            pygame.draw.circle(screen, BLACK, (switch_x + 70, switch_y + 8), 3)
        else:
            pygame.draw.rect(screen, (100, 100, 100), (switch_x + 60, switch_y, 20, 25))
            pygame.draw.rect(screen, BLACK, (switch_x + 60, switch_y, 20, 25), 2)
        
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
        
        # Show pause control
        pause_text = pygame.font.Font(None, 20).render('ESC/P: Pause', True, BLACK)
        screen.blit(pause_text, (WIDTH - 200, 50))
        
        # Draw pause menu if game is paused
        if game_paused:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            # Pause menu background
            menu_width = 300
            menu_height = 200
            menu_x = (WIDTH - menu_width) // 2
            menu_y = (HEIGHT - menu_height) // 2
            
            pygame.draw.rect(screen, WHITE, (menu_x, menu_y, menu_width, menu_height))
            pygame.draw.rect(screen, BLACK, (menu_x, menu_y, menu_width, menu_height), 3)
            
            # Pause menu title
            title_font = pygame.font.Font(None, 48)
            title_text = title_font.render("PAUSED", True, BLACK)
            title_x = menu_x + (menu_width - title_text.get_width()) // 2
            screen.blit(title_text, (title_x, menu_y + 20))
            
            # Menu options
            option_font = pygame.font.Font(None, 36)
            options = ["Resume", "Restart Level", "Go to Home"]
            
            for i, option in enumerate(options):
                color = RED if i == pause_menu_selection else BLACK
                option_text = option_font.render(option, True, color)
                option_x = menu_x + (menu_width - option_text.get_width()) // 2
                option_y = menu_y + 80 + i * 40
                screen.blit(option_text, (option_x, option_y))
                
                # Draw selection arrow
                if i == pause_menu_selection:
                    arrow_x = option_x - 30
                    arrow_y = option_y + option_text.get_height() // 2
                    pygame.draw.polygon(screen, RED, [
                        (arrow_x, arrow_y - 8),
                        (arrow_x, arrow_y + 8),
                        (arrow_x + 15, arrow_y)
                    ])
            
            # Instructions
            inst_font = pygame.font.Font(None, 24)
            inst_text = inst_font.render("↑↓ Navigate, SPACE/ENTER Select", True, BLACK)
            inst_x = menu_x + (menu_width - inst_text.get_width()) // 2
            screen.blit(inst_text, (inst_x, menu_y + menu_height - 30))
            
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    