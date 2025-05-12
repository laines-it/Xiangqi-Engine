from pieces import Piece, General, Soldier
from typing import List, Optional, Callable, Tuple
from supports import Vector, Color, textcolors, FULLBOARD_AREA, RED_PALACE_AREA, BLACK_PALACE_AREA, EvaluateSet, Square_status
from math import inf

class Square:
    def __init__(self, position: Vector):
        self.position = position
        self.piece: Optional['Piece'] = None
        self.state = Square_status.neutral
        self.red_attacks: int = 0
        self.black_attacks: int = 0

    def reset_attacks(self):
        self.red_attacks = 0
        self.black_attacks = 0
        self.state = Square_status.neutral

    def add_attack(self, color: Color):
        if color == Color.RED:
            self.red_attacks += 1
        else:
            self.black_attacks += 1
        self.update_state()
    
    def remove_attack(self, color: Color):
        if color == Color.RED:
            self.red_attacks -= 1
        else:
            self.black_attacks -= 1
        self.update_state()

    def update_state(self):
        if self.red_attacks > self.black_attacks:
            self.state = Square_status.red
        elif self.black_attacks > self.red_attacks:
            self.state = Square_status.black
        else:
            self.state = Square_status.neutral

    def get_state(self):
        return self.state

    def get_piece(self):
        return self.piece

    def remove_piece(self):
        self.piece = None

    def set_piece(self, piece: Piece):
        old_piece = self.piece
        self.piece = piece
        piece.set_position(self.position)
        return old_piece

class Board:
    def __init__(self, debug=False):
        self.squares = [[Square(Vector(x, y)) for y in range(10)] for x in range(9)]
        self.evaluation = 0
        self.history = []
        self.uncapturing_moves_count = 0
        self.save_UMC = self.uncapturing_moves_count
        self.reds = []
        self.blacks = []
        self.debug = debug

    def add_piece(self, piece: Piece):
        position = piece.get_position()
        square = self.get_square(position)
        if square and square.get_piece():
            raise ValueError(f"Square {position} is already occupied by {square.piece}")
        else:
            square.set_piece(piece)
        if piece.color == Color.RED:
            self.reds.append(piece)
        else:
            self.blacks.append(piece)

    def history_by_index(self, index):
        return self.history[-index]

    def remove_piece(self, piece: Optional['Piece']):
        if piece.color == Color.RED:
            self.reds.remove(piece)
        else:
            self.blacks.remove(piece)

    def get_square(self, position: Vector, area:Optional[tuple]=None):
        """
        params: area: part of the board to check if square is in this area
                None means area checking is not needed 
        """
        if area and not(position.in_area(area)):
            return None
        return self.squares[position.x][position.y]

    def get_uncapturing_moves_count(self):
        return self.uncapturing_moves_count

    # returns the square of piece, giving check
    # if is not in check, returns None
    def is_in_check(self, color: Color):
        #General sight
        gen_red = None
        gen_black = None
        for piece in self.reds:
            if isinstance(piece, General):
                gen_red = piece
        for piece in self.blacks:
            if isinstance(piece, General):
                gen_black = piece
        if gen_black and gen_red:
            x = gen_red.get_position().getX()
            if (x == gen_black.get_position().getX()) and self.empty_between_general(x, gen_red.get_position().getY(), gen_black.get_position().getY()):
                return (gen_red, Vector(x,10)) if color == Color.BLACK else (gen_black, Vector(x,10))

        #Move repeatition
        # 3-time repetition causes mate
        if len(self.history) > 5:
            repeated3 = True
            for i in range(1,4):
                if self.history[-i] != self.history[-i-4]:
                    repeated3 = False
                    break
            if repeated3:
                print("REPEATED")
                return (self.get_square(self.history[-1][1]).get_piece(), self.history[-1])

        #Checks
        opponent_pieces = self.reds if color == Color.BLACK else self.blacks
        palace = RED_PALACE_AREA if color == Color.RED else BLACK_PALACE_AREA
        attackers = [attacker for attacker in opponent_pieces if attacker.is_attacker()]
        for attacker in attackers:
            attackers_valid_moves = self.get_piece_valid_moves(attacker, check=False)
            for move in attackers_valid_moves:
                square = self.get_square(move, area=palace)
                if square and square.piece and isinstance(square.piece, General):
                    return (attacker, move)
        
        return (None,None)

    def empty_between_general(self, x, y1, y2):
        for j in range(y1+1, y2):
            if self.squares[x][j].get_piece():
                return False
        return True

    def get_attackers(self, color: Color) -> List[Piece]:
        return [piece for piece in (self.reds if color == Color.RED else self.blacks) if piece.is_attacker()]
    
    def move_piece(self, from_pos: Vector, to_pos: Vector, set_instead : Optional['Piece'] = None, returning = False):
        old_square = self.squares[from_pos.getX()][from_pos.getY()]
        the_piece = old_square.get_piece()
        if the_piece is None:
            raise ValueError("There is no piece on " + from_pos)
        the_piece.set_position(to_pos)
        taken = self.squares[to_pos.getX()][to_pos.getY()].set_piece(the_piece)
        if taken is not None:
            #capturing
            self.remove_piece(taken)
            self.save_UMC = self.uncapturing_moves_count
            self.uncapturing_moves_count = 0
        else:
            self.uncapturing_moves_count += 1

        old_square.remove_piece()

        if returning:
            self.history.pop()
            self.uncapturing_moves_count -= 2
        else:
            self.history.append([from_pos, to_pos])

        if set_instead is not None:
            #set captured => cancel capturing
            self.add_piece(set_instead)
            self.uncapturing_moves_count = self.save_UMC

        return taken

    def ghost_test(self, from_pos:Vector, to_pos:Vector, func: Callable):
        taken = self.move_piece(from_pos, to_pos)
        result = func(self)
        self.move_piece(to_pos, from_pos, set_instead=taken, returning=True)
        return result

    def get_piece_valid_moves(self, piece: Piece, check=True, for_eval=False):
        valid_moves = []

        if piece.can_modify() and (not piece.is_modified()):
            if (piece.position.getY() > 4 if (piece.get_color() == Color.RED) else piece.get_position().getY() < 5):
                piece.modify()
        
        move = piece.get_move()

        for direction in move.get_directions():
            
            if move.is_bigstep() and self.has_piece(piece.get_position() + direction // 2):
                continue

            has_screen = False
            position = piece.get_position()
            for step in range(piece.get_max_steps()):
                position += direction
                target_square = self.get_square(position, area=piece.get_area())
                if target_square is None:
                    break
                if target_square.get_piece():
                    if (not piece.need_screen()) or has_screen:
                        if for_eval or target_square.get_piece().get_color() != piece.get_color():
                            if check:
                                threat, killer_move = self.ghost_test(piece.get_position(), position,
                                                                      lambda xxx: xxx.is_in_check(piece.get_color()))
                                if threat is not None:
                                    if self.debug:
                                        print(f"Move by {piece} to {position} causes mate by {threat} with {killer_move}")
                                    break     
                            valid_moves.append(position)
                        break
                    else:
                        has_screen = True
                elif (has_screen == piece.need_screen()) if for_eval else (not has_screen):
                    if check:
                        threat, killer_move = self.ghost_test(piece.get_position(), position,
                                                              lambda xxx: xxx.is_in_check(piece.get_color()))
                        if threat is None:
                            valid_moves.append(position)
                        elif self.debug:
                            print(f"BOT Move by {piece} to {position} causes mate by {threat} with {killer_move}")
                    else:
                        valid_moves.append(position)

        if piece.can_modify() and piece.is_modified():
            piece.set_default()

        return valid_moves


    def has_piece(self, position: Vector) -> bool:
        sq = self.get_square(position, area=FULLBOARD_AREA)
        return bool(sq) and bool(sq.get_piece())

    def is_mate(self):
        mate = 3
        for i,team in enumerate((self.reds, self.blacks)):
            for piece in team:
                if isinstance(piece, General):
                    mate -= i+1
                    break
        if mate == 0:
            return 0
        elif mate == 1:
            return -inf
        else:
            return inf


    def evaluate(self, eval_set: EvaluateSet, describe=False):
        if self.uncapturing_moves_count > 49:
            return 0
        res = self.is_mate()
        if res:
            return res 
        total_value = 0
        self.reset_control_state()
        value_multiplier, attack_bonus, mobility_multiplier, control_multiplier = eval_set.get()
        for i,team in enumerate((self.reds, self.blacks)):
            team_values = team_attack_bonus = team_mobility = 0
            for piece in team:
                team_values += piece.get_value() * value_multiplier
                if attack_bonus:
                    team_attack_bonus += attack_bonus if piece.is_attacker() else 0
                if mobility_multiplier:
                    vds = self.get_piece_valid_moves(piece, check=True, for_eval=True)
                    team_mobility += len(vds)* mobility_multiplier
                if control_multiplier:
                    self.update_control_state(piece.get_color(), vds)
                if describe:
                    #print(f"BOARD Evaluating: for {piece} valid moves {vds}")
                    print(f"BOARD: {piece.get_color().name} values = {team_values}")
                    print(f"BOARD: {piece.get_color().name} attack bonus = {team_attack_bonus}")
                    print(f"BOARD: {piece.get_color().name} mobility = {team_mobility}")
            total_value += (team_values + team_attack_bonus + team_mobility) * ((-1) if i else 1)
        if control_multiplier:
            for rows in self.squares:
                for square in rows:
                    total_value += square.get_state().value * (control_multiplier if square.get_piece() is None else (control_multiplier+attack_bonus))
        return total_value

    def update_evaluation(self, eval_set: EvaluateSet, describe=False):
        self.evaluation = self.evaluate(eval_set, describe=describe)
        return self.evaluation

    def update_control_state(self, color:Color, attacks: List[Vector]):
        for attack in attacks:
            square = self.get_square(attack)
            square.add_attack(color)

    def reset_control_state(self):
        for row in self.squares:
            for square in row:
                square.reset_attacks()

    def get_reds(self):
        return self.reds

    def get_blacks(self):
        return self.blacks

    def print_pieces(self):
        print("RED PIECES:")
        for piece in self.reds:
            print(piece)
        print("BLACK PIECES:")
        for piece in self.blacks:
            print(piece)

    def print_visual(self, prespective: Color = Color.RED):
        line = " ╔"
        for i in range(9):
            line += "═══"
        line += "╗"
        print(line)
        
        for i in range(10):
            vert = i if prespective==Color.BLACK else (9-i)
            line = str(vert)
            line += "║"
            for j in range(9):
                print_piece = self.squares[j][vert].get_piece()
                if i in (4,9):
                    between = "┴"
                elif i in (5, 0):
                    between = "┬"
                elif j == 0:
                    between = "├"
                elif j == 8:
                    between = "┤"
                else:
                    between = "┼"
                if print_piece:
                    line += " "
                    line += textcolors.red if print_piece.get_color()==Color.RED else textcolors.green
                    line += print_piece.get_name() + textcolors.endc + " "
                else:
                    line += "─" if j > 0 else " "
                    line += between
                    line += "─" if j < 8 else " " 
            line += "║"
            print(line)
        line = " ╚"
        for i in range(9):
            line += "═══"
        line += "╝"
        print(line)
        line = "   "
        for i in range(9):
            line += str(i) + "  "
        print(line)
        print()
    
    def print_control(self, prespective: Color = Color.RED):
        for i in range(10):
            line = ""
            for j in range(9):
                vert = i if prespective==Color.BLACK else (9-i)
                state = self.squares[j][vert].get_state()
                color = textcolors.lightgrey
                if state==Square_status.red:
                    color = textcolors.red
                elif state==Square_status.black:
                    color = textcolors.green
                s = "██"
                if i == 5:
                    s = "▄▄"
                elif i == 4:
                    s = "▀▀"
                line += color
                line += s + textcolors.endc
            print(line)
        