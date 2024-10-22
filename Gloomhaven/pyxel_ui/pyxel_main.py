import pyxel

from collections import defaultdict, deque
import itertools
from typing import List, Optional

from .enums import AnimationFrame, Direction
from .models.actions import Action, PyxelActionQueue
from .models.canvas import Canvas
from .models.characters import Character
from .models.walls import Wall
from .utils import BACKGROUND_TILES
from .views.sprites import Sprite, SpriteManager


WALL_THICKNESS = 32
GRID_COLOR = 11
FRAME_DURATION_MS = 34


# phase 1, generate play space based on 64x64 character. add wall boundaries
# phase 2, create move queue and read from them to move character around on grid
# phase 3, start UI, allow for mouse hover to highlight grid boxes
# phase 4, add log and be able to write to it.
# phase 5, add way to dynamically shape walls as obstacles.


def draw_tile(x, y, img_bank, u, v, w, h, colkey=0):
    pyxel.blt(x, y, img_bank, u, v, w, h, colkey)


class PyxelView:
    def __init__(
        self, board: List[List[Optional[str]]], action_queue: PyxelActionQueue
    ):
        self.board_tile_width = len(board[0])
        self.board_tile_height = len(board)

        # TODO(John): replace these hardcoded numbers.
        pyxel.init(self.board_tile_width * 64 + 32, self.board_tile_height * 64 + 64)
        pyxel.load("../my_resource.pyxres")

        self.canvas = Canvas(
            board_tile_width=self.board_tile_width,
            board_tile_height=self.board_tile_height,
            tile_width_px=64,
            tile_height_px=64,
            wall_sprite_thickness_px=32,
        )

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
            "knight": Character(
                name="knight",
                x=self.canvas.board_start_pos[0],
                y=self.canvas.board_start_pos[1] + self.canvas.tile_height_px,
                animation_frame=AnimationFrame.SOUTH,
                alive=True,
            )
        }

        # Init action queue system
        self.action_queue = action_queue
        self.current_action = None

        self.sprite_manager = SpriteManager()

    def start(self):
        print("Starting Pyxel game loop...")
        pyxel.run(self.update, self.draw)

    def draw_sprite(self, x: int, y: int, sprite: Sprite, colkey=0) -> None:
        pyxel.blt(x, y, sprite.img_bank, sprite.u, sprite.v, sprite.w, sprite.h, colkey)

    def draw_background(self, tile_key: str, occupied_coordinates: dict):
        tile = BACKGROUND_TILES[tile_key]
        for x in range(0, pyxel.width, tile["w"]):
            for y in range(0, pyxel.height, tile["h"]):
                if (x, y) not in occupied_coordinates:
                    draw_tile(x, y, **tile)

    def convert_grid_to_pixel_pos(self, tile_x: int, tile_y: int) -> tuple[int, int]:
        """
        Converts grid-based tile coordinates to pixel coordinates on the canvas.

        Args:
            tile_x (int): The x-coordinate of the tile on the grid.
            tile_y (int): The y-coordinate of the tile on the grid.

        Returns:
            tuple[int, int]: The pixel coordinates corresponding to the grid position.
        """
        pixel_x = self.canvas.board_start_pos[0] + (tile_x * self.canvas.tile_width_px)
        pixel_y = self.canvas.board_start_pos[1] + (tile_y * self.canvas.tile_height_px)
        return (pixel_x, pixel_y)

    def get_px_move_steps_between_tiles(
        self,
        start_tile_pos: tuple[int, int],
        end_tile_pos: tuple[int, int],
        tween_time: int,
    ) -> deque[tuple[int, int]]:
        """
        Calculates the pixel-based steps for movement between two tiles.

        Movement is broken into discrete steps, where the number of steps determines
        the speed of the animation. The steps are stored as tuples of (x, y) pixel coordinates.

        Args:
            start_tile_pos (tuple[int, int]): The starting tile coordinates on the grid.
            end_tile_pos (tuple[int, int]): The target tile coordinates on the grid.
            tween_time (int): The total duration of the movement in milliseconds.

        Returns:
            deque[tuple[int, int]]: A deque containing the pixel coordinates for each step.

        Raises:
            AssertionError: If the tween time is shorter than the frame duration.
        """
        assert tween_time > FRAME_DURATION_MS, "Action smaller than frame rate"

        start_px_x, start_px_y = self.convert_grid_to_pixel_pos(*start_tile_pos)
        end_px_x, end_px_y = self.convert_grid_to_pixel_pos(*end_tile_pos)

        step_count = tween_time // FRAME_DURATION_MS
        diff_px_x = end_px_x - start_px_x
        diff_px_y = end_px_y - start_px_y

        return deque(
            (
                int(start_px_x + i / step_count * (diff_px_x)),
                int(start_px_y + i / step_count * (diff_px_y)),
            )
            for i in range(step_count + 1)
        )

    def convert_and_append_move_steps_to_action(self, action: Action) -> Action:
        """
        Converts grid-based movement coordinates into pixel-based steps and
        appends them to the action.

        Args:
            action (Action): The action containing the movement details.

        Returns:
            Action: The updated action with pixel-based movement steps added.
        """
        action.action_steps = self.get_px_move_steps_between_tiles(
            action.from_grid_pos, action.to_grid_pos, action.duration_ms
        )
        return action

    def process_action(self) -> None:
        assert self.current_action, "Attempting to process empty action"
        print(f"{self.current_action.action_steps=}")

        if not self.current_action.action_steps:
            print("Action processing complete. Clearing...")
            self.current_action = None  # better than del; no dangling logic
            return

        px_pos_x, px_pos_y = self.current_action.action_steps.popleft()
        self.characters[self.current_action.character].update_position(
            px_pos_x, px_pos_y
        )

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if not self.current_action and not self.action_queue.is_empty():
            self.current_action = self.convert_and_append_move_steps_to_action(
                self.action_queue.dequeue()
            )
            print(f"Has new action: {self.current_action}")
            return

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
                    self.draw_background("dungeon_floor", occupied_coordinates)

        # Draw sprites
        for character_name, character in self.characters.items():
            self.draw_sprite(
                character.x,
                character.y,
                self.sprite_manager.get_sprite(
                    character_name, character.animation_frame
                ),
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
