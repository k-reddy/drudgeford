from enum import Enum, IntEnum, auto


class AnimationFrame(Enum):
    NORTH = auto()
    WEST = auto()
    EAST = auto()
    SOUTH = auto()
    IDLE_1 = auto()
    IDLE_2 = auto()


class Direction(Enum):
    NORTH = auto()
    WEST = auto()
    EAST = auto()
    SOUTH = auto()


class RotationDirection(IntEnum):
    COUNTER_CLOCK_WISE = 1
    CLOCK_WISE = -1
