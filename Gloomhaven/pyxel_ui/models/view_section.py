import abc
import random
import pyxel
from pyxel_ui.utils import BACKGROUND_TILES, draw_tile
from pyxel_ui.constants import (
    GRID_COLOR,
    MAX_LOG_LINES,
)

class ViewSection(abc.ABC):
    def __init__(self, font, start_pos, bounding_coordinate):
        self.font = font
        self.start_pos = start_pos
        self.end_pos = start_pos
        self.bounding_coordinate = bounding_coordinate

    @abc.abstractmethod
    def draw(self):
        pass

WALL_DIRECTIONS = [
    {
        "coord": (1, 0),
        "wall_tile_name": "new_wall_ns",
        "height": 32,
        "width": 4,
    },
    {
        "coord": (-1, 0),
        "wall_tile_name": "new_wall_ns",
        "height": 32,
        "width": 4,
    },
    {
        "coord": (0, 1),
        "wall_tile_name": "new_wall_ew",
        "height": 4,
        "width": 32,
    },
    {
        "coord": (0, -1),
        "wall_tile_name": "new_wall_ew",
        "height": 4,
        "width": 32,
    },
]

class LogView(ViewSection):
    log: list[str] = []
    round_number: int = 0
    acting_character_name: str = ""
    max_log_lines: int = MAX_LOG_LINES

    def draw(self) -> None:
        # only draw if you have something loaded
        if not (self.log or self.round_number > 0):
            return 
        
        log_line_y = self.start_pos[1]
        
        for line in [f"Round {self.round_number}, {self.acting_character_name}'s turn"] + self.log[
            -self.max_log_lines:
        ]:
            self.font.draw_text(
                self.start_pos[0],
                log_line_y,
                line,
                col=7,
                size="medium",
                max_width=self.bounding_coordinate[0]-self.start_pos[0]
            )
            line_height = self.font.get_text_height(line, size="medium", max_width=self.bounding_coordinate[0]-self.start_pos[0]) + 4
            log_line_y += line_height

class MapView(ViewSection):
    dungeon_floor_tile_names: list[str] = [f"dungeon_floor_cracked_{i}" for i in range(1, 13)]
    valid_map_coordinates = [[]]
    tile_width_px = 0
    tile_height_px = 0

    def draw(self):
        self.draw_map_background()
        self.draw_map_grid()

    def draw_map_background(self):
        # ensure we get the same floor tiles each time we draw the floor
        random.seed(100)

        for x, y in self.valid_map_coordinates:
            # get coordinates
            x_px = x * self.tile_width_px + self.start_pos[0]
            y_px = y * self.tile_height_px + self.start_pos[1]

            # draw floor tile
            floor_tile = BACKGROUND_TILES[random.choice(self.dungeon_floor_tile_names)]
            draw_tile(x_px, y_px, **floor_tile)

            # draw walls where there's blank space
            self.draw_necessary_walls(x, y, x_px, y_px)

    def draw_necessary_walls(self, x, y, x_px, y_px):
        for direction in WALL_DIRECTIONS:
            neighbor_coord = tuple(a + b for a, b in zip((x, y), direction["coord"]))
            # if the neighbor isn't blank space, no walls
            if neighbor_coord in self.valid_map_coordinates:
                continue

            # otherwise, calculate where the wall should be and draw it
            x_px_wall = (
                x_px + self.tile_width_px * direction["coord"][0]
                if direction["coord"][0] > 0
                else x_px + direction["width"] * direction["coord"][0]
            )
            y_px_wall = (
                y_px + self.tile_height_px * direction["coord"][1]
                if direction["coord"][1] > 0
                else y_px + direction["height"] * direction["coord"][1]
            )
            draw_tile(
                x_px_wall,
                y_px_wall,
                **BACKGROUND_TILES[direction["wall_tile_name"]],
            )

    def draw_map_grid(self) -> None:
        # draw grid only on valid map coordinates
        for x, y in self.valid_map_coordinates:
            pyxel.rectb(
                x * self.tile_width_px + self.start_pos[0],
                y * self.tile_height_px + self.start_pos[1],
                self.tile_width_px,
                self.tile_height_px,
                GRID_COLOR,
            )
