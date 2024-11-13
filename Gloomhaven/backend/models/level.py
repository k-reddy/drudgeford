from dataclasses import dataclass
from backend.models import character
import textwrap
from backend.utils.config import TEXT_WIDTH

GAME_PLOT = textwrap.fill('''Welcome to Drudgeford, your home since childhood. Recently, strange events have been plaguing your village. Crops wither overnight, shadows move against the sun, and ancient runes appear carved into doors. All in the town swear innocence but darkness spreads. You journey to nearby villages in search of information and hear rumors of a puppet master working from the shadows. You decide to seek out this mysterious force before your village succumbs to its influence.''',
                          width=TEXT_WIDTH)

@dataclass
class Level:
    floor_color_map: list[tuple[int,int]]
    wall_color_map: list[tuple[int,int]]
    monster_classes: list[character.Character]
    pre_level_text: str

campaign_levels=[
    Level(
        floor_color_map=[(1,3), (5,11)],
        wall_color_map=[(1,4), (13,15)],
        monster_classes=[character.Treeman, character.MushroomMan, character.Fairy],
        pre_level_text=textwrap.fill('''A hunter you talked to at the tavern mentioned seeing the same mysterious rune that's been appearing on village doors carved into the bark of an ancient tree in a forest nearby. When the village healer mentioned that the mushrooms from that part of the forest had suddenly lost their curative effects, you decide to investigate the area. The rune on the tree points to a trail of withered vegetation. You follow it deep into the forest - only to find yourself surrounded by forest creatures whose vacant eyes and jerky movements suggest they're under some dark influence. Before you can retreat, they lunge at you in perfect, unsettling union.''',
        TEXT_WIDTH)),
    Level(
        floor_color_map=[(1,8), (5,2)],
        wall_color_map=[],# (1,2), (13,14)
        monster_classes=[character.Demon, character.Fiend, character.FireSprite],
        pre_level_text=textwrap.fill('''As you kill the last of the corrupted creatures, a dark figure in a hooded robe materializes at the forest's edge. Before you can focus on it, the shape dissolves into shadow. Your head erupts into searing pain, as a raspy voice booms in your mind. 'I have you in my grasp now,' it cackles. 'Good luck ever escaping me.' The world spins, then fades to black as you collapse. You wake up burning hot, and your eyes open to the sight of demons and fire - you'll need to fight through them to survive.''',
        TEXT_WIDTH)
        ),
]