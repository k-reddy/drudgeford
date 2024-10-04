import pyxel

from collections import defaultdict
from dataclasses import dataclass
from enum import auto, Enum
import itertools

"""
colors
0,0,0
43,51,95
126,32,114
25,149,156
139,72,82
57,92,152
169,193,255


238,238,238 sucks


212,24,108
211,132,65
233,195,91
112,198,169
118,150,222
163,163,163
255,151,152
237,199,176

"""


"""
optimizations
instead of y is magic value,
might wanna go back to actually having
"""

CANVAS_WIDTH = 256
CANVAS_HEIGHT = 256


class Direction(Enum):
    NORTH = auto()
    WEST = auto()
    EAST = auto()
    SOUTH = auto()


@dataclass
class Wall:
    u: int
    v: int
    thickness: int
    direction: Direction

    def pixels(self):
        if self.direction is Direction.NORTH:
            return range(self.u, CANVAS_WIDTH, self.thickness), itertools.repeat(0, CANVAS_WIDTH // self.thickness)


# 32, 32
# 98 75 is the upper wall
DUNGEON_WALLS = {
    "north": Wall(0, 0, 32, Direction.NORTH),
    "west": None,
    "east": None,
    "south": None,
}

BACKGROUND_TILES = {
    "dungeon_floor": {
        "img_bank": 1,
        "u": 111,
        "v": 106,
        "w": 32,
        "h": 32,
    },
    "dungeon_wall_north": {
        "img_bank": 1,
        "u": 98,
        "v": 75,
        "w": 32,
        "h": 32,
    },
}

BACKGROUND_TILE_HEIGHT = 32
BACKGROUND_TILE_WIDTH = 32


class AnimationFrame(Enum):
    NORTH = auto()
    WEST = auto()
    EAST = auto()
    SOUTH = auto()
    IDLE_1 = auto()
    IDLE_2 = auto()


# sprites are currently 64x64
SPRITE_TILES = {"knight": {}}


def draw_tile(x, y, img_bank, u, v, w, h, colkey=0):
    pyxel.blt(x, y, img_bank, u, v, w, h, colkey)


class PyxelView:
    def __init__(self):
        pyxel.init(CANVAS_WIDTH, CANVAS_HEIGHT)
        self.x = 64
        self.y = 64
        pyxel.load("../my_resource.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        self.x = (self.x + 1) % pyxel.width

    def draw(self):
        pyxel.cls(0)

        occupied_coordinates = defaultdict(lambda: False)

        for cardinal_direction, wall in DUNGEON_WALLS.items():
            if wall is not None:
                assert isinstance(wall, Wall)
                if cardinal_direction == "north" or cardinal_direction == "south":
                    pixels = itertools.product(*wall.pixels())
                    for x, y in pixels:
                        draw_tile(
                            x,
                            y,
                            **BACKGROUND_TILES[f"dungeon_wall_{cardinal_direction}"],
                        )
                        occupied_coordinates[(x, y)] = True
                    # pixels_x = range(wall.u, CANVAS_WIDTH, wall.thickness)
                    # pixels_y = range(wall.v, wall.thickness)
                    # for x in pixels_x:
                    #     draw_tile(
                    #         x,
                    #         y,
                    #         **BACKGROUND_TILES[f"dungeon_wall_{cardinal_direction}"],
                    #     )
                    #     occupied_coordinates[(x, y)] = True
                else:
                    ...

        # Draw background
        for x in range(0, pyxel.width, BACKGROUND_TILES["dungeon_floor"]["w"]):
            for y in range(0, pyxel.height, BACKGROUND_TILES["dungeon_floor"]["h"]):
                if (x, y) not in occupied_coordinates:
                    draw_tile(x, y, **BACKGROUND_TILES["dungeon_floor"])

        # Draw characters
        pyxel.blt(self.x, self.y, 0, 0, 0, 64, 64, 0)


PyxelView()
