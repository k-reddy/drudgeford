from enum import Enum, auto


class Direction(Enum):
    NORTH = auto()
    WEST = auto()
    EAST = auto()
    SOUTH = auto()


class AnimationFrame(Enum):
    NORTH = auto()
    WEST = auto()
    EAST = auto()
    SOUTH = auto()
    IDLE_1 = auto()
    IDLE_2 = auto()
