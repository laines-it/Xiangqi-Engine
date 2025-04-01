from typing import List, Tuple, Optional
import math
from board import Board
from pieces import Piece
from supports import EvaluateSet, Vector, Color

class Engine:
    def __init__(self, depth: int = 3, debug: bool = False):
        self.debug = debug
        self.depth = depth
        self.eval_set = EvaluateSet(2, 0.1, 0.01, 0.1)

    def get_best_move(self, board: Board, current_player: Color) -> Optional[Tuple[Vector, Vector]]:
        best_move = None
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

                if current_player == Color.RED and move_value > alpha:
                    alpha = move_value
                    best_move = (from_pos, to_pos)
                elif current_player == Color.BLACK and move_value < beta:
                    beta = move_value
                    best_move = (from_pos, to_pos)
                if alpha >= beta:
                    break
        
        return best_move

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
            if self.debug:
                print(f"ENGINE WRAPPER: Evaluation = {evaluate}")
                board.print_visual()
            return evaluate

        extreme_value = -math.inf if maximizing_player else math.inf
        pieces = board.get_reds() if maximizing_player else board.get_blacks()

        for piece in pieces:
            valid_moves = board.get_piece_valid_moves(piece, check=True)
            for move in valid_moves:
                if self.debug:
                    print(f"ENGINE WRAPPER depth={depth}: evaluating {piece} to {move}")
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