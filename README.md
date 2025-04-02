# Xiangqi (Chinese Chess) Python Project

A Python implementation of Xiangqi (Chinese Chess) featuring an AI opponent using the Minimax algorithm with Alpha-Beta pruning.

## Project Description

This project simulates a game of Xiangqi (Chinese Chess) with a command-line interface. It includes an AI engine capable of making strategic decisions using the Minimax algorithm with Alpha-Beta pruning for optimization. The game supports saving/loading states, move validation, and board visualization with ANSI-colored pieces.

## Features

- **AI Engine**: Uses Minimax with Alpha-Beta pruning to determine optimal moves.
- **Board Visualization**: ANSI-colored pieces and control highlights.
- **Move Validation**: Ensures all moves adhere to Xiangqi rules, including palace restrictions and piece-specific logic.
- **Save/Load System**: Save game states and resume later.
- **Evaluation System**: Scores positions based on piece values, mobility, and board control.
- **Automated & Interactive Play**: Watch AI vs AI matches or modify the code for human vs AI gameplay.

## Installation

1. **Requirements**:
   - Python 3.x (Tested on Python 3.8+)
   - No external dependencies (uses built-in libraries).

2. **Clone the Repository**:
```bash
git clone https://github.com/laines-it/Xiangqi-Engine
```

## Usage
# Running the Game

Execute the game loop (default: AI vs AI) by running:
```bash
python game_enviroment.py
```

## Key Components

**AI vs AI Mode**: The default setup in game_enviroment.py runs an automated game where the engine plays against itself.

**Human vs AI Mode**: Modify the loop in game_enviroment.py to include user input (example provided in comments).

**Save/Load**: Use save_board() and load_board() methods to persist game states.

**Board Visualization**: Run game.print() to display the board in the console.

# Example Modification for Human Input

Uncomment the `input()` line in `game_enviroment.py` and adjust the loop:
```python
while True:
    user_input = input("Press Enter for AI move or input coordinates...")
    if user_input == "":
        # AI move
    else:
        # Parse human input and call select_piece() + make_move()
```

## File Structure

`board.py`: Manages board state, piece movements, and attack calculations.

`pieces.py`: Defines Xiangqi pieces (General, Chariot, Horse, etc.) and their movement logic.

`supports.py`: Contains helper classes (Vector, Move, Color) and enums.

`game_enviroment.py`: Handles game initialization, UI, and save/load functionality.

`engine.py`: Implements the AI engine using Minimax with Alpha-Beta pruning.