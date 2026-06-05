"""
gameplay.py — the PLAY state update + render pass.

Handles:
  • biome physics (wind, gravity)
  • player movement & jump sound
  • combo timer
  • mom / boss / enemy logic
  • coin / powerup / token collection
  • pipe warp in/out
  • flag collision & level completion
  • camera update & checkpoint
  • coin-goal bookkeeping
  • danger music volume boost
  • particle update
  • background + level element rendering
  • HUD overlay
  • pause overlay (drawn on top when game_paused)
"""
from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING, Any, Dict, List

import pygame

from game import audio
from game.constants import (
    BLACK, BLUE, BROWN, FLAGPOLE, GOLDEN, GRAVITY, GREEN, HEIGHT,
    JUMP_HEIGHT, LEVEL_END_X, PIPE_GREEN, RED, SKIN, WHITE, WIDTH, YELLOW,
)
from game.objects import Particle
from game.renderer import get_font, build_gradient_surface
from game.states import GameState
from game.level_manager import (
    load_normal_level, load_boss_level, load_secret_level,
    apply_player_profile, reset_checkpoint, reset_camera, get_biome_modifiers,
)

if TYPE_CHECKING:
    from game.context import GameContext


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def handle(ctx: "GameContext", screen: pygame.Surface,
           keydown_events: List[int], keys,
           actions: Dict[str, Any],
           sounds: Dict[str, Any]) -> GameState:
    """Run one frame of the PLAY state.  Returns the new GameState."""

    # --- Pause toggle ---
    if actions["pause_pressed"]:
        if not ctx.input_state["pause_key_pressed"]:
            ctx.game_paused = not ctx.game_paused
            ctx.pause_menu_selection = 0
        ctx.input_state["pause_key_pressed"] = True
    else:
        ctx.input_state["pause_key_pressed"] = False

    next_state = GameState.PLAY

    if ctx.game_paused:
        next_state = _handle_pause_input(ctx, keys, actions)
    else:
        next_state = _update_game_logic(ctx, keys, actions, sounds)

    # --- Render ---
    _render(ctx, screen, sounds)

    return next_state


# ---------------------------------------------------------------------------
# Pause input
# ---------------------------------------------------------------------------

def _handle_pause_input(ctx: "GameContext", keys, actions) -> GameState:
    if keys[pygame.K_UP]:
        if not ctx.input_state["up_key_pressed"]:
            ctx.pause_menu_selection = (ctx.pause_menu_selection - 1) % 4
        ctx.input_state["up_key_pressed"] = True
    else:
        ctx.input_state["up_key_pressed"] = False

    if keys[pygame.K_DOWN]:
        if not ctx.input_state["down_key_pressed"]:
            ctx.pause_menu_selection = (ctx.pause_menu_selection + 1) % 4
        ctx.input_state["down_key_pressed"] = True
    else:
        ctx.input_state["down_key_pressed"] = False

    if keys[ctx.controls["jump"]] or keys[pygame.K_RETURN]:
        if not ctx.input_state["select_key_pressed"]:
            if ctx.pause_menu_selection == 0:   # Resume
                ctx.game_paused = False
            elif ctx.pause_menu_selection == 1:  # Restart Level
                ctx.game_paused = False
                _restart_current_level(ctx)
            elif ctx.pause_menu_selection == 2:  # Settings
                ctx.game_paused = False
                ctx.settings_return_state = GameState.PLAY
                return GameState.SETTINGS
            elif ctx.pause_menu_selection == 3:  # Go to Home
                ctx.game_paused = False
                _go_home(ctx)
                return GameState.START
        ctx.input_state["select_key_pressed"] = True
    else:
        ctx.input_state["select_key_pressed"] = False

    return GameState.PLAY


def _restart_current_level(ctx: "GameContext") -> None:
    from game.player import Player
    saved_lives = ctx.player.lives
    ctx.player = Player()
    apply_player_profile(ctx)
    ctx.player.lives = max(saved_lives, 3) if ctx.settings.get("assist_mode") else saved_lives
    if ctx.in_secret_world:
        load_secret_level(ctx)
    elif ctx.current_level % 3 == 0:
        load_boss_level(ctx)
    else:
        load_normal_level(ctx)
    reset_checkpoint(ctx)
    reset_camera(ctx)
    ctx.pipe_entry_timer = 0
    ctx.coin_goal_done = False


def _go_home(ctx: "GameContext") -> None:
    from game.player import Player
    ctx.player = Player()
    apply_player_profile(ctx)
    ctx.current_level = 1
    ctx.score = 0
    ctx.in_secret_world = False
    ctx.boss = None
    load_normal_level(ctx)
    reset_checkpoint(ctx)
    reset_camera(ctx)
    ctx.pipe_entry_timer = 0
    ctx.coin_goal_done = False


# ---------------------------------------------------------------------------
# Game logic update
# ---------------------------------------------------------------------------

def _update_game_logic(ctx: "GameContext", keys, actions, sounds) -> GameState:
    biome_mods = get_biome_modifiers(ctx.current_level, ctx.in_secret_world)
    ctx.player.current_gravity = GRAVITY * biome_mods["gravity"]
    ctx.player.current_wind = biome_mods["wind"]

    # Music volume hotkeys
    if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:
        ctx.music_volume = min(1.0, ctx.music_volume + 0.01)
        audio.set_music_volume(ctx.music_volume)
        ctx.settings["music_volume"] = round(ctx.music_volume, 3)
    if keys[pygame.K_MINUS]:
        ctx.music_volume = max(0.0, ctx.music_volume - 0.01)
        audio.set_music_volume(ctx.music_volume)
        ctx.settings["music_volume"] = round(ctx.music_volume, 3)
    if keys[pygame.K_m]:
        if ctx.music_volume > 0:
            audio.set_music_volume(0)
            ctx.settings["music_volume"] = 0.0
        else:
            ctx.music_volume = 0.15
            audio.set_music_volume(ctx.music_volume)
            ctx.settings["music_volume"] = round(ctx.music_volume, 3)

    ctx.player.move(ctx.platforms, actions)
    if ctx.player._just_jumped:
        audio.play_sound(sounds["jump"])

    # Combo timer
    if ctx.combo_timer > 0:
        ctx.combo_timer -= 1
    else:
        ctx.combo_count = 0

    # --- Mom ---
    next_state = GameState.PLAY
    if ctx.mom:
        ctx.mom.update()
        for slipper in ctx.mom.slippers[:]:
            if ctx.player.rect.colliderect(slipper.rect) and not ctx.player.is_immune():
                if ctx.player.die():
                    return GameState.GAMEOVER
                audio.play_sound(sounds["boss_hit"])
                ctx.player.rect.x = ctx.checkpoint_x
                ctx.player.rect.y = HEIGHT - 120
                break

    # --- Boss ---
    if ctx.boss:
        ctx.boss.update(ctx.player)
        for slipper in ctx.boss.slippers[:]:
            if ctx.player.rect.colliderect(slipper.rect) and not ctx.player.is_immune():
                if ctx.player.die():
                    return GameState.GAMEOVER
                audio.play_sound(sounds["boss_hit"])
                ctx.player.rect.x = ctx.checkpoint_x
                ctx.player.rect.y = HEIGHT - 120
                break

        if ctx.player.rect.colliderect(ctx.boss.rect):
            p = ctx.player
            b = ctx.boss
            if p.vy > 0 and p.rect.bottom - b.rect.top < 40 and p.rect.top < b.rect.top + 10:
                if b.take_damage():
                    p.vy = JUMP_HEIGHT // 2
                    ctx.score += 500
                    audio.play_sound(sounds["boss_hit"])
                    ctx.screen_shake = 8
                    if b.is_defeated():
                        ctx.score += 1000
                        boss_number = ctx.current_level // 3
                        if boss_number == 1 and not ctx.switch_parts['left_controller']:
                            ctx.switch_parts['left_controller'] = True
                            ctx.switch_parts_count += 1
                            return GameState.CUTSCENE_LEFT_CONTROLLER
                        elif boss_number == 2 and not ctx.switch_parts['right_controller']:
                            ctx.switch_parts['right_controller'] = True
                            ctx.switch_parts_count += 1
                            return GameState.CUTSCENE_RIGHT_CONTROLLER
                        elif boss_number == 3 and not ctx.switch_parts['screen']:
                            ctx.switch_parts['screen'] = True
                            ctx.switch_parts_count += 1
                            return GameState.CUTSCENE_SCREEN
                        else:
                            return GameState.COMPLETE
            elif not p.is_immune():
                if p.die():
                    return GameState.GAMEOVER
                audio.play_sound(sounds["boss_hit"])
                p.rect.x = ctx.checkpoint_x
                p.rect.y = HEIGHT - 120

    # --- Regular enemies ---
    remove_enemies = []
    for enemy in ctx.enemies:
        enemy.move(ctx.platforms)
        if enemy.enemy_type == "badminton":
            for shuttlecock in enemy.shuttlecocks[:]:
                if ctx.player.rect.colliderect(shuttlecock.rect) and not ctx.player.is_immune():
                    if ctx.player.die():
                        return GameState.GAMEOVER
                    audio.play_sound(sounds["boss_hit"])
                    ctx.player.rect.x = ctx.checkpoint_x
                    ctx.player.rect.y = HEIGHT - 120
                    enemy.shuttlecocks.remove(shuttlecock)
                    break

    for i, enemy in enumerate(ctx.enemies):
        if ctx.player.rect.colliderect(enemy.rect) and not ctx.player.is_immune():
            p = ctx.player
            if (p.vy > 0 and p.rect.bottom - enemy.rect.top < 24
                    and p.rect.top < enemy.rect.top):
                remove_enemies.append(i)
                p.vy = JUMP_HEIGHT // 2
                ctx.combo_count += 1
                ctx.combo_timer = int(ctx.balance.get("combo_window_frames", 75))
                ctx.score += 100 * ctx.combo_count
                audio.play_sound(sounds["stomp"])
                ctx.screen_shake = 6
                for _ in range(8):
                    ctx.particles.append(Particle(
                        enemy.rect.centerx, enemy.rect.bottom, YELLOW,
                        random.uniform(-2.2, 2.2), random.uniform(-2.8, -0.5),
                        life=24, radius=3,
                    ))
            else:
                if p.die():
                    return GameState.GAMEOVER
                audio.play_sound(sounds["boss_hit"])
                p.rect.x = ctx.checkpoint_x
                p.rect.y = HEIGHT - 120
                break

    for idx in sorted(remove_enemies, reverse=True):
        del ctx.enemies[idx]

    # --- Coins ---
    for coin in ctx.coins[:]:
        if ctx.player.rect.colliderect(coin.rect):
            ctx.coins.remove(coin)
            ctx.score += 1
            audio.play_sound(sounds["coin"])
            for _ in range(5):
                ctx.particles.append(Particle(
                    coin.rect.centerx, coin.rect.centery, GOLDEN,
                    random.uniform(-1.3, 1.3), random.uniform(-2.0, -0.2),
                    life=20, radius=2,
                ))

    # --- Power-ups ---
    for powerup in ctx.powerups[:]:
        if not powerup.collected and ctx.player.rect.colliderect(powerup.rect):
            powerup.collected = True
            ctx.player.apply_powerup(powerup.power_type)
            ctx.powerups.remove(powerup)
            ctx.score += 50
            audio.play_sound(sounds["level_complete"])
            for _ in range(10):
                ctx.particles.append(Particle(
                    powerup.rect.centerx, powerup.rect.centery, (255, 180, 120),
                    random.uniform(-2.0, 2.0), random.uniform(-2.5, -0.4),
                    life=26, radius=3,
                ))
    for powerup in ctx.powerups:
        powerup.update()

    # --- Secret tokens ---
    for token in ctx.secret_tokens:
        token.update()
        if not token.collected and ctx.player.rect.colliderect(token.rect):
            token.collected = True
            ctx.tokens_collected += 1
            ctx.score += 200
            for _ in range(12):
                ctx.particles.append(Particle(
                    token.rect.centerx, token.rect.centery, (170, 80, 255),
                    random.uniform(-2.4, 2.4), random.uniform(-3.2, -0.8),
                    life=30, radius=3,
                ))

    # --- Pipes (warp) ---
    pipe_entered = False
    for pipe in ctx.pipes:
        if ctx.player.rect.colliderect(pipe.rect):
            if ctx.player.rect.bottom > pipe.rect.top and ctx.player.vy >= 0:
                ctx.player.rect.bottom = pipe.rect.top
                ctx.player.vy = 0
                ctx.player.on_ground = True

            if (pipe.is_warp_pipe and actions["down"]
                    and ctx.player.on_ground and ctx.pipe_entry_timer <= 0
                    and not pipe_entered):
                pipe_entered = True
                if not ctx.in_secret_world:
                    _enter_secret_world(ctx)
                    audio.play_sound(sounds["level_complete"])
                else:
                    _exit_secret_world(ctx)
                    audio.play_sound(sounds["jump"])
                break

    if ctx.pipe_entry_timer > 0:
        ctx.pipe_entry_timer -= 1

    # --- Flag / level end ---
    if ctx.flag and ctx.player.rect.colliderect(ctx.flag.rect):
        if ctx.in_secret_world:
            _complete_secret_world(ctx)
            audio.play_sound(sounds["level_complete"])
        else:
            return GameState.COMPLETE

    # --- Camera ---
    ctx.camera_x = ctx.player.rect.centerx - WIDTH // 2
    ctx.camera_x = max(0, min(ctx.camera_x, LEVEL_END_X + 100 - WIDTH))

    # --- Checkpoint ---
    if not ctx.checkpoint_reached and ctx.player.rect.x >= LEVEL_END_X // 2:
        ctx.checkpoint_reached = True
        ctx.checkpoint_x = ctx.player.rect.x
        ctx.score += int(ctx.balance.get("checkpoint_bonus", 120))

    # --- Coin goal ---
    collected = ctx.coin_goal - len(ctx.coins)
    if not ctx.coin_goal_done and collected >= ctx.coin_goal:
        ctx.coin_goal_done = True
        ctx.score += int(ctx.balance.get("coin_goal_bonus", 350))

    # --- Dynamic music volume (danger boost) ---
    danger = False
    if ctx.boss:
        danger = abs(ctx.player.rect.centerx - ctx.boss.rect.centerx) < 180
    if not danger:
        for enemy in ctx.enemies:
            if abs(enemy.rect.centerx - ctx.player.rect.centerx) < 130:
                danger = True
                break
    target_vol = ctx.music_volume + (0.08 if danger else 0.0)
    audio.set_music_volume(_clamp(target_vol, 0.0, 1.0))

    return GameState.PLAY


# ---------------------------------------------------------------------------
# Pipe helpers
# ---------------------------------------------------------------------------

def _enter_secret_world(ctx: "GameContext") -> None:
    ctx.in_secret_world = True
    ctx.return_level = ctx.current_level
    ctx.return_score = ctx.score
    ctx.secret_world_type = ((ctx.current_level - 1) % 3) + 1
    load_secret_level(ctx)
    ctx.score += 500
    ctx.player.rect.x = 150
    ctx.player.rect.y = HEIGHT - 100
    ctx.player.vy = 0
    reset_camera(ctx)
    ctx.pipe_entry_timer = 60


def _exit_secret_world(ctx: "GameContext") -> None:
    ctx.in_secret_world = False
    ctx.current_level = ctx.return_level
    if ctx.current_level % 3 == 0:
        load_boss_level(ctx)
    else:
        load_normal_level(ctx)
    ctx.player.rect.x = 150
    ctx.player.rect.y = HEIGHT - 100
    ctx.player.vy = 0
    reset_camera(ctx)
    ctx.pipe_entry_timer = 60


def _complete_secret_world(ctx: "GameContext") -> None:
    ctx.score += 1000
    ctx.in_secret_world = False
    ctx.current_level = ctx.return_level
    if ctx.current_level % 3 == 0:
        load_boss_level(ctx)
    else:
        load_normal_level(ctx)
    ctx.player.rect.x = 150
    ctx.player.rect.y = HEIGHT - 100
    ctx.player.vy = 0
    reset_camera(ctx)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _render(ctx: "GameContext", screen: pygame.Surface, sounds) -> None:
    # Particle update
    ctx.particles = [p for p in ctx.particles if not p.update()]
    if ctx.screen_shake > 0:
        ctx.screen_shake -= 1

    # Background
    _draw_background(ctx, screen)

    # Moving platforms
    _update_moving_platforms(ctx)

    cam = ctx.camera_x
    if ctx.screen_shake > 0:
        cam += random.randint(-4, 4)

    # Level elements
    for platform in ctx.platforms:
        platform.draw(screen, cam)
    for pipe in ctx.pipes:
        pipe.draw(screen, cam)
    for enemy in ctx.enemies:
        enemy.draw(screen, cam)
    for coin in ctx.coins:
        coin.draw(screen, cam)
    for powerup in ctx.powerups:
        powerup.draw(screen, cam)
    for token in ctx.secret_tokens:
        token.draw(screen, cam)
    if ctx.flag:
        ctx.flag.draw(screen, cam)
    if ctx.mom:
        ctx.mom.draw(screen, cam)
    if ctx.boss:
        ctx.boss.draw(screen, cam)
    ctx.player.draw(screen, cam)
    for particle in ctx.particles:
        particle.draw(screen, cam)

    # HUD
    _draw_hud(ctx, screen)

    # Pause overlay
    if ctx.game_paused:
        _draw_pause_overlay(ctx, screen)


def _draw_background(ctx: "GameContext", screen: pygame.Surface) -> None:
    reduced = ctx.settings.get("reduced_motion", False)
    if reduced:
        if ctx.in_secret_world:
            screen.fill((40, 30, 80))
        elif ctx.current_level == 5:
            screen.fill((220, 225, 230))
        else:
            screen.fill((130, 205, 255))
    elif ctx.in_secret_world:
        t = ctx.cutscene_timer
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(128 + 127 * math.sin(ratio * 2 + t * 0.05))
            g = int(128 + 127 * math.sin(ratio * 2 + 2 + t * 0.05))
            b = int(128 + 127 * math.sin(ratio * 2 + 4 + t * 0.05))
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    elif ctx.current_level == 5:
        screen.blit(build_gradient_surface((180, 190, 200), (240, 240, 240)), (0, 0))
        cam = ctx.camera_x
        pygame.draw.rect(screen, (210, 180, 140), (0 - cam, HEIGHT - 50, LEVEL_END_X + 200, 50))
    else:
        screen.blit(build_gradient_surface((92, 192, 255), (142, 232, 255)), (0, 0))
        random.seed(42)
        for i in range(8):
            cx = (i * 250 + random.randint(-50, 50) - ctx.camera_x // 3) % (WIDTH + 200) - 100
            cy = 50 + random.randint(-20, 40)
            for j in range(4):
                rx = cx + j * 15 + random.randint(-5, 5)
                ry = cy + random.randint(-8, 8)
                rs = 15 + random.randint(-3, 8)
                pygame.draw.circle(screen, WHITE, (int(rx), int(ry)), rs)
                pygame.draw.circle(screen, (240, 240, 255), (int(rx - 2), int(ry - 2)), rs - 2)


def _update_moving_platforms(ctx: "GameContext") -> None:
    for platform in ctx.platforms:
        if not hasattr(platform, 'update'):
            continue
        old_x, old_y = platform.rect.x, platform.rect.y
        on_it = (
            ctx.player.rect.bottom <= platform.rect.top + 10
            and ctx.player.rect.bottom >= platform.rect.top - 5
            and ctx.player.rect.centerx >= platform.rect.left - 10
            and ctx.player.rect.centerx <= platform.rect.right + 10
        )
        platform.update()
        if on_it:
            dx = platform.rect.x - old_x
            dy = platform.rect.y - old_y
            ctx.player.rect.x += dx
            ctx.player.rect.y += dy
        for enemy in ctx.enemies:
            if hasattr(enemy, 'platform') and enemy.platform == platform.rect:
                dx = platform.rect.x - old_x
                dy = platform.rect.y - old_y
                enemy.rect.x += dx
                enemy.rect.y += dy


def _draw_hud(ctx: "GameContext", screen: pygame.Surface) -> None:
    font = get_font(36)

    # Score + combo
    screen.blit(font.render(f'Score: {ctx.score}', True, BLACK), (10, 10))
    combo_color = RED if ctx.combo_count > 1 else BLACK
    screen.blit(get_font(28).render(f'Combo: x{max(1, ctx.combo_count)}', True, combo_color), (10, 38))

    # Level / secret world indicator
    if ctx.in_secret_world:
        screen.blit(font.render(f'SECRET WORLD {ctx.secret_world_type}!', True, GOLDEN), (10, 50))
        screen.blit(get_font(24).render('Find warp pipes to return!', True, YELLOW), (10, 90))
    elif ctx.current_level == 5:
        screen.blit(font.render('Level 5: BADMINTON COURT!', True, RED), (10, 50))
        screen.blit(get_font(24).render('⚠️ Forced Badminton Class! ⚠️', True, (255, 100, 100)), (10, 85))
    else:
        screen.blit(font.render(f'Level: {ctx.current_level}', True, BLACK), (10, 50))
        if audio.current_music_type == "boss":
            screen.blit(get_font(28).render('♪ BOSS FIGHT ♪', True, RED), (10, 85))

    # Lives
    lives_y = 130 if ctx.in_secret_world else (115 if audio.current_music_type == "boss" else 90)
    screen.blit(font.render(f'Lives: {ctx.player.lives}', True, BLACK), (10, lives_y))

    # Switch parts
    parts_y = 160 if ctx.in_secret_world else (145 if audio.current_music_type == "boss" else 120)
    screen.blit(get_font(28).render(f'Switch Parts: {ctx.switch_parts_count}/3', True, BLACK), (10, parts_y))
    screen.blit(get_font(24).render(f'Secret Tokens: {ctx.tokens_collected}', True, (120, 0, 180)), (10, parts_y + 24))

    # Visual Switch parts indicators
    sx, sy = 200, parts_y
    # Left controller
    if ctx.switch_parts['left_controller']:
        pygame.draw.rect(screen, BLUE, (sx, sy, 20, 25))
        pygame.draw.circle(screen, BLACK, (sx + 10, sy + 8), 3)
    else:
        pygame.draw.rect(screen, (100, 100, 100), (sx, sy, 20, 25))
        pygame.draw.rect(screen, BLACK, (sx, sy, 20, 25), 2)
    # Screen
    if ctx.switch_parts['screen']:
        pygame.draw.rect(screen, BLACK, (sx + 25, sy + 3, 30, 19))
        pygame.draw.rect(screen, (100, 255, 100), (sx + 27, sy + 5, 26, 15))
    else:
        pygame.draw.rect(screen, (100, 100, 100), (sx + 25, sy + 3, 30, 19))
        pygame.draw.rect(screen, BLACK, (sx + 25, sy + 3, 30, 19), 2)
    # Right controller
    if ctx.switch_parts['right_controller']:
        pygame.draw.rect(screen, RED, (sx + 60, sy, 20, 25))
        pygame.draw.circle(screen, BLACK, (sx + 70, sy + 8), 3)
    else:
        pygame.draw.rect(screen, (100, 100, 100), (sx + 60, sy, 20, 25))
        pygame.draw.rect(screen, BLACK, (sx + 60, sy, 20, 25), 2)

    # Warp pipe hint
    near_warp = any(
        pipe.is_warp_pipe and ctx.player.rect.colliderect(
            pygame.Rect(pipe.rect.x - 30, pipe.rect.y - 30, pipe.rect.w + 60, pipe.rect.h + 60))
        for pipe in ctx.pipes
    )
    if near_warp and ctx.pipe_entry_timer <= 0:
        if ctx.in_secret_world:
            hint = get_font(28).render('Press DOWN to return to normal world!', True, YELLOW)
        else:
            hint = get_font(28).render('Press DOWN to enter SECRET WORLD!', True, GOLDEN)
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 80))

    # Power-up status
    ui_y = 170 if ctx.in_secret_world else 130
    if ctx.player.speed_boost > 0:
        screen.blit(get_font(24).render(f'Speed Boost: {ctx.player.speed_timer // 60 + 1}s', True, GREEN), (10, ui_y))
    if ctx.player.jump_boost < 0:
        screen.blit(get_font(24).render(f'Jump Boost: {ctx.player.jump_timer // 60 + 1}s', True, BLUE), (10, ui_y + 20))
    if ctx.player.is_immune():
        screen.blit(get_font(24).render(f'Immune: {ctx.player.immunity_timer // 60 + 1}s', True, YELLOW), (10, ui_y + 40))

    # Coin objective
    obj_color = GREEN if ctx.coin_goal_done else BLACK
    screen.blit(get_font(24).render(
        f'Objective: Coins {ctx.coin_goal - len(ctx.coins)}/{ctx.coin_goal}', True, obj_color,
    ), (10, ui_y + 60))

    if ctx.checkpoint_reached:
        screen.blit(get_font(24).render("Checkpoint Active", True, (0, 120, 0)), (10, ui_y + 80))

    if ctx.boss:
        screen.blit(get_font(28).render(f'Boss Stage: {ctx.boss.stage}/3', True, RED), (10, ui_y + 70))

    # Music controls hint (top-right)
    screen.blit(get_font(20).render('Music: +/- Volume, M Mute', True, BLACK), (WIDTH - 200, 10))
    screen.blit(get_font(20).render(f'Vol: {int(ctx.music_volume * 100)}%', True, BLACK), (WIDTH - 200, 30))
    screen.blit(get_font(20).render('ESC/P: Pause', True, BLACK), (WIDTH - 200, 50))
    access = get_font(20).render(
        f"F1 Motion:{'Off' if ctx.settings.get('reduced_motion') else 'On'}  "
        f"F2 Assist:{'On' if ctx.settings.get('assist_mode') else 'Off'}",
        True, BLACK,
    )
    screen.blit(access, (WIDTH - 330, 70))


def _draw_pause_overlay(ctx: "GameContext", screen: pygame.Surface) -> None:
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    mw, mh = 300, 200
    mx = (WIDTH - mw) // 2
    my = (HEIGHT - mh) // 2
    pygame.draw.rect(screen, WHITE, (mx, my, mw, mh))
    pygame.draw.rect(screen, BLACK, (mx, my, mw, mh), 3)

    title_text = get_font(48).render("PAUSED", True, BLACK)
    screen.blit(title_text, (mx + (mw - title_text.get_width()) // 2, my + 20))

    options = ["Resume", "Restart Level", "Settings", "Go to Home"]
    for i, option in enumerate(options):
        color = RED if i == ctx.pause_menu_selection else BLACK
        opt_text = get_font(36).render(option, True, color)
        ox = mx + (mw - opt_text.get_width()) // 2
        oy = my + 80 + i * 40
        screen.blit(opt_text, (ox, oy))
        if i == ctx.pause_menu_selection:
            ax = ox - 30
            ay = oy + opt_text.get_height() // 2
            pygame.draw.polygon(screen, RED, [(ax, ay - 8), (ax, ay + 8), (ax + 15, ay)])

    inst = get_font(24).render("↑↓ Navigate, SPACE/ENTER Select", True, BLACK)
    screen.blit(inst, (mx + (mw - inst.get_width()) // 2, my + mh - 30))
