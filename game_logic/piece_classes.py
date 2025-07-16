import Move from supports



class Piece:
    def __init__(self, color, position):
        self.color = color  # 'red' or 'black'
        if color == 'red':
            self.opposite_color = 'black'
        else:
            self.opposite_color = 'red'
        self.position = position  # (x, y) tuple
        self.value = 0

    def move(self, new_position):
        self.position = new_position

    def get_color(self):
        return self.color

    def is_valid_move(self, new_position, board):
        return new_position in self.valid_moves(board)

    def valid_moves(self, board):
        raise NotImplementedError("Subclasses must implement this method")

class General(Piece):
    def __init__(self, color, position):
        super().__init__(self, color, position)
        self.in_check = False

    def is_in_check(self):
        return self.in_check

    def valid_moves(self, palace):
        x, y = self.position
        moves = []
        # General can move one step orthogonally within the palace
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 10 and 0 <= new_y < 9:  # Check if within board
                if (self.color == 'red' and 0 <= new_x <= 2) or (self.color == 'black' and 7 <= new_x <= 9):  # Palace bounds
                    target_square = palace.squares[new_x][new_y]
                    if target_piece.get_attacks(opposite_color) == 0 and (target_square.is_clear() or target_square.get_piece().get_color() != self.color):
                        moves.append((new_x, new_y))
        return moves

class Advisor(Piece):
    def __init__(self, color, position):
        super().__init__(self, color, position)
        self.value = 2

    def valid_moves(self, board):
        x, y = self.position
        moves = []
        # Advisor moves one step diagonally within the palace
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 10 and 0 <= new_y < 9:  # Check if within board
                if (self.color == 'red' and 0 <= new_x <= 2) or (self.color == 'black' and 7 <= new_x <= 9):  # Palace bounds
                    target_piece = board.squares[new_x][new_y]
                    if not target_piece or target_piece.color != self.color:
                        moves.append((new_x, new_y))
        return moves

class Elephant(Piece):
    def __init__(self, color, position):
        super().__init__(self, color, position)
        self.value = 2

    def valid_moves(self, board):
        x, y = self.position
        moves = []
        # Elephant moves two steps diagonally, cannot jump over pieces
        for dx, dy in [(2, 2), (2, -2), (-2, 2), (-2, -2)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 10 and 0 <= new_y < 9:  # Check if within board
                # Check if the elephant crosses the river (only for red/black)
                if (self.color == 'red' and new_x <= 4) or (self.color == 'black' and new_x >= 5):
                    # Check if the intervening square is empty
                    mid_x, mid_y = x + dx // 2, y + dy // 2
                    if not board.squares[mid_x][mid_y]:
                        target_piece = board.squares[new_x][new_y]
                        if not target_piece or target_piece.color != self.color:
                            moves.append((new_x, new_y))
        return moves

class Horse(Piece):
    def __init__(self, color, position):
        super().__init__(self, color, position)
        self.value = 3.5

    def valid_moves(self, board):
        x, y = self.position
        moves = []
        # Horse moves one step orthogonally and then one step diagonally
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 10 and 0 <= new_y < 9:  # Check if within board
                if not board.squares[new_x][new_y]:  # No blocking piece
                    for ddx, ddy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
                        final_x, final_y = new_x + ddx, new_y + ddy
                        if 0 <= final_x < 10 and 0 <= final_y < 9:
                            target_piece = board.squares[final_x][final_y]
                            if not target_piece or target_piece.color != self.color:
                                moves.append((final_x, final_y))
        return moves

class Chariot(Piece):
    def __init__(self, color, position):
        super().__init__(self, color, position)
        self.value = 9

    def valid_moves(self, board):
        x, y = self.position
        moves = []
        # Chariot moves orthogonally any number of squares
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x, new_y = x + dx, y + dy
            while 0 <= new_x < 10 and 0 <= new_y < 9:
                target_piece = board.squares[new_x][new_y]
                if not target_piece:
                    moves.append((new_x, new_y))
                else:
                    if target_piece.color != self.color:
                        moves.append((new_x, new_y))
                    break
                new_x += dx
                new_y += dy
        return moves

class Cannon(Piece):
    def __init__(self, color, position):
        super().__init__(self, color, position)
        self.value = 3.5

    def valid_moves(self, board):
        x, y = self.position
        moves = []
        # Cannon moves orthogonally like a chariot but must jump over exactly one piece to capture
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x, new_y = x + dx, y + dy
            while 0 <= new_x < 10 and 0 <= new_y < 9:
                target_piece = board.squares[new_x][new_y]
                if not target_piece:
                    moves.append((new_x, new_y))
                else:
                    # Look for a piece to jump over
                    new_x += dx
                    new_y += dy
                    while 0 <= new_x < 10 and 0 <= new_y < 9:
                        target_piece = board.squares[new_x][new_y]
                        if target_piece:
                            if target_piece.color != self.color:
                                moves.append((new_x, new_y))
                            break
                        new_x += dx
                        new_y += dy
                    break
                new_x += dx
                new_y += dy
        return moves

class Soldier(Piece):
    def __init__(self, color, position):
        super().__init__(self, color, position)
        self.value = 1

    def valid_moves(self, board):
        x, y = self.position
        moves = []
        # Soldier moves forward one step, and sideways after crossing the river
        if self.color == 'red':
            if x + 1 < 10:
                target_piece = board.squares[x + 1][y]
                if not target_piece or target_piece.color != self.color:
                    moves.append((x + 1, y))
            if x >= 5:  # Crossed the river
                if y - 1 >= 0:
                    target_piece = board.squares[x][y - 1]
                    if not target_piece or target_piece.color != self.color:
                        moves.append((x, y - 1))
                if y + 1 < 9:
                    target_piece = board.squares[x][y + 1]
                    if not target_piece or target_piece.color != self.color:
                        moves.append((x, y + 1))
        else:  # Black soldier
            if x - 1 >= 0:
                target_piece = board.squares[x - 1][y]
                if not target_piece or target_piece.color != self.color:
                    moves.append((x - 1, y))
            if x <= 4:  # Crossed the river
                if y - 1 >= 0:
                    target_piece = board.squares[x][y - 1]
                    if not target_piece or target_piece.color != self.color:
                        moves.append((x, y - 1))
                if y + 1 < 9:
                    target_piece = board.squares[x][y + 1]
                    if not target_piece or target_piece.color != self.color:
                        moves.append((x, y + 1))
        return moves