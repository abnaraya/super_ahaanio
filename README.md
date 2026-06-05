# Super Ahaanio

A basic 2D platformer game inspired by classic Super Mario Bros, built with Python and pygame.

## Features

- Move left, right, and jump
- Gravity and collision detection with platforms and ground
- Simple enemy characters (with mushroom-style shapes)
- Collectible coins (round, shiny)
- Scrolling level that follows the player
- Start screen and Game Over screen
- Modular code for easy graphics/sound extension

## Controls

- **Left/Right Arrow**: Move player left/right
- **Space**: Jump
- **Space (Start Screen/Game Over)**: Start or Restart game

## Requirements

- Python 3.7+
- pygame (install via `pip install pygame`)

## How to Run

1. Install pygame inside your virtual environment (if not already done):  
  ```
   pip install pygame
   ```
2. Run the game:
  ```
   python main.py
   ```
## Structure

- `main.py` - Main game logic and all classes
- `requirements.txt` - Dependency list

You can extend the artwork by replacing the shape drawing in each object's `draw()` method or by using actual images/sprites for a more Mario-like feel.

## Credits

Built by Ahaan.

## License

MIT
