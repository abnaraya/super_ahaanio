# Super Ahaanio

A 2D platformer game built with Python and Pygame where Ahaan must collect his broken Nintendo Switch pieces by defeating Mom bosses across increasingly challenging levels.

## Story

Ahaan loves his Nintendo Switch, but Mom breaks it into 3 pieces! Navigate through levels filled with homework enemies, chores obstacles, forced badminton, and showers to collect the left Joy-Con, right Joy-Con, and screen by defeating Mom bosses every 3rd level.

## Features

- **20+ levels** with 4 enemy types (homework, chores, badminton, showers)
- **3 Boss fights** against Mom, each dropping a Nintendo Switch piece
- **Double jump** for advanced platforming
- **6 powerup types**: Speed (pizza), Jump (donut), Life (chapati), Invincibility (Nintendo), AoE stomp (Drums), Projectile (Soccer)
- **Bottomless pits** and platforming challenges
- **Mom hazard** appears in later levels, throwing slippers
- **Secret worlds** accessible via warp pipes
- **3 new biomes** for higher levels: Ice, Lava, Underwater
- **Time challenge** with bonus for fast completion
- **Secret token milestones** that unlock permanent rewards
- **Screen transitions** (fade in/out)
- **Combo system** for chaining enemy stomps
- **Difficulty presets** (Easy / Normal / Hard) with granular tuning
- **Rebindable controls** and gamepad support
- **Accessibility**: reduced motion mode (F1), assist mode (F2)
- **Procedural audio** and visuals (no external assets needed besides bgm.mp3)

## Controls

| Action           | Keyboard         | Gamepad       |
|-----------------|-----------------|---------------|
| Move left/right  | Arrow keys       | Left stick    |
| Jump             | Space            | A button      |
| Enter pipe       | Down arrow       | Stick down    |
| Fire soccer ball | Jump + Down      | A + Stick down|
| Pause            | Escape / P       | -             |
| Volume +/-       | + / -            | -             |
| Mute             | M                | -             |
| Reduced motion   | F1               | -             |
| Assist mode      | F2               | -             |

## Requirements

- Python 3.7+
- pygame
- numpy

## How to Run

```bash
pip install pygame numpy
python main.py
```

## Project Structure

```
main.py                  # Entry point, sound bank, main loop
game/
  __init__.py
  constants.py           # Screen dimensions, physics, colors, settings
  context.py             # GameContext — mutable game state container
  states.py              # GameState enum (12 states)
  player.py              # Player movement, jumping, powerups, drawing
  enemies.py             # Enemy types, Shuttlecock, Slipper
  boss.py                # Boss (Mom boss) and Mom (background hazard)
  objects.py             # Platform, Coin, Pipe, Flag, PowerUp, SoccerBall, Particle
  levels.py              # Level creation functions (normal, secret, boss)
  level_manager.py       # Level loading, difficulty, biomes, reset helpers
  gameplay.py            # PLAY state: physics, collisions, HUD, pause menu
  controls.py            # Input key resolution
  audio.py               # Procedural sound effects, music management
  renderer.py            # Font cache, gradient backgrounds, character drawing
  persistence.py         # JSON save/load for high score, settings, progress
  transitions.py         # Screen fade in/out transitions
  screens/
    start.py             # Title screen
    story.py             # 9-page animated intro cutscene
    settings_screen.py   # Settings menu with key rebinding
    level_select.py      # Level grid selector
    gameover.py          # Game over screen
    complete.py          # Level completion screen
    cutscenes.py         # Boss victory cutscenes (Switch pieces)
    victory.py           # Final victory and congratulations
```

## Credits

Built by Ahaan.

## License

MIT
