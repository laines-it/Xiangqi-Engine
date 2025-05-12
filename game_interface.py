from game_enviroment import Game
from players import Player, Human, Bot
from engine import Engine
from typing import Optional
from supports import Color, EvaluateSet, GameResult

class GameInterface:
    def __init__(self):
        self.default_eval_set = EvaluateSet(control_multiplier=0, mobility_multiplier=0)
        self.game = Game(eval_set=self.default_eval_set, load=False)
        self.default_engine = Engine(self.default_eval_set, depth=1)  # For deep analysis
        self.red_player : Optional['Player'] = None
        self.black_player : Optional['Player'] = None

    def get_all_of_game(self):
        return self.game.get_all()

    def start_game(self) -> GameResult:
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
                return GameResult.tie
            i += 1

        self.game.save_board()
        return GameResult.red_won if self._determine_winner() == Color.RED else GameResult.black_won

    def start_match(self, best_of: int = 1):
        red_wins = 0
        black_wins = 0
        ties = 0
        while max(red_wins, black_wins) < best_of:
            self.game = Game(eval_set=self.default_eval_set, load=False)
            result = self.start_game()
            if result == GameResult.red_won:
                red_wins += 1
            elif result == GameResult.black_won:
                black_wins += 1
            else:
                ties += 1
        winner = Color.RED if red_wins > black_wins else Color.BLACK
        return winner, red_wins, black_wins, ties

    def _determine_winner(self) -> Color:
        return self.game.current_player_color.opposite()

    def add_players(self, ai=False):
        human1 = Human(name="Alice", color=Color.RED, profile_url="https://example.com/alice")
        human2 = Human(name="PALICE", color=Color.BLACK, profile_url="https://example.com/alice")
    
        bot_engine1 = Engine(EvaluateSet(value_multiplier=100, attack_bonus=0, mobility_multiplier=0, control_multiplier=0), depth=5)
        ai1 = Bot(
            engine=bot_engine1,
            color=Color.RED,
            name="Aggressive AI",
            strategy_description="Prefers attacking moves"
        )

        bot_engine2 = Engine(EvaluateSet(value_multiplier=100, attack_bonus=0, mobility_multiplier=0, control_multiplier=0), depth=5)
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
    # print(interface.start_match(best_of=))
    interface.start_game()