import copy
from typing import List, Optional, Callable
from supports import *
#from supports import FULLBOARD_AREA, RED_PALACE_AREA, RED_HALF, BLACK_PALACE_AREA, Move, Color, Vector, textcolors

class Piece:
    def __init__(self, color: Color, position: Vector, move: Move,
                 name: str, attacking: bool, value: float):
        self.color = color
        self.position = position
        self.move = move
        self.name = name    
        self.attacking = attacking
        self.value = value

    def get_area(self):
        return FULLBOARD_AREA
    def need_screen(self):
        return False
    def can_modify(self):
        return False
    def is_modified(self):
        pass
    def modify(self):
        pass
    def set_default(self):
        pass
    def get_max_steps(self):
        pass

    def is_attacker(self):
        return self.attacking

    def set_value(self, value:int):
        self.value = value

    def get_value(self):
        return self.value

    def get_position(self):
        return self.position

    def set_position(self, new_position: Vector):
        self.position = new_position
    
    def get_color(self):
        return self.color

    def get_move(self):
        return self.move

    def get_name(self):
        return self.name

    def __repr__(self):
        return f"Piece {textcolors.red if self.color==Color.RED else textcolors.green}{self.name}{textcolors.endc} on position {self.position}"

class General(Piece):
    def __init__(self, color: Color, position: Vector):
        move = Move([Vector(1, 0), Vector(-1, 0), Vector(0, 1), Vector(0, -1)])
        super().__init__(color, position, move, 'G', attacking=False, value=200)

    def get_area(self):
        return RED_PALACE_AREA if self.color==Color.RED else BLACK_PALACE_AREA
    
    def get_max_steps(self):
        return 1

class Advisor(Piece):
    def __init__(self, color: Color, position: Vector):
        move = Move([Vector(1, 1), Vector(1, -1), Vector(-1, 1), Vector(-1, -1)])
        super().__init__(color, position, move, 'A', attacking=False, value=2)
    
    def get_max_steps(self):
        return 1

    def get_area(self):
        return RED_PALACE_AREA if self.color==Color.RED else BLACK_PALACE_AREA

class Chariot(Piece):
    def __init__(self, color: Color, position: Vector):
        move = Move([Vector(1, 0), Vector(-1, 0), Vector(0, 1), Vector(0, -1)])
        super().__init__(color, position, move, 'R', attacking=True, value=9)
    
    def get_max_steps(self):
        return 10

class Horse(Piece):
    def __init__(self, color: Color, position: Vector):
        move = Move([Vector(2, 1), Vector(2, -1), Vector(-2, 1), Vector(-2, -1), Vector(1, 2),
                     Vector(1, -2), Vector(-1, 2), Vector(-1, -2)], bigstep=True)
        super().__init__(color, position, move, 'H', attacking=True, value=3.5)
    
    def get_max_steps(self):
        return 1

class Elephant(Piece):
    def __init__(self, color: Color, position: Vector):
        move = Move([Vector(2, 2), Vector(2, -2), Vector(-2, 2), Vector(-2, -2)], bigstep=True)
        super().__init__(color, position, move, 'E', attacking=False, value=2)
    
    def get_max_steps(self):
        return 1

    def get_area(self):
        return RED_HALF if self.color==Color.RED else BLACK_HALF

class Cannon(Piece):
    def __init__(self, color: Color, position: Vector):
        move = Move([Vector(1, 0), Vector(-1, 0), Vector(0, 1), Vector(0, -1)])
        super().__init__(color, position, move, 'C', attacking=True, value=3.5)
    
    def get_max_steps(self):
        return 10

    def need_screen(self):
        return True

class Soldier(Piece):
    def __init__(self, color: Color, position: Vector):
        move = Move([Vector(0, 1)] if color==Color.RED else [Vector(0, -1)])
        super().__init__(color, position, move, 'S', attacking=True, value=1)
        self.modified = False

    def get_max_steps(self):
        return 1

    def can_modify(self):
        return True

    def is_modified(self):
        return self.modified

    def modify(self):
        self.modified = True
        self.move += Vector(-1,0)
        self.move += Vector(1,0)
        self.value = 2

    def set_default(self):
        self.modified = False
        self.move = Move([Vector(0, 1)] if self.color==Color.RED else [Vector(0, -1)])
        self.value = 1