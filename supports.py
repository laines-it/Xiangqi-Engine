class Vector:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def __add__(self, other: 'Vector') -> 'Vector':
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: int) -> 'Vector':
        return Vector(self.x * scalar, self.y * scalar)

    def __floordiv__(self, scalar: int) -> 'Vector':
        return Vector(int(self.x / scalar), int(self.y / scalar))

    def __eq__(self, other: 'Vector') -> bool:
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f"({self.x}, {self.y})"
    
    def in_area(self, area):

        if not isinstance(area, tuple) or len(area) != 2:
            raise ValueError("Area must be a tuple of two Vector instances")

        bottom_left, top_right = area
        return (bottom_left.x <= self.x <= top_right.x) and (bottom_left.y <= self.y <= top_right.y)

FULLBOARD_AREA = (Vector(0,0),Vector(8,9))
RED_PALACE_AREA = (Vector(3,0),Vector(5,2))
BLACK_PALACE_AREA = (Vector(3,7),Vector(5,9))
BLACK_HALF = (Vector(0,5),Vector(8,9))
RED_HALF = (Vector(0,0),Vector(8,4))


from typing import List

class Move:
    def __init__(self, directions: List[Vector], bigstep: bool = False):
        """
        Represents the movement capabilities of a piece.
        :param directions: List of Vector objects representing possible directions.
        :param bigstep: Bool value representing if piece can jump over another.
        """
        self.directions = directions
        self.bigstep = bigstep
    
    def is_bigstep(self):
        return self.bigstep

    def get_directions(self):
        return self.directions
    
    def __add__(self, vector: Vector):
        if not isinstance(vector, Vector):
            raise TypeError("Can only add Vector objects to Move directions.")
        self.directions.append(vector)
        return self

class EvaluateSet:
    
    def __init__(self, value_multiplier=10, attack_bonus=1, mobility_multiplier=1, control_multiplier=1):
        self.value_multiplier = value_multiplier
        self.attack_bonus = attack_bonus
        self.mobility_multiplier = mobility_multiplier
        self.control_multiplier = control_multiplier
    
    def get(self):
        return (self.value_multiplier, self.attack_bonus, self.mobility_multiplier, self.control_multiplier)

from enum import Enum

class Square_status(Enum):
    red = 1
    neutral = 0
    black = -1

class Color(Enum):
    RED = 'RED'
    BLACK = 'BLACK'

    def opposite(self):
        return Color.RED if self == Color.BLACK else Color.BLACK

class textcolors:
    black = '\033[30m'
    red = '\033[31m'
    green = '\033[32m'
    orange = '\033[33m'
    blue = '\033[34m'
    purple = '\033[35m'
    cyan = '\033[36m'
    lightgrey = '\033[37m'
    darkgrey = '\033[90m'
    lightred = '\033[91m'
    lightgreen = '\033[92m'
    yellow = '\033[93m'
    lightblue = '\033[94m'
    pink = '\033[95m'
    lightcyan = '\033[96m'
    endc = '\033[0m'