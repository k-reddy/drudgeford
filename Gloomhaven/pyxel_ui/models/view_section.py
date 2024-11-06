import abc
import random
import pyxel
from pyxel_ui.utils import BACKGROUND_TILES, draw_tile
from pyxel_ui.views.sprite import Sprite, SpriteManager
from pyxel_ui.enums import AnimationFrame
from pyxel_ui.constants import (
    GRID_COLOR,
    MAX_LOG_LINES,
    BITS
)
from pyxel_ui.models.entity import Entity


# !!! somehow enforce the end bounds throughout
# !!! have tasks update the view data directly

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

class ViewSection(abc.ABC):
    def __init__(self, font, start_pos, bounding_coordinate):
        self.font = font
        self.start_pos = start_pos
        self.end_pos = start_pos
        self.bounding_coordinate = bounding_coordinate

    @abc.abstractmethod
    def draw(self):
        pass

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
    sprite_manager = SpriteManager()
    entities = {}

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

    def draw_sprites(self) -> None:
        """draws entity sprites with a notion of priority"""
        max_priority = max((entity.priority for entity in self.entities.values()), default=0)
        for i in range(0, max_priority + 1):
            for _, entity in self.entities.items():
                if entity.priority == i:
                    draw_sprite(
                        entity.x,
                        entity.y,
                        self.sprite_manager.get_sprite(
                            entity.name, entity.animation_frame
                        ),
                    )

class ActionCardView(ViewSection):
    action_card_log: list[str] = []
    current_card_page = 0
    cards_per_page = 3
    def draw(self) -> None:
        # Draw action cards
        start_idx = self.current_card_page * self.cards_per_page
        end_idx = min(start_idx + self.cards_per_page, len(self.action_card_log))

        x = self.start_pos[0]
        card_border = 4
        card_width = (self.bounding_coordinate[0]-self.start_pos[0]-self.cards_per_page*card_border)//self.cards_per_page
        # Draw only the current page of cards
        for card in self.action_card_log[start_idx:end_idx]:
            self.font.draw_text(x, self.start_pos[1], card, col=7, size="medium", max_width=card_width)
            x += card_width + card_border

        if self.action_card_log:
            # !!! should change this to measure the height of the cards
            indicator_navig_start_y = self.start_pos[1] + BITS * 4 + card_border
            self.draw_page_indicator(indicator_navig_start_y)
            self.draw_navigation_hints(x, indicator_navig_start_y)

    def draw_page_indicator(self, y_start) -> None:
        total_pages = (len(self.action_card_log) + self.cards_per_page - 1) // self.cards_per_page
        page_text = f"Page {self.current_card_page + 1}/{total_pages}"
        pyxel.text(0, y_start, page_text, col=7)

    def draw_navigation_hints(self, x_start, y_start) -> None:
        if self.current_card_page > 0:
            pyxel.text(BITS * 3, y_start, "<- Previous", col=7)
        if (self.current_card_page + 1) * self.cards_per_page < len(self.action_card_log):
            pyxel.text(x_start, y_start, "-> Next", col=7)

class InitiativeBarView(ViewSection):
    sprite_names: list[str] = []
    healths: list[int] = []
    teams: list[bool] = []
    horiz_gap = 12
    sprite_width = BITS  # BITS is the sprite width constant
    font_offset = BITS // 4
    vertical_gap = BITS  # Gap between rows
    sprite_manager = SpriteManager()

    def draw(self) -> None:
        """
        Draw a bar showing health and initiative for sprites, with team indicators.

        Args:
            sprite_names: List of sprite names to display
            healths: List of health values corresponding to sprites
            teams: List of boolean values (True for monster team, False for player team)
        """
        # Calculate maximum items per row based on screen width
        item_width = self.sprite_width + self.horiz_gap
        # Leave some margin on both sides
        usable_width = self.bounding_coordinate[0] - self.start_pos[0] - (self.sprite_width // 2)
        items_per_row = max(1, usable_width // item_width)

        # Calculate items for each row
        first_row = self.sprite_names[:items_per_row]
        second_row = self.sprite_names[items_per_row:]

        for row_num, row_items in enumerate([first_row, second_row]):
            if not row_items:
                continue

            # Calculate total width needed for this row
            item_width = self.sprite_width + self.horiz_gap
            row_width = item_width * len(row_items)

            # Center alignment calculation for this row
            screen_center_x = (self.bounding_coordinate[0]-self.start_pos[0])//2
            start_x = screen_center_x - (row_width // 2)

            for i, sprite_name in enumerate(row_items):
                actual_index = i if row_num == 0 else i + items_per_row

                # Calculate x and y positions
                x_pos = start_x + (i * (self.sprite_width + self.horiz_gap))
                y_pos = row_num * self.vertical_gap

                # Draw sprite
                draw_sprite(
                    x_pos,
                    y_pos,
                    self.sprite_manager.get_sprite(sprite_name, AnimationFrame.SOUTH),
                    colkey=0,
                    scale=0.5,
                )

                # Draw health text
                pyxel.text(x_pos + self.font_offset, y_pos, f"H:{self.healths[actual_index]}", 7)

                # Draw team indicator line
                line_y = y_pos + BITS - self.sprite_width // 4  # Position line below sprite
                line_color = (
                    8 if self.teams[actual_index] else 11
                )  # Red (8) for monsters, Green (11) for players
                pyxel.line(
                    x_pos + self.sprite_width // 4,
                    line_y,
                    x_pos + self.sprite_width - self.sprite_width // 4,
                    line_y,
                    line_color,
                )

def draw_sprite(x, y, sprite: Sprite, colkey=0, scale=1) -> None:
    pyxel.blt(
        x,
        y,
        sprite.img_bank,
        sprite.u,
        sprite.v,
        sprite.w,
        sprite.h,
        colkey,
        scale=scale,
    )