from typing import List, Tuple, Optional
import math
from board import Board
from pieces import Piece, General
from supports import EvaluateSet, Vector, Color
import random

class Engine:
    def __init__(self, eval_set:EvaluateSet, depth: int = 3, debug: bool = False):
        self.debug = debug
        self.depth = depth
        self.eval_set = eval_set

    def get_best_move(self, board: Board, current_player: Color, is_random:bool = False) -> Optional[Tuple[Vector, Vector]]:
        alpha = -math.inf
        beta = math.inf
        if is_random:
            best_moves = []
        pieces = board.get_reds() if current_player == Color.RED else board.get_blacks()
        moves = []
        for piece in pieces:
            from_pos = piece.get_position()
            valid_moves = board.get_piece_valid_moves(piece, check=True)
            
            for to_pos in valid_moves:
                target_square = board.get_square(to_pos)
                is_capture = target_square.get_piece() is not None
                
                quick_eval = board.ghost_test(from_pos, to_pos, 
                                            lambda b: b.evaluate(self.eval_set))
                eval_bonus = 0
                if is_capture:
                    captured_piece = target_square.get_piece()
                    eval_bonus += captured_piece.get_value() * 0.5
                
                if isinstance(piece, General):
                    eval_bonus += 0.3
                
                moves.append((quick_eval + eval_bonus, from_pos, to_pos))
        moves.sort(reverse=(current_player == Color.RED), key=lambda x: x[0])

        if len(moves):
            best_move = (moves[0][1], moves[0][2])
        else:
            best_move = None

        for move in moves:
            bonus, from_pos, to_pos = move

            if self.debug:
                print()
                print("=============================================================================================================================")
                print(f"ENGINE for {current_player.name} with {from_pos}->{to_pos}:")

            move_value = self.minimax(
                    board=board,
                    from_pos=from_pos,
                    to_pos=to_pos,
                    depth=self.depth,
                    alpha=alpha,
                    beta=beta,
                    maximizing_player=(current_player == Color.RED))

            if self.debug:
                print(f"ENGINE EVALUATION for {current_player.name} after {from_pos}->{to_pos}: {current_player.opposite().name} can get {move_value}")
                print("=============================================================================================================================")
                print()

            if current_player == Color.RED and move_value > alpha:
                if is_random and ((move_value / alpha) if alpha else 2) < 1.05:
                    best_moves.append((from_pos, to_pos))
                else:
                    best_move = (from_pos, to_pos)
                alpha = move_value
                
            elif current_player == Color.BLACK and beta > move_value:
                if is_random and ((beta / move_value) if move_value else 2) < 1.05:
                    best_moves.append((from_pos, to_pos))
                else:
                    best_move = (from_pos, to_pos)
                beta = move_value
                
                if abs(move_value) == math.inf:
                    print("FOUND CHECKMATE")
                    break
    
        move_value = alpha if current_player==Color.RED else beta
        if is_random:
            result = (move_value,
                    self.handle_gameover(board, current_player) if best_moves==[] else random.choice(best_moves))
        else:
            result = (move_value,
                    best_move if best_move else self.handle_gameover(board, current_player))

        return result

    def handle_gameover(self, board: Board, color: Color):
        board.debug = True
        team = board.get_reds() if color == Color.RED else board.get_blacks()
        for piece in team:
            vds = board.get_piece_valid_moves(piece, check=True)
            print(f"ENGINE GAMEOVER: {piece} valid moves = {vds}")
        board.debug = self.debug
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
        
        if self.debug:
            debcolor = Color.RED if maximizing_player else Color.BLACK

        if depth == 1:
            evaluate = board.evaluate(self.eval_set)
            if self.debug:
                print(f"ENGINE WRAPPER: Evaluation = {evaluate}")
                # board.print_visual()
            return evaluate
        
        extreme_value = -math.inf if maximizing_player else math.inf
        pieces = board.get_reds() if maximizing_player else board.get_blacks()

        for piece in pieces:
            valid_moves = board.get_piece_valid_moves(piece, check=False)
            for move in valid_moves:
                if self.debug:
                    print("--------------------------------------" * depth)
                    print(f"MINIMAX {debcolor} with {piece.get_position()}->{move}")
                    print(f"            depth={depth}, alpha={alpha}, beta={beta}")
                current_value = self.minimax(
                    board=board,
                    from_pos=piece.get_position(),
                    to_pos=move,
                    depth=depth,
                    alpha=alpha,
                    beta=beta,
                    maximizing_player=maximizing_player)
                
                if self.debug:
                    print(f"MINIMAX EVALUATION for {debcolor} after {piece.get_position()}->{move}: {debcolor.opposite().name} can get {current_value}")
                    print("--------------------------------------" * depth)

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