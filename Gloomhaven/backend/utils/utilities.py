from functools import partial
from enum import Enum, auto
from pathlib import Path
from backend.utils.config import SAVE_FILE_DIR


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


def get_campaign_filenames():
    return [
        p.name
        for p in list(Path(SAVE_FILE_DIR).glob("*.pickle"))
        if "campaign_" in p.name
    ]


class DieAndEndTurn(Exception):
    pass


directions = [
    (1, 0),  # Down
    (0, 1),  # Right
    (-1, 0),  # Up
    (0, -1),  # Left
    (-1, 1),  # NE
    (1, 1),  # SE
    (1, -1),  # SW
    (-1, -1),  # NW
]
