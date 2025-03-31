import pieces
from board import Board
from typing import List, Optional, Callable 
from supports import Vector, Color, textcolors, EvaluateSet
from pieces import Chariot, Horse, Elephant, Advisor, General, Cannon, Soldier
from engine import Engine

class Game:
    def __init__(self, debug=False):
        self.debug = debug
        self.board = Board(debug=False)
        self.engine = Engine(depth=5, debug=debug)
        self.current_player_color = Color.RED
        self.selected_piece: Optional['Piece'] = None
        self.initialize_pieces()

    def initialize_pieces(self):
        for i,color in enumerate(Color):
            self.board.add_piece(General(color, Vector(4,9*i)))
            for x,piece_class in enumerate([Chariot, Horse, Elephant, Advisor]):
                self.board.add_piece(piece_class(color, Vector(x,9*i)))
                self.board.add_piece(piece_class(color, Vector(8-x, 9*i)))
            for x in range(5):
                self.board.add_piece(Soldier(color, Vector(x*2, 3 + 3*i)))
            self.board.add_piece(Cannon(color, Vector(1, 2 + 5*i)))
            self.board.add_piece(Cannon(color, Vector(7, 2 + 5*i)))
        if self.debug:
            print("GAME: Board initialized successfully")
            print(self.board.print_visual())
        return self.board

    def create_queue(self):
        if self.selected_piece == Color.RED:
            return self.board.get_reds()
        else:
            return self.board.get_blacks()

    def select_piece(self, position):
        if self.debug and self.selected_piece is not None:
            print(f"GAME trying to select on {position}: piece already selected>> {self.selected_piece}")
            return False
        piece = self.board.get_square(position).get_piece()
        if piece and piece.get_color() == self.current_player_color:
            self.selected_piece = piece
            if self.debug:
                print(f"GAME: Selected {piece}")
            return True
        else:
            print(f"GAME trying to select on {position}: No piece or incorrect color")
        return False

    def make_move(self, new_position: Vector, check=False):
        if self.selected_piece is None:
            print(f"GAME trying to move to {new_position}: Please select a piece")
            return False
        valid_moves = self.board.get_piece_valid_moves(self.selected_piece, check=check)
        if self.debug:
            print(f"Valid moves: {valid_moves}")
        if new_position in valid_moves:
            self.board.move_piece(self.selected_piece.get_position(), new_position)
            if self.debug:
                print(f"Game moving {self.selected_piece}")
            self.current_player_color = Color.BLACK if self.current_player_color == Color.RED else Color.RED
            self.selected_piece = None
            return True
        else:
            print(f"Move {self.selected_piece} to {new_position} is invalid")
            return False

    def evaluate(self):
        return self.board.evaluate(EvaluateSet(10,0.1,0.01,0.1),describe=True)

    def engine_best_move(self):
        return self.engine.get_best_move(self.board, self.current_player_color)

    def print_pieces(self):
        self.board.print_pieces()

    #prints the board in console
    def print(self):
        return self.board.print_visual()

g = Game(debug=False)
g.print()

from_pos, to_pos = g.engine_best_move()
print(f"Best move for {g.current_player_color}: {from_pos} -> {to_pos}")
