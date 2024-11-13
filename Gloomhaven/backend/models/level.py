from dataclasses import dataclass
from .character import Character

@dataclass
class Level:
    floor_color_map: list[tuple[int,int]]
    wall_color_map: list[tuple[int,int]]
    monster_classes: list[Character]
    pre_level_text: str