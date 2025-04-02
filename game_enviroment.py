import pieces
import pickle
from board import Board
from typing import List, Optional, Callable
from supports import Vector, Color, textcolors, EvaluateSet
from pieces import Chariot, Horse, Elephant, Advisor, General, Cannon, Soldier
from engine import Engine

class Game:
    def __init__(self, load=False, debug=False):
        self.debug = debug
        self.board = Board(debug=debug)
        self.selected_piece: Optional['Piece'] = None
        self.logs = open("game_log.txt", "w")
        self.eval_set = EvaluateSet(1,0,0,0)
        self.engine = Engine(self.eval_set, depth=5, debug=debug)        
        if load:
            self.load_board()
            self.load_current_color()
        else:
            self.initialize_pieces()
            self.current_player_color = Color.RED

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
        return self.board

    def create_queue(self):
        if self.selected_piece == Color.RED:
            return self.board.get_reds()
        else:
            return self.board.get_blacks()

    def select_piece(self, position: Vector):
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

    def make_move(self, new_position: Vector, check=True):
        if self.selected_piece is None:
            print(f"GAME trying to move to {new_position}: Please select a piece")
            return False
        valid_moves = self.board.get_piece_valid_moves(self.selected_piece, check=check)
        if self.debug:
            print(f"Valid moves: {valid_moves}")
        if new_position in valid_moves:
            self.board.move_piece(self.selected_piece.get_position(), new_position)
            print(f"GAME: moving {self.selected_piece}")
            self.logs.write(f"MOVE: {self.current_player_color.name} {self.selected_piece.get_name()} to {self.selected_piece.get_position()}\n")
            self.current_player_color = Color.BLACK if self.current_player_color == Color.RED else Color.RED
            self.selected_piece = None
            return True
        else:
            print(f"Move {self.selected_piece} to {new_position} is invalid")
            return False

    def is_mated(self):
        return self.board.is_mated()

    def evaluate(self):
        return self.board.update_evaluation(self.eval_set, describe=False)

    def engine_best_move(self):
        return self.engine.get_best_move(self.board, self.current_player_color)

    def print_pieces(self):
        self.board.print_pieces()

    #prints the board in console
    def print(self):
        print(f"Evaluation: {self.evaluate():.2f}")
        print(f"{self.current_player_color} to move")
        #self.board.print_control()
        return self.board.print_visual()

    def save_board(self):
        with open('board.pkl', 'wb') as f:
            pack = self.board.get_reds() + self.board.get_blacks()
            pickle.dump(pack, f)
        with open('color2move.pkl', 'wb') as f:
            pickle.dump(self.current_player_color, f)
        self.logs.close()
        print("Board saved successfully")

    def load_board(self):
        try:
            with open('board.pkl', 'rb') as f:
                pack = pickle.load(f)
                for piece in pack:
                    self.board.add_piece(piece)
                print("Board loaded successfully")
                return True
        except FileNotFoundError:
            print("No saved board found")
            self.initialize_pieces()
            return False
    def load_current_color(self):
        try:
            with open('color2move.pkl', 'rb') as f:
                self.current_player_color = pickle.load(f)
                print("Current color loaded successfully")
                return True
        except FileNotFoundError:
            print("No saved color found")
            self.current_player_color = Color.RED
            return False

    def openning_general_sight(self):
        self.select_piece(Vector(4,3))
        self.make_move(Vector(4,4))
        self.select_piece(Vector(4,6))
        self.make_move(Vector(4,5))
        self.select_piece(Vector(4,4))
        self.make_move(Vector(4,5))
        self.select_piece(Vector(4,9))
        self.make_move(Vector(4,8))
        self.select_piece(Vector(4,5))
        self.make_move(Vector(5,5))
        self.select_piece(Vector(5,0))
        self.make_move(Vector(4,1))
        self.select_piece(Vector(4,8))
        self.make_move(Vector(5,8))
        self.select_piece(Vector(4,0))
        self.make_move(Vector(5,0))

g = Game(load=False, debug=False)
g.print()
i = 0
while True:
    #input()
    print("MOVE", i // 2)
    best_move = g.engine_best_move()
    if best_move is None:
        print(f"PLAYER {g.current_player_color.opposite()} WON")
        g.save_board()
        break
    from_pos, to_pos = best_move
    g.select_piece(from_pos)
    g.make_move(to_pos)
    g.print()
    i += 1
