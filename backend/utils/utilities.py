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
        for p in list(Path(SAVE_FILE_DIR).glob("*.json"))
        if "campaign_" in p.name
    ]


def wrap_color_tags(text: str, color: int) -> str:
    """
    Wraps each line of text in color tags.

    Example:
        Input: "Line 1\nLine 2", 13
        Output: "<color:13>Line 1</color>\n<color:13>Line 2</color>"
    """
    lines = text.strip().split("\n")
    return "\n".join(f"<color:{color}>{line}</color>" for line in lines if line)


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

color_map = {
    "damage": 9,
    "heal": 11,
    "modifier_deck": 12,
    "attack": 9,
    "action_card": 13,
    "health": 14,
    "shield": 4,
    "killed": 8,
}
