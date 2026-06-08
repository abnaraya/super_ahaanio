"""
main.py — Super Ahaanio entry point.

Responsibilities:
  1. Initialise pygame, audio, and the sound-effect bank.
  2. Build the initial GameContext from saved settings/progress.
  3. Run the main loop, dispatching each frame to the correct screen handler.
  4. Save settings and progress on exit.

All gameplay logic, rendering, and state-specific UI live in:
  game/screens/   — one file per non-play state
  game/gameplay.py — the PLAY state (update + render)
  game/level_manager.py — level loading / helper functions
  game/context.py — mutable game state container
"""
import sys
import pygame

from game import audio
from game.constants import (
    FPS, WIDTH, HEIGHT,
    DEFAULT_SETTINGS, DEFAULT_PROGRESS,
)
from game.context import GameContext
from game.persistence import (
    load_high_score, load_settings, save_settings,
    load_progress, save_progress,
)
from game.player import Player
from game.states import GameState
from game.transitions import TransitionManager
from game.level_manager import load_normal_level, apply_player_profile
from game.controls import resolve_controls

# Screen handlers
from game.screens.start import handle as handle_start
from game.screens.story import handle as handle_story
from game.screens.settings_screen import handle as handle_settings
from game.screens.level_select import handle as handle_level_select
from game.screens.gameover import handle as handle_gameover
from game.screens.complete import handle as handle_complete
from game.screens.cutscenes import (
    handle_left_controller, handle_right_controller, handle_screen_piece,
)
from game.screens.victory import handle_victory_cutscene, handle_congratulations
from game.gameplay import handle as handle_play



# ---------------------------------------------------------------------------
# Sound bank (module-level so screen modules can import them)
# ---------------------------------------------------------------------------

def _init_sounds() -> dict:
    return {
        "jump":           audio.create_sound_effect(600, 0.15, 0.4),
        "coin":           audio.create_sound_effect(1200, 0.15, 0.4),
        "enemy_defeat":   audio.create_sound_effect(300, 0.3, 0.4),
        "stomp":          audio.create_sound_effect(200, 0.2, 0.5),
        "boss_hit":       audio.create_sound_effect(600, 0.3, 0.5),
        "game_over":      audio.create_sound_effect(200, 0.5, 0.4),
        "level_complete": audio.create_sound_effect(1000, 0.4, 0.5),
    }


# Legacy names kept for modules that import from main
JUMP_SOUND = None
COIN_SOUND = None
ENEMY_DEFEAT_SOUND = None
STOMP_SOUND = None
BOSS_HIT_SOUND = None
GAME_OVER_SOUND = None
LEVEL_COMPLETE_SOUND = None


# ---------------------------------------------------------------------------
# Initialise
# ---------------------------------------------------------------------------

pygame.init()
pygame.mixer.init()
audio.initialize_music("bgm.mp3")

_sounds = _init_sounds()

# Assign legacy module-level names after init
JUMP_SOUND = _sounds["jump"]
COIN_SOUND = _sounds["coin"]
ENEMY_DEFEAT_SOUND = _sounds["enemy_defeat"]
STOMP_SOUND = _sounds["stomp"]
BOSS_HIT_SOUND = _sounds["boss_hit"]
GAME_OVER_SOUND = _sounds["game_over"]
LEVEL_COMPLETE_SOUND = _sounds["level_complete"]

# Convenience re-exports used by some legacy callers
play_sound = audio.play_sound
start_background_music = audio.start_background_music
start_boss_music = audio.start_boss_music
stop_background_music = audio.stop_background_music
return_to_normal_music = audio.return_to_normal_music
set_music_volume = audio.set_music_volume

clamp = lambda v, lo, hi: max(lo, min(hi, v))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Super Ahaanio")
    clock = pygame.time.Clock()

    # --- Load persistent data ---
    settings = load_settings(DEFAULT_SETTINGS)
    settings.setdefault("controls", dict(DEFAULT_SETTINGS["controls"]))
    settings.setdefault("difficulty_preset", "Normal")
    balance = dict(DEFAULT_SETTINGS["balance"])
    balance.update(settings.get("balance", {}))
    settings["balance"] = balance
    progress = load_progress(DEFAULT_PROGRESS)

    # --- Build context ---
    ctx = GameContext()
    ctx.settings = settings
    ctx.balance = balance
    ctx.controls = resolve_controls(settings)
    ctx.progress = progress
    ctx.high_score = load_high_score()
    ctx.music_volume = float(settings.get("music_volume", 0.15))

    # Joystick
    if pygame.joystick.get_count() > 0:
        try:
            ctx.joystick = pygame.joystick.Joystick(0)
            ctx.joystick.init()
        except pygame.error:
            ctx.joystick = None

    # Initialise player and level 1
    ctx.player = Player()
    apply_player_profile(ctx)
    load_normal_level(ctx)
    ctx.transition = TransitionManager()
    ctx.transition.start_fade_in()  # fade in on game start

    # --- Main loop ---
    running = True
    while running:
        jump_pressed = False
        keydown_events: list = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                keydown_events.append(event.key)
                if event.key == ctx.controls["jump"]:
                    jump_pressed = True
                if event.key == pygame.K_F1:
                    settings["reduced_motion"] = not settings.get("reduced_motion", False)
                if event.key == pygame.K_F2:
                    settings["assist_mode"] = not settings.get("assist_mode", False)
                    if settings.get("assist_mode"):
                        ctx.player.lives = max(ctx.player.lives, 3)

        keys = pygame.key.get_pressed()

        # Joystick
        joy_left = ctx.joystick is not None and ctx.joystick.get_axis(0) < -0.4
        joy_right = ctx.joystick is not None and ctx.joystick.get_axis(0) > 0.4
        joy_jump = ctx.joystick is not None and ctx.joystick.get_button(0)
        if joy_jump and not ctx.prev_joy_jump:
            jump_pressed = True
        ctx.prev_joy_jump = joy_jump

        actions = {
            "left":          keys[ctx.controls["left"]] or joy_left,
            "right":         keys[ctx.controls["right"]] or joy_right,
            "jump":          keys[ctx.controls["jump"]] or joy_jump,
            "jump_pressed":  jump_pressed,
            "down":          keys[ctx.controls["pipe_down"]] or (
                ctx.joystick is not None and ctx.joystick.get_axis(1) > 0.5
            ),
            "pause_pressed": keys[ctx.controls["pause"]] or keys[ctx.controls["alt_pause"]],
        }

        # --- Dispatch to state handler ---
        prev_state = ctx.state
        state = ctx.state
        if state == GameState.START:
            ctx.state = handle_start(ctx, screen, keydown_events, keys)
        elif state == GameState.STORY:
            ctx.state = handle_story(ctx, screen, keydown_events, keys)
        elif state == GameState.SETTINGS:
            ctx.state = handle_settings(ctx, screen, keydown_events, keys)
        elif state == GameState.LEVEL_SELECT:
            ctx.state = handle_level_select(ctx, screen, keydown_events, keys)
        elif state == GameState.PLAY:
            ctx.state = handle_play(ctx, screen, keydown_events, keys, actions, _sounds)
        elif state == GameState.GAMEOVER:
            ctx.state = handle_gameover(ctx, screen, keydown_events, keys)
        elif state == GameState.COMPLETE:
            ctx.state = handle_complete(ctx, screen, keydown_events, keys)
        elif state == GameState.CUTSCENE_LEFT_CONTROLLER:
            ctx.state = handle_left_controller(ctx, screen, keydown_events, keys)
        elif state == GameState.CUTSCENE_RIGHT_CONTROLLER:
            ctx.state = handle_right_controller(ctx, screen, keydown_events, keys)
        elif state == GameState.CUTSCENE_SCREEN:
            ctx.state = handle_screen_piece(ctx, screen, keydown_events, keys)
        elif state == GameState.VICTORY_CUTSCENE:
            ctx.state = handle_victory_cutscene(ctx, screen, keydown_events, keys)
        elif state == GameState.CONGRATULATIONS:
            ctx.state = handle_congratulations(ctx, screen, keydown_events, keys)

        # Trigger fade on state change
        if ctx.state != prev_state and ctx.transition:
            ctx.transition.start_fade_in()
        if ctx.transition:
            ctx.transition.update()
            ctx.transition.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    # --- Save on exit ---
    ctx.settings["music_volume"] = round(ctx.music_volume, 3)
    save_settings(ctx.settings)
    save_progress(ctx.progress)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
