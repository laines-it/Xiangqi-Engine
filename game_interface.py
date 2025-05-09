from game_enviroment import Game
from players import Player, Human, Bot
from engine import Engine
from typing import Optional
from supports import Color, EvaluateSet

class GameInterface:
    def __init__(self):
        self.default_eval_set = EvaluateSet(control_multiplier=0, mobility_multiplier=0)
        self.game = Game(eval_set=self.default_eval_set, load=False)
        self.default_engine = Engine(self.default_eval_set, depth=1)  # For deep analysis
        self.red_player : Optional['Player'] = None
        self.black_player : Optional['Player'] = None

    def get_all_of_game(self):
        return self.game.get_all()

    def start_match(self, auto_play: bool = True) -> None:
        print(f"Starting match: {self.red_player.name} (RED) vs {self.black_player.name} (BLACK)")
        i = 1
        while True:
            """
            NEW MOVE
            """
            self.game.print()
            current_player = self.red_player if self.game.current_player_color == Color.RED else self.black_player
            print(f"\nMOVE {i//2}:\n  {current_player.name}'s turn")
            
            success = current_player.turn(self.game)
            if not success:
                break
            if self.game.is_50moves_rule():
                print("TIE")
                break
            i += 1

        self.game.save_board()
        winner = self._determine_winner()
        self.red_player.update_stats("win" if winner == Color.RED else "loss")
        self.black_player.update_stats("win" if winner == Color.BLACK else "loss")
        print(f"Match concluded. Winner: {winner}")

    def _determine_winner(self) -> Color:
        return self.game.current_player_color.opposite()

    def add_players(self, ai=False):
        human1 = Human(name="Alice", color=Color.RED, profile_url="https://example.com/alice")
        human2 = Human(name="PALICE", color=Color.BLACK, profile_url="https://example.com/alice")
    
        bot_engine1 = Engine(EvaluateSet(value_multiplier=10, attack_bonus=0, mobility_multiplier=0, control_multiplier=0), depth=6)
        ai1 = Bot(
            engine=bot_engine1,
            color=Color.RED,
            name="Aggressive AI",
            strategy_description="Prefers attacking moves"
        )

        bot_engine2 = Engine(EvaluateSet(value_multiplier=10, attack_bonus=0, mobility_multiplier=0, control_multiplier=0), depth=6)
        ai2 = Bot(
            engine=bot_engine2,
            name="Defensive AI",
            color=Color.BLACK,
            strategy_description="Prefers controlling moves"
        )
        if ai:
            self.red_player = ai1
            self.black_player = ai2
        else:
            self.red_player = human1
            self.black_player = human2

if __name__ == "__main__":
    interface = GameInterface()
    interface.add_players(ai=True)
    interface.start_match()

    