import pyxel

from collections import defaultdict, deque
from dataclasses import dataclass
from enum import auto, Enum
import itertools
from typing import Optional
import time
import statistics
# from board import Board

"""
average frame time = 0.0343 sec
colors (for aseprite use)
0,0,0 this is transparency
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

MAP_TILE_WIDTH = 5
MAP_TILE_HEIGHT = 5
WALL_THICKNESS = 32
GRID_COLOR = 11
FRAME_DURATION_MS = 34


# phase 1, generate play space based on 64x64 character. add wall boundaries
# phase 2, create move queue and read from them to move character around on grid
# phase 3, start UI, allow for mouse hover to highlight grid boxes
# phase 4, add log and be able to write to it.
# phase 5, add way to dynamically shape walls as obstacles.


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


@dataclass
class Action:
    character: str
    animation_type: str
    direction: Direction
    from_grid_pos: tuple
    to_grid_pos: tuple
    duration_ms: int = 1000
    action_steps: Optional[deque[tuple[int, int]]] = None


class PyxelActionQueue:
    def __init__(self):
        self.queue = deque()

    def enqueue(self, action: Action) -> None:
        self.queue.append(action)

    def is_empty(self) -> bool:
        return not len(self.queue)

    def dequeue(self) -> Action:
        if not self.is_empty():
            return self.queue.popleft()
        raise IndexError("Cannot pop from empty queue")

    def clear(self) -> None:
        self.queue.clear()

    def peek(self) -> Optional[Action]:
        if self.is_empty():
            return None
        return self.queue[0]


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
        self.board_end_pos = (
            self.canvas_width_px - wall_sprite_thickness_px // 2,
            self.canvas_height_px - wall_sprite_thickness_px,
        )

    def grid_pixels(self):
        x_values = range(
            self.board_start_pos[0], self.board_end_pos[0], self.tile_width_px
        )
        y_values = range(
            self.board_start_pos[1], self.board_end_pos[1], self.tile_height_px
        )

        return itertools.product(x_values, y_values)


@dataclass
class Wall:
    u: int  # x coord of where to start this particular wall
    v: int  # y coord of where to start this wall
    thickness: int  # in px, what size chunk to take out of sprite sheet
    direction: Direction  # NSwE
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


@dataclass
class Sprite:
    img_bank: int  # spriate sheet, 0-3
    u: int  # x-coord, pyxel nomenclature
    v: int  # y-coord, pyxel nomenclature
    w: int  # width
    h: int  # height


# sprites are currently 64x64
SPRITE_TILES = {
    "knight": {
        AnimationFrame.SOUTH: Sprite(
            img_bank=0,
            u=0,
            v=0,
            w=64,
            h=64,
        )
    }
}


def draw_tile(x, y, img_bank, u, v, w, h, colkey=0):
    pyxel.blt(x, y, img_bank, u, v, w, h, colkey)


class PyxelView:
    def __init__(
        self,
    ):
        test_map = [
            [None for _ in range(MAP_TILE_HEIGHT)] for _ in range(MAP_TILE_WIDTH)
        ]

        self.canvas = Canvas(
            board_tile_width=MAP_TILE_WIDTH,
            board_tile_height=MAP_TILE_HEIGHT,
            tile_width_px=64,
            tile_height_px=64,
            wall_sprite_thickness_px=32,
        )

        # add 32 to top and bottom for wall
        # add 16 to sides for wall
        pyxel.init(len(test_map) * 64 + 32, len(test_map[0]) * 64 + 64)

        self.dungeon_walls = {
            "north": Wall(
                0, 0, self.canvas.wall_sprite_thickness_px, Direction.NORTH, self.canvas
            ),
            "south": Wall(
                0,
                self.canvas.canvas_height_px - self.canvas.wall_sprite_thickness_px,
                self.canvas.wall_sprite_thickness_px,
                Direction.SOUTH,
                self.canvas,
            ),
            "west": Wall(0, 0, 32, Direction.WEST, self.canvas),
            "east": Wall(
                self.canvas.canvas_width_px - 32, 0, 32, Direction.EAST, self.canvas
            ),
        }
        self.characters = {
            "knight": {
                "animation_frame": AnimationFrame.SOUTH,
                "x": self.canvas.board_start_pos[0],
                "y": self.canvas.board_start_pos[1] + self.canvas.tile_height_px,
                "alive": True,
            }
        }
        self.x = self.canvas.board_start_pos[0]
        self.y = self.canvas.board_start_pos[1] + self.canvas.tile_height_px

        # Init action queue system
        self.action_queue = PyxelActionQueue()
        self.current_action = None

        # temp values
        self.start_time = time.time()
        self.time_diffs = []
        self.x_min = self.canvas.board_start_pos[0]
        self.x_max = (
            self.canvas.board_start_pos[0]
            + self.canvas.board_width_px
            - self.canvas.tile_width_px
        )
        self.direction = 1
        test_duration = 300
        test_action = Action(
            character="knight",
            animation_type="walk",
            direction="east",
            from_grid_pos=(0, 0),
            to_grid_pos=(1, 0),
            duration_ms=test_duration,
        )
        test_action2 = Action(
            character="knight",
            animation_type="walk",
            direction="east",
            from_grid_pos=(1, 0),
            to_grid_pos=(1, 1),
            duration_ms=test_duration,
        )
        test_action3 = Action(
            character="knight",
            animation_type="walk",
            direction="east",
            from_grid_pos=(1, 1),
            to_grid_pos=(1, 2),
            duration_ms=test_duration,
        )
        self.action_queue.enqueue(test_action)
        self.action_queue.enqueue(test_action2)
        self.action_queue.enqueue(test_action3)
        # end temp values

        pyxel.load("../my_resource.pyxres")
        pyxel.run(self.update, self.draw)

    def draw_sprite(self, x: int, y: int, sprite: Sprite, colkey=0) -> None:
        pyxel.blt(x, y, sprite.img_bank, sprite.u, sprite.v, sprite.w, sprite.h, colkey)

    # start with way to turn grid position to pixels within board
    def convert_grid_to_pixel_pos(self, tile_x: int, tile_y: int) -> tuple[int, int]:
        pixel_x = self.canvas.board_start_pos[0] + (tile_x * self.canvas.tile_width_px)
        pixel_y = self.canvas.board_start_pos[1] + (tile_y * self.canvas.tile_height_px)
        return (pixel_x, pixel_y)

    def get_px_move_steps_between_tiles(
        self,
        start_tile_pos: tuple[int, int],
        end_tile_pos: tuple[int, int],
        tween_time: int,
    ) -> deque[tuple[int, int]]:
        start_px_x, start_px_y = self.convert_grid_to_pixel_pos(
            start_tile_pos[0], start_tile_pos[1]
        )
        end_px_x, end_px_y = self.convert_grid_to_pixel_pos(
            end_tile_pos[0], end_tile_pos[1]
        )

        assert tween_time > FRAME_DURATION_MS, "action smaller than frame rate"
        step_count = tween_time // FRAME_DURATION_MS
        diff_px_x = end_px_x - start_px_x
        step_px_x = diff_px_x // step_count
        diff_px_y = end_px_y - start_px_y
        step_px_y = diff_px_y // step_count
        steps: deque = deque([])

        for step in range(step_count + 1):
            steps.append(
                (start_px_x + (step * step_px_x), start_px_y + (step * step_px_y))
            )

        # This guarantees that the sprite will end up on correct position
        steps.append((end_px_x, end_px_y))
        return steps

    def convert_and_append_move_steps_to_action(self, action: Action) -> Action:
        action.action_steps = self.get_px_move_steps_between_tiles(
            action.from_grid_pos, action.to_grid_pos, action.duration_ms
        )
        return action

    def process_action(self) -> None:
        print(f"{self.current_action.action_steps=}")
        if not self.current_action.action_steps:
            self.current_action = None  # better than del; no dangling logic
            return

        px_pos_x, px_pos_y = self.current_action.action_steps.popleft()
        action = self.current_action
        self.characters[action.character]["x"] = px_pos_x
        self.characters[action.character]["y"] = px_pos_y

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            print(f"{statistics.mean(self.time_diffs)=}")
            pyxel.quit()

        if not self.current_action and not self.action_queue.is_empty():
            self.current_action = self.convert_and_append_move_steps_to_action(
                self.action_queue.dequeue()
            )

        if self.current_action:
            self.process_action()

    def draw(self):
        pyxel.cls(0)

        occupied_coordinates = defaultdict(lambda: False)

        # Draw walls
        for cardinal_direction, wall in self.dungeon_walls.items():
            if wall is not None:
                assert isinstance(wall, Wall)
                if cardinal_direction not in self.dungeon_walls.keys():
                    raise ValueError("invalid cardinal_directiona")

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

        # Draw background
        for x in range(0, pyxel.width, BACKGROUND_TILES["dungeon_floor"]["w"]):
            for y in range(0, pyxel.height, BACKGROUND_TILES["dungeon_floor"]["h"]):
                if (x, y) not in occupied_coordinates:
                    draw_tile(x, y, **BACKGROUND_TILES["dungeon_floor"])

        # Draw sprites
        for character, attributes in self.characters.items():
            self.draw_sprite(
                attributes["x"],
                attributes["y"],
                SPRITE_TILES[character][attributes["animation_frame"]],
            )

        # Draw grids
        for tile_x, tile_y in self.canvas.grid_pixels():
            pyxel.rectb(
                tile_x,
                tile_y,
                self.canvas.tile_width_px,
                self.canvas.tile_height_px,
                GRID_COLOR,
            )


if __name__ == "__main__":
    PyxelView()
