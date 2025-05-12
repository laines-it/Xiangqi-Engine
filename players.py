from typing import Optional, Dict, Any, Callable, Tuple
from game_enviroment import Game
from engine import Engine
from supports import Color, Vector
import datetime

class Player:
    def __init__(
        self,
        name: str,
        color: Color,
        profile_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.color = color
        self.profile_url = profile_url
        self.metadata = metadata or {}
        self.stats = {
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "moves_made": 0,
            "last_played": None
        }

    def turn(self, game: Game) -> bool:
        """Execute a turn. Returns True if move was successful."""
        raise NotImplementedError

    def update_stats(self, result: str) -> None:
        """Update player statistics."""
        self.stats["last_played"] = datetime.datetime.now()
        if result == "win":
            self.stats["wins"] += 1
        elif result == "loss":
            self.stats["losses"] += 1
        elif result == "draw":
            self.stats["draws"] += 1

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color

    def swap_colors(self, other):
        c = self.color
        self.color = other.get_color()
        other.set_color(c)
        return self.color

class Human(Player):
    """Human player class with interactive input."""
    def __init__(
        self,
        color: Color,
        name: str = "Human",
        input_method: Callable = input,
        **kwargs
    ):
        super().__init__(name, color, **kwargs)
        self.input_method = input_method
        self.metadata["type"] = "human"

    def turn(self, game: Game) -> bool:
        while True:
            try:
                move_str = self.input_method(f"{self.name}'s turn (format 'x,y to x,y'): ")
                from_pos, to_pos = self._parse_input(move_str)

                if game.select_piece(from_pos):
                    if game.make_move(to_pos):
                        self.stats["moves_made"] += 1
                        return True
                    else:
                        print("Invalid move")
                        return False
                else:
                    print("Invalid piece selection")
                    return False
            except (ValueError, IndexError):
                print("Invalid input format")
                return False

    def _parse_input(self, move_str: str) -> Tuple[Vector, Vector]:
        """Parse human input into Vector positions."""
        parts = move_str.strip().split(" to ")
        return (
            Vector(*map(int, parts[0].split(","))),
            Vector(*map(int, parts[1].split(",")))
        )

class Bot(Player):
    """AI player using an engine."""
    def __init__(
        self,
        engine: Engine,
        color: Color,
        name: str = "AI Bot",
        strategy_description: str = "",
        **kwargs
    ):
        super().__init__(name, color, **kwargs)
        self.engine = engine
        self.metadata.update({
            "type": "bot",
            "engine_depth": engine.depth,
            "strategy": strategy_description
        })

    def turn(self, game: Game) -> bool:
        my_eval, best_move = self.engine.get_best_move(game.board, self.color)
        if best_move is None:
            return False

        from_pos, to_pos = best_move
        game.select_piece(from_pos)
        success = game.make_move(to_pos, check=False)
        if success:
            self.stats["moves_made"] += 1
        return success