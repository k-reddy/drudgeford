from dataclasses import dataclass
from backend.models import character
import textwrap
from backend.utils.config import TEXT_WIDTH
from backend.models import obstacle 

GAME_PLOT = textwrap.fill('''Welcome to Drudgeford, your rather unremarkable home since childhood. Recently, however, things have changed. Strange events have been plaguing your village. Crops wither overnight, shadows move against the sun, and ancient runes appear carved into doors. All in the town swear innocence but darkness spreads. You journey to nearby villages in search of information and hear rumors of a puppet master working from the shadows. You decide to seek out this mysterious force before your village succumbs to its influence.''',
                          width=TEXT_WIDTH)

@dataclass
class Level:
    floor_color_map: list[tuple[int,int]]
    wall_color_map: list[tuple[int,int]]
    monster_classes: list[character.Character]
    pre_level_text: str
    starting_elements: list[obstacle.TerrainObject]

campaign_levels=[
    # Level(
    #     floor_color_map=[(1,3), (5,11)],
    #     wall_color_map=[(1,4), (13,15)],
    #     monster_classes=[character.Treeman, character.MushroomMan, character.Fairy],
    #     pre_level_text=textwrap.fill('''A hunter you talked to at the tavern mentioned seeing the same mysterious rune that's been appearing on village doors carved into the bark of an ancient tree in a forest nearby. When the village healer mentioned that the mushrooms from that part of the forest had suddenly lost their curative effects, you decide to investigate the area. The rune on the tree points to a trail of withered vegetation. You follow it deep into the forest - only to find yourself surrounded by forest creatures whose vacant eyes and jerky movements suggest they're under some dark influence. Before you can retreat, they lunge at you in perfect, unsettling union.''',
    #     TEXT_WIDTH),
    #     starting_elements=[obstacle.Spores, obstacle.PoisonShroom]),
    # Level(
    #     floor_color_map=[(1,8), (5,2)],
    #     wall_color_map=[],# (1,2), (13,14)
    #     monster_classes=[character.Demon, character.Fiend, character.FireSprite],
    #     pre_level_text=textwrap.fill('''As you kill the last of the corrupted creatures, a dark figure in a hooded robe materializes at the forest's edge. Before you can focus on it, the shape dissolves into shadow. Your head erupts into searing pain, as a raspy voice booms in your mind. 'I have you in my grasp now,' it cackles. 'Good luck ever escaping me.' The world spins, then fades to black as you collapse. You wake up burning hot, and your eyes open to the sight of demons and fire - you'll need to fight through them to survive.''',
    #     TEXT_WIDTH),
    #     starting_elements=[obstacle.Fire, obstacle.Trap, obstacle.Shadow]
    #     ),
    # Level(
    #     floor_color_map=[(1,6), (5,7)],
    #     wall_color_map=[(13,12)],
    #     monster_classes=[character.IceDragon, character.SnowStalker, character.IceMonster],
    #     pre_level_text=textwrap.fill('''As the last demon falls, the infernal heat suddenly crystallizes into deadly cold. Your victory over the demons is cut short by a sinister laugh echoing through your mind and the realization that your journey is not taking you homeward. You crash onto a vast tundra, where howling winds whip endless sheets of snow and ice in every direction. Through the blinding white, you glimpse an ancient dragon's massive form circling overhead, its scales gleaming like shards of frozen starlight. You know instantly that this battle will be harder than all that came before.''',
    #     TEXT_WIDTH),
    #     starting_elements=[obstacle.Ice, obstacle.Trap]
    # ),
    # Level(
    #     floor_color_map=[],
    #     wall_color_map=[],
    #     monster_classes=[character.Ghost, character.WailingSpirit, character.Corpse, character.Skeleton],
    #     pre_level_text=textwrap.fill('''Your last enemy crashes to the frozen earth with a thunderous impact that splinters the ice beneath. But as the snow settles, the ground continues to crack and decay, the pristine white turning to rotting soil. The crisp winter air grows thick with the stench of decay, and through the mist rising from freshly disturbed graves, you see hands prying their way out of the earth. Horrors beyond your darkest nightmares emerge from the shadows - translucent spirits wailing in eternal agony, ethereal wraiths drifting between tombstones, and things for which you have no name. The sheer number and intensity of these abominations makes one thing clear: whatever force has been testing you is now desperate to ensure you don't survive this nightmare.''',
    #     TEXT_WIDTH),
    #     starting_elements=[obstacle.Shadow, obstacle.Trap, obstacle.Shadow]
    # ),
    Level(
        floor_color_map=[(1,8), (5,14)],
        wall_color_map=[(1,2), (13,8)],
        monster_classes=[character.MalformedFlesh, character.FleshGolem, character.BloodOoze],
        pre_level_text=textwrap.fill('''Your victory over the undead hordes is cut short as the mist-shrouded graveyard begins to pulse with an unnatural rhythm. Through the fog, you finally glimpse the hooded figure again - but this time they're stumbling backward, their confident posture replaced with panic. "No... impossible... you weren't supposed to make it this far!" they shriek before dissolving into shadow. The ground beneath you softens sickeningly, transforming from packed earth into something warm and organic. You find yourself in a grotesque chamber of living tissue, where half-formed creatures writhe in pools of viscous crimson, and monstrous flesh-golems lumber through pulsing tunnels of raw meat and sinew. The wet, rhythmic sounds of this place make your skin crawl as you realize you're trapped inside something impossibly vast and alive - but you're close now, so close to ending this nightmare.''',
        TEXT_WIDTH),
        starting_elements=[]
    ),
]