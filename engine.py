from typing import List, Tuple, Optional
import math
from board import Board
from pieces import Piece
from supports import EvaluateSet, Vector, Color
import random

class Engine:
    def __init__(self, eval_set:EvaluateSet, depth: int = 3, debug: bool = False):
        self.debug = debug
        self.depth = depth
        self.eval_set = eval_set

    def get_best_move(self, board: Board, current_player: Color) -> Optional[Tuple[Vector, Vector]]:
        best_moves = []
        alpha = -math.inf
        beta = math.inf
        
        pieces = board.get_reds() if current_player == Color.RED else board.get_blacks()
        for piece in pieces:
            from_pos = piece.get_position()
            valid_moves = board.get_piece_valid_moves(piece, check=True)
            for to_pos in valid_moves:
                if self.debug:
                    print(f"ENGINE: evaluating {piece} to {to_pos}")
                move_value = self.minimax(
                        board=board,
                        from_pos=from_pos,
                        to_pos=to_pos,
                        depth=self.depth,
                        alpha=alpha,
                        beta=beta,
                        maximizing_player=(current_player == Color.RED))
                if self.debug:
                    print(f"ENGINE EVALUATION: {current_player.opposite()} can get {move_value}")
                if current_player == Color.RED and move_value > alpha:
                    ratio = (move_value / alpha) if alpha else 2
                    if 1.05 > ratio > 1:
                        best_moves.append((from_pos, to_pos))
                    else:
                        best_moves = [(from_pos, to_pos)]
                    alpha = move_value
                elif current_player == Color.BLACK and beta > move_value:
                    ratio = (beta / move_value) if move_value else 2
                    if 1.05 > ratio > 1:
                        best_moves.append((from_pos, to_pos))
                    else:
                        best_moves = [(from_pos, to_pos)]
                    beta = move_value
        
        return self.handle_gameover(board, current_player) if best_moves == [] else random.choice(best_moves)

    def handle_gameover(self, board: Board, color: Color):
        board.debug = True
        team = board.get_reds() if color == Color.RED else board.get_blacks()
        for piece in team:
            vds = board.get_piece_valid_moves(piece, check=True)
            print(f"ENGINE GAMEOVER: {piece} valid moves = {vds}")
        return None

    def minimax(self, 
               board: Board,
               from_pos: Vector,
               to_pos: Vector,
               depth: int,
               alpha: float,
               beta: float,
               maximizing_player: bool) -> float:
        return board.ghost_test(from_pos, to_pos, 
                                lambda x: self.minimax_wrapper(x, depth-1, not maximizing_player, alpha, beta))

    def minimax_wrapper(self,
                       board: Board,
                       depth: int,
                       maximizing_player: bool,
                       alpha: float,
                       beta: float) -> float:
        
        if depth == 1:
            evaluate = board.evaluate(self.eval_set)
            # if self.debug:
                # print(f"ENGINE WRAPPER: Evaluation = {evaluate}")
                # board.print_visual()
            return evaluate

        extreme_value = -math.inf if maximizing_player else math.inf
        pieces = board.get_reds() if maximizing_player else board.get_blacks()

        for piece in pieces:
            valid_moves = board.get_piece_valid_moves(piece, check=True)
            for move in valid_moves:
                current_value = self.minimax(
                    board=board,
                    from_pos=piece.get_position(),
                    to_pos=move,
                    depth=depth,
                    alpha=alpha,
                    beta=beta,
                    maximizing_player=maximizing_player)

                if maximizing_player:
                    extreme_value = max(extreme_value, current_value)
                    alpha = max(alpha, extreme_value)
                else:
                    extreme_value = min(extreme_value, current_value)
                    beta = min(beta, extreme_value)

                if beta <= alpha:
                    break

            if beta <= alpha:
                break

        return extreme_value