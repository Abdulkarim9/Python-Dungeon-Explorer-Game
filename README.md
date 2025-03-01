# Dungeon Explorer

A procedurally generated dungeon crawler game created using Pygame. The game features dynamic level generation, engaging combat, and a progression system that increases in difficulty as you advance.

## Features

- **Procedural Generation**: Every playthrough offers a unique dungeon layout using cellular automata algorithms.
- **Multiple Enemy Types**: Face different enemies with unique behaviors and attack patterns:
  - **Slimes**: Slow but resilient enemies that deal moderate damage.
  - **Ghosts**: Fast enemies that can move through walls with medium damage.
  - **Spiders**: Quick enemies with high damage but low health.
- **Power-up System**: Collect items to enhance your abilities:
  - **Health Potions**: Restore your health.
  - **Speed Boots**: Increase your movement speed.
  - **Damage Crystals**: Enhance your attack power.
- **Combat System**: Attack enemies with directional attacks and particle effects.
- **Sound Effects**: Procedurally generated sound effects for different game events.
- **Interactive UI**: Animated menus, health bars, score tracking, and game state screens.
- **Progression**: Navigate through 5 increasingly difficult levels to achieve victory.


## Requirements

- Python 3.6 or higher
- Pygame 2.5.0
- Noise 1.2.2

## Installation

1. Clone this repository or download the source code.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Game

Run the main script to start the game:

```bash
python main.py
```

## Controls

- **Movement**: WASD or Arrow Keys
- **Attack**: Spacebar
- **Menu Navigation**: Enter to confirm, Escape to exit

## Gameplay Tips

1. Keep moving to avoid enemy attacks.
2. Collect power-ups to increase your chances of survival.
3. The exit to the next level is marked with a green square.
4. Enemies become stronger on higher levels, so prioritize collecting damage and speed upgrades.
5. Health potions can be saved for emergencies.

## Code Structure

- **main.py**: Main game loop and state management
- **player.py**: Player character implementation with movement and combat
- **enemy.py**: Enemy classes with AI behaviors
- **level.py**: Procedural dungeon generation
- **item.py**: Collectible items and power-ups
- **ui.py**: User interface components

## Credits

Developed as a demonstration of procedural generation and game development with Pygame. All visual elements are created programmatically using shapes, colors, and algorithms—no external assets were used in the development of this game.

## License

This project is open source and available under the MIT License. 
