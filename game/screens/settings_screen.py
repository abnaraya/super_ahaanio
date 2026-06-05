"""SETTINGS screen."""
from __future__ import annotations

from typing import TYPE_CHECKING, List

import pygame

from game import audio
from game.constants import DEFAULT_SETTINGS, DIFFICULTY_PRESETS, WHITE, YELLOW, HEIGHT, WIDTH
from game.renderer import get_font
from game.states import GameState
from game.level_manager import apply_player_profile, configure_level_difficulty, derive_coin_goal

if TYPE_CHECKING:
    from game.context import GameContext


def _key_label(key: int) -> str:
    name = pygame.key.name(key)
    return name.upper() if name else str(key)


def _clamp(value, lo, hi):
    return max(lo, min(hi, value))


# Ordered list of setting rows
_SETTING_ROWS = [
    ("toggle",   "Reduced Motion",   "reduced_motion"),
    ("toggle",   "Assist Mode",      "assist_mode"),
    ("preset",   "Difficulty Preset","difficulty_preset"),
    ("gameplay", "Diff/Level",       "difficulty_per_level"),
    ("gameplay", "Combo Window",     "combo_window_frames"),
    ("gameplay", "Coin Goal Ratio",  "coin_goal_ratio"),
    ("gameplay", "Checkpoint Bonus", "checkpoint_bonus"),
    ("gameplay", "Coin Goal Bonus",  "coin_goal_bonus"),
    ("volume",   "Music Volume",     None),
    ("rebind",   "Move Left",        "left"),
    ("rebind",   "Move Right",       "right"),
    ("rebind",   "Jump",             "jump"),
    ("rebind",   "Pause",            "pause"),
    ("rebind",   "Pipe Down",        "pipe_down"),
    ("action",   "Reset Controls",   "reset_controls"),
    ("action",   "Reset Gameplay",   "reset_gameplay"),
    ("action",   "Back",             "back"),
]

_GAMEPLAY_FIELDS = {
    "difficulty_per_level": ("Diff/Level", 0.01, 0.12, 0.01, 2),
    "combo_window_frames":  ("Combo Window", 40, 140, 5, 0),
    "coin_goal_ratio":      ("Coin Goal Ratio", 0.3, 0.9, 0.05, 2),
    "checkpoint_bonus":     ("Checkpoint Bonus", 0, 400, 20, 0),
    "coin_goal_bonus":      ("Coin Goal Bonus", 0, 700, 25, 0),
}


def handle(ctx: "GameContext", screen: pygame.Surface,
           keydown_events: List[int], keys) -> GameState:
    preset_names = list(DIFFICULTY_PRESETS.keys())
    ctx.settings_menu_selection = _clamp(ctx.settings_menu_selection, 0, len(_SETTING_ROWS) - 1)

    if ctx.rebinding_action is not None:
        for key in keydown_events:
            if key == pygame.K_ESCAPE:
                ctx.rebinding_action = None
                break
            if key not in (pygame.K_F1, pygame.K_F2):
                ctx.settings["controls"][ctx.rebinding_action] = key
                ctx.controls = _resolve_controls(ctx.settings)
                ctx.rebinding_action = None
                break
    else:
        if pygame.K_UP in keydown_events:
            ctx.settings_menu_selection = (ctx.settings_menu_selection - 1) % len(_SETTING_ROWS)
        if pygame.K_DOWN in keydown_events:
            ctx.settings_menu_selection = (ctx.settings_menu_selection + 1) % len(_SETTING_ROWS)

        row_type, _, row_key = _SETTING_ROWS[ctx.settings_menu_selection]

        if row_type == "volume":
            if pygame.K_LEFT in keydown_events:
                ctx.music_volume = _clamp(ctx.music_volume - 0.05, 0.0, 1.0)
                ctx.settings["music_volume"] = round(ctx.music_volume, 3)
                audio.set_music_volume(ctx.music_volume)
            if pygame.K_RIGHT in keydown_events:
                ctx.music_volume = _clamp(ctx.music_volume + 0.05, 0.0, 1.0)
                ctx.settings["music_volume"] = round(ctx.music_volume, 3)
                audio.set_music_volume(ctx.music_volume)

        elif row_type == "preset":
            cur = ctx.settings.get("difficulty_preset", "Normal")
            if cur not in preset_names:
                cur = "Normal"
            idx = preset_names.index(cur)
            changed = False
            if pygame.K_LEFT in keydown_events:
                idx = (idx - 1) % len(preset_names); changed = True
            if pygame.K_RIGHT in keydown_events:
                idx = (idx + 1) % len(preset_names); changed = True
            if changed:
                name = preset_names[idx]
                ctx.settings["difficulty_preset"] = name
                ctx.balance.update(DIFFICULTY_PRESETS[name])
                ctx.settings["balance"] = dict(ctx.balance)
                apply_player_profile(ctx)
                configure_level_difficulty(ctx.current_level, ctx.in_secret_world,
                                           ctx.enemies, ctx.boss, ctx.balance)
                ctx.coin_goal = derive_coin_goal(ctx.coins, ctx.balance)
                ctx.coin_goal_done = False

        elif row_type == "gameplay":
            _, min_v, max_v, step_v, round_d = _GAMEPLAY_FIELDS[row_key]
            value = ctx.balance.get(row_key, DEFAULT_SETTINGS["balance"][row_key])
            changed = False
            if pygame.K_LEFT in keydown_events:
                value = _clamp(value - step_v, min_v, max_v); changed = True
            if pygame.K_RIGHT in keydown_events:
                value = _clamp(value + step_v, min_v, max_v); changed = True
            if changed:
                value = round(value, round_d) if round_d > 0 else int(value)
                ctx.balance[row_key] = value
                ctx.settings["balance"] = dict(ctx.balance)
                ctx.settings["difficulty_preset"] = "Custom"
                apply_player_profile(ctx)
                configure_level_difficulty(ctx.current_level, ctx.in_secret_world,
                                           ctx.enemies, ctx.boss, ctx.balance)
                ctx.coin_goal = derive_coin_goal(ctx.coins, ctx.balance)
                ctx.coin_goal_done = False

        if pygame.K_RETURN in keydown_events or ctx.controls.get("jump") in keydown_events:
            if row_type == "toggle":
                ctx.settings[row_key] = not ctx.settings.get(row_key, False)
                if row_key == "assist_mode":
                    apply_player_profile(ctx)
            elif row_type == "preset":
                preset_name = ctx.settings.get("difficulty_preset", "Normal")
                ctx.balance.update(DIFFICULTY_PRESETS.get(preset_name, DIFFICULTY_PRESETS["Normal"]))
                ctx.settings["balance"] = dict(ctx.balance)
                apply_player_profile(ctx)
                configure_level_difficulty(ctx.current_level, ctx.in_secret_world,
                                           ctx.enemies, ctx.boss, ctx.balance)
                ctx.coin_goal = derive_coin_goal(ctx.coins, ctx.balance)
                ctx.coin_goal_done = False
            elif row_type == "rebind":
                ctx.rebinding_action = row_key
            elif row_type == "action" and row_key == "reset_controls":
                ctx.settings["controls"] = dict(DEFAULT_SETTINGS["controls"])
                ctx.controls = _resolve_controls(ctx.settings)
            elif row_type == "action" and row_key == "reset_gameplay":
                ctx.settings["difficulty_preset"] = "Normal"
                ctx.balance.update(dict(DEFAULT_SETTINGS["balance"]))
                ctx.settings["balance"] = dict(ctx.balance)
                apply_player_profile(ctx)
                configure_level_difficulty(ctx.current_level, ctx.in_secret_world,
                                           ctx.enemies, ctx.boss, ctx.balance)
                ctx.coin_goal = derive_coin_goal(ctx.coins, ctx.balance)
                ctx.coin_goal_done = False
            elif row_type == "action" and row_key == "back":
                return ctx.settings_return_state

        if pygame.K_ESCAPE in keydown_events:
            return ctx.settings_return_state

    # --- Draw ---
    screen.fill((18, 22, 35))
    title = get_font(62).render("Settings", True, WHITE)
    subtitle = get_font(24).render("Arrows navigate/adjust, Enter select, Esc back", True, (200, 200, 220))
    screen.blit(title, ((WIDTH - title.get_width()) // 2, 40))
    screen.blit(subtitle, ((WIDTH - subtitle.get_width()) // 2, 95))

    y = 145
    for idx, (row_type, label, row_key) in enumerate(_SETTING_ROWS):
        selected = idx == ctx.settings_menu_selection
        color = YELLOW if selected else WHITE
        value_text = ""
        if row_type == "toggle":
            value_text = "ON" if ctx.settings.get(row_key, False) else "OFF"
        elif row_type == "volume":
            value_text = f"{int(ctx.music_volume * 100)}%"
        elif row_type == "preset":
            value_text = ctx.settings.get("difficulty_preset", "Normal")
        elif row_type == "gameplay":
            val = ctx.balance.get(row_key, DEFAULT_SETTINGS["balance"][row_key])
            value_text = f"{val:.2f}" if isinstance(val, float) else str(val)
        elif row_type == "rebind":
            value_text = _key_label(ctx.controls[row_key])
        line = get_font(34).render(f"{label}: {value_text}" if value_text else label, True, color)
        screen.blit(line, (120, y))
        if selected:
            pygame.draw.polygon(screen, YELLOW, [(90, y + 10), (105, y + 4), (105, y + 16)])
        y += 34

    if ctx.rebinding_action is not None:
        bind_msg = get_font(30).render(
            f"Press a key for {ctx.rebinding_action.replace('_', ' ').title()} (Esc to cancel)",
            True, (255, 220, 140),
        )
        screen.blit(bind_msg, ((WIDTH - bind_msg.get_width()) // 2, HEIGHT - 70))

    return GameState.SETTINGS


def _resolve_controls(settings: dict) -> dict:
    from game.controls import resolve_controls
    return resolve_controls(settings)
