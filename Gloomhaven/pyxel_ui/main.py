import pyxel

from collections import defaultdict
from dataclasses import dataclass
from enum import auto, Enum
import itertools

# from typing import Iterable, Tuple, Union

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

MAP_TILE_WIDTH = 4
MAP_TILE_HEIGHT = 4
WALL_THICKNESS = 32

test_map = [[None for _ in range(4)] for _ in range(4)]  # test with 4 x 4 map
# phase 1, generate play space based on 64x64 character. add wall boundaries

"""
for every cell, check all directions to see if there is a tile there.
if there is no tile, generate appropriate tile for direction.
fill tile with floor.
"""

"""
if no tiles touch the edge, redefine the edge by marking tiles as "edge" and
treating that as an edge.
"""

"""
if the tile is an obstacle, first, check to see if it touches an edge, another obstacle
or if the tile group is edge accessible. <- memoize this.
"""


class Direction(Enum):
    NORTH = auto()
    WEST = auto()
    EAST = auto()
    SOUTH = auto()


class Canvas:
    """
    Canvas class to manage the board's dimensions and position.
    Assumes that East/West wall tiles are half the width of North/South

    Attributes:
        board_tile_width (int): Number of tiles along the board's width.
        board_tile_height (int): Number of tiles along the board's height.
        tile_width_px (int): Width of a single tile in pixels.
        tile_height_px (int): Height of a single tile in pixels.
        wall_sprite_thickness_px (int): Thickness of the wall sprite in pixels.
        board_start_pos (tuple): Starting position of the board in pixels.
        board_width_px (int): Total width of the board in pixels.
        board_height_px (int): Total height of the board in pixels.
        canvas_width_px (int): Total width of the canvas in pixels.
        canvas_height_px (int): Total height of the canvas in pixels.
    """

    def __init__(
        self,
        board_tile_width,
        board_tile_height,
        tile_width_px,
        tile_height_px,
        wall_sprite_thickness_px,
    ):
        self.board_tile_width = board_tile_width
        self.board_tile_height = board_tile_height
        self.tile_width_px = tile_width_px
        self.tile_height_px = tile_height_px
        self.wall_sprite_thickness_px = wall_sprite_thickness_px

        # Calculate the board start position and sizes
        self.board_start_pos = (wall_sprite_thickness_px // 2, wall_sprite_thickness_px)
        self.board_width_px = board_tile_width * tile_width_px
        self.board_height_px = board_tile_height * tile_height_px
        self.canvas_width_px = self.board_width_px + wall_sprite_thickness_px
        self.canvas_height_px = self.board_height_px + (2 * wall_sprite_thickness_px)


@dataclass
class Wall:
    u: int
    v: int
    thickness: int
    direction: Direction
    canvas: Canvas

    def pixels(
        self,
    ):  # -> Tuple[Iterable[int], Iterable[int]]: should be, but mypy has issues with this
        """
        Returns a tuple of iterables representing the x and y coordinates of the wall's pixels.
        The tuple is always in the form (x_values, y_values).
        """
        canvas_width = self.canvas.canvas_width_px
        canvas_height = self.canvas.canvas_height_px

        if self.direction is Direction.NORTH or self.direction is Direction.SOUTH:
            x_values = range(self.u, canvas_width, self.thickness)
            y_values = itertools.repeat(self.v, canvas_width // self.thickness)
        elif self.direction is Direction.WEST or self.direction is Direction.EAST:
            x_values = itertools.repeat(self.u, canvas_height // self.thickness)
            y_values = range(self.v, canvas_height, self.thickness)
        else:
            raise ValueError(f"Unsupported direction: {self.direction}")

        return x_values, y_values


# 32, 32
# 98 75 is the upper wall


BACKGROUND_TILES = {
    "dungeon_floor": {
        "img_bank": 1,
        "u": 113,
        "v": 108,
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
    "dungeon_wall_south": {
        "img_bank": 1,
        "u": 96,
        "v": 156,
        "w": 32,
        "h": 32,
    },
    "dungeon_wall_west": {
        "img_bank": 1,
        "u": 81,
        "v": 108,
        "w": 32,
        "h": 32,
    },
    "dungeon_wall_east": {
        "img_bank": 1,
        "u": 144,
        "v": 108,
        "w": 32,
        "h": 32,
    },
}


class AnimationFrame(Enum):
    NORTH = auto()
    WEST = auto()
    EAST = auto()
    SOUTH = auto()
    IDLE_1 = auto()
    IDLE_2 = auto()


# sprites are currently 64x64
SPRITE_TILES = {
    "knight": {
        AnimationFrame.SOUTH: {
            "img_bank": 0,
            "u": 0,
            "v": 0,
            "w": 64,
            "h": 64,
        }
    }
}


def draw_tile(x, y, img_bank, u, v, w, h, colkey=0):
    pyxel.blt(x, y, img_bank, u, v, w, h, colkey)


class PyxelView:
    def __init__(self):
        test_map = [
            [None for _ in range(MAP_TILE_WIDTH)] for _ in range(MAP_TILE_HEIGHT)
        ]
        # add 32 to top and bottom for wall
        # add 16 to sides for wall
        pyxel.init(len(test_map) * 64 + 32, len(test_map[0]) * 64 + 64)
        # pyxel.init(256, 256)  # test
        canvas = Canvas(
            board_tile_width=MAP_TILE_WIDTH,
            board_tile_height=MAP_TILE_HEIGHT,
            tile_width_px=64,
            tile_height_px=64,
            wall_sprite_thickness_px=32,
        )

        self.dungeon_walls = {
            "north": Wall(0, 0, canvas.board_tile_height, Direction.NORTH, canvas),
            "south": Wall(
                0,
                canvas.canvas_height_px - canvas.tile_height_px,
                canvas.board_tile_height,
                Direction.SOUTH,
                canvas,
            ),
            "west": Wall(0, 0, 32, Direction.WEST, canvas),
            "east": Wall(canvas.canvas_width_px - 32, 0, 32, Direction.EAST, canvas),
        }
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

        # Draw walls
        for cardinal_direction, wall in self.dungeon_walls.items():
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
                if cardinal_direction == "west" or cardinal_direction == "east":
                    pixels = itertools.product(*wall.pixels())

                    for x, y in pixels:
                        if (x, y) in occupied_coordinates:
                            continue
                        draw_tile(
                            x,
                            y,
                            **BACKGROUND_TILES[f"dungeon_wall_{cardinal_direction}"],
                        )
                        occupied_coordinates[(x, y)] = True
                else:
                    ...

        # Draw background
        for x in range(0, pyxel.width, BACKGROUND_TILES["dungeon_floor"]["w"]):
            for y in range(0, pyxel.height, BACKGROUND_TILES["dungeon_floor"]["h"]):
                if (x, y) not in occupied_coordinates:
                    draw_tile(x, y, **BACKGROUND_TILES["dungeon_floor"])

        # Draw characters
        draw_tile(self.x, self.y, **SPRITE_TILES["knight"][AnimationFrame.SOUTH])


PyxelView()
