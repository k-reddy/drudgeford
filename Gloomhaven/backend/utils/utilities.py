from functools import partial
from enum import Enum, auto

def make_multiply_modifier(multiplier: int, multiplier_text: str) -> tuple:
    def multiply(x, y):
        return x * y
    return (partial(multiply, multiplier), multiplier_text)

def make_additive_modifier(modifier_num) -> tuple:
    def add(x, y):
        return x + y
    return (partial(add, modifier_num), f"{modifier_num:+d}")

class GameState(Enum):
    START = auto()
    RUNNING = auto()
    WIN = auto()
    GAME_OVER = auto()
    EXHAUSTED = auto()