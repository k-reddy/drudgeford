import abc
import random
import pyxel

from pyxel_ui.utils import draw_tile
from pyxel_ui.views.sprite import Sprite, SpriteManager
from pyxel_ui.enums import AnimationFrame
from pyxel_ui.constants import (
    GRID_COLOR,
    MAX_LOG_LINES,
    BITS,
    BACKGROUND_TILES,
    WALL_DIRECTIONS,
)

# !!! somehow enforce the end bounds throughout
# !!! have tasks update the view data directly
# !!! figure out who should be initializing the views and managing them


class ViewSection(abc.ABC):
    """view sections are pieces of the pyxel display that
    know their own data and draw themselves within the bounds they
    are given by the controller"""

    def __init__(self, font, start_pos, bounding_coordinate):
        self.font = font
        self.start_pos = start_pos
        self.bounding_coordinate = bounding_coordinate
        self.end_pos = self.bounding_coordinate
        self.drawable = False

    def clear_bounds(self):
        """a function to clear the view's area before redrawing itself"""
        pyxel.rect(
            self.start_pos[0],
            self.start_pos[1],
            self.end_pos[0] - self.start_pos[0],
            self.end_pos[1] - self.start_pos[1],
            0,
        )

    def draw(self) -> None:
        self.clear_bounds()
        if not self.drawable:
            return

        self._draw()

    @abc.abstractmethod
    def _draw(self):
        pass


class LogView(ViewSection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log: list[str] = []
        self.round_number: int = 0
        self.acting_character_name: str = ""
        # !!! I want to set this dynamically based on the amount of space we have
        self.max_log_lines: int = MAX_LOG_LINES

    def _draw(self) -> None:
        def get_line_height(text: str) -> int:
            return (
                self.font.get_text_height(
                    text,
                    size="medium",
                    max_width=self.bounding_coordinate[0] - self.start_pos[0],
                )
                + 4
            )

        def draw_line(text: str, y_pos: int, size: str = "medium") -> int:
            self.font.draw_text(
                self.start_pos[0],
                y_pos,
                text,
                col=7,
                size=size,
                max_width=self.bounding_coordinate[0] - self.start_pos[0],
            )
            return y_pos + get_line_height(text)

        current_y = self.start_pos[1]
        available_height = self.bounding_coordinate[1] - self.start_pos[1]

        # Try to draw header
        header = f"Round {self.round_number}, {self.acting_character_name}'s turn"
        header_height = get_line_height(header)

        if header_height <= available_height:
            current_y = draw_line(header, current_y, "large")
            available_height -= header_height

        # Get displayable log lines
        lines = []
        for line in reversed(self.log[-self.max_log_lines :]):
            line_height = get_line_height(line)
            if line_height <= available_height:
                lines.insert(0, line)
                available_height -= line_height
            else:
                break

        # Draw log lines
        for line in lines:
            current_y = draw_line(line, current_y)

        # Why are we re-sizing the log view port?
        # self.end_pos = (self.bounding_coordinate[0], current_y)


class MapView(ViewSection):
    def __init__(
        self,
        font,
        start_pos,
        bounding_coordinate,
        floor_color_map=[],
        wall_color_map=[],
    ):
        super().__init__(font, start_pos, bounding_coordinate)
        self.dungeon_floor_tile_names: list[str] = [
            f"dungeon_floor_cracked_{i}" for i in range(1, 13)
        ]
        self.valid_map_coordinates = [[]]
        # !!! these 2 should probably be set in the init
        self.tile_width_px = BITS
        self.tile_height_px = BITS
        self.sprite_manager = SpriteManager()
        self.entities = {}
        self.floor_color_map = floor_color_map
        self.wall_color_map = wall_color_map

    def _draw(self):
        self.draw_map_background()
        self.draw_map_grid()
        self.draw_sprites()

    def draw_map_background(self):
        # ensure we get the same floor tiles each time we draw the floor
        random.seed(100)
        for x, y in self.valid_map_coordinates:
            # get coordinates
            x_px = x * self.tile_width_px + self.start_pos[0]
            y_px = y * self.tile_height_px + self.start_pos[1]

            # draw floor tile
            floor_tile = BACKGROUND_TILES[random.choice(self.dungeon_floor_tile_names)]
            self.set_colors(self.floor_color_map)
            draw_tile(x_px, y_px, **floor_tile)
            pyxel.pal()
            self.set_colors(self.wall_color_map)
            # draw walls where there's blank space
            self.draw_necessary_walls(x, y, x_px, y_px)
            pyxel.pal()

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
        # draw grid only on valid map coordinates'
        for x, y in self.valid_map_coordinates:
            pyxel.rectb(
                x * self.tile_width_px + self.start_pos[0],
                y * self.tile_height_px + self.start_pos[1],
                self.tile_width_px,
                self.tile_height_px,
                GRID_COLOR,
            )

    def set_colors(self, mapping: list[tuple[int, int]]) -> None:
        # 11 light green
        # 3 dark green
        # 5 blue
        # 1 dark blue
        """maps colors in the pyxel palette"""
        pyxel.pal()
        if mapping:
            for orig_col, new_col in mapping:
                pyxel.pal(orig_col, new_col)

    def draw_sprites(self) -> None:
        """draws entity sprites with a notion of priority"""
        max_priority = max(
            (entity.priority for entity in self.entities.values()), default=0
        )
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

    def convert_grid_to_pixel_pos(self, tile_x: int, tile_y: int) -> tuple[int, int]:
        """Converts grid-based tile coordinates to pixel coordinates on the canvas."""
        pixel_x = self.start_pos[0] + (tile_x * self.tile_width_px)
        pixel_y = self.start_pos[1] + (tile_y * self.tile_height_px)
        return (pixel_x, pixel_y)


class ActionCardView(ViewSection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # !!! we should probably set a card width and then
        # set cards per page dynamically rather than the other
        # way around
        self.action_card_log: list[str] = []
        self.current_card_page = 0
        self.cards_per_page = 3

    def _draw(self) -> None:
        self.draw_page_indicator(self.start_pos[1])

        # Draw action cards
        start_idx = self.current_card_page * self.cards_per_page
        end_idx = min(start_idx + self.cards_per_page, len(self.action_card_log))

        x = self.start_pos[0]
        # !!! ideally put something here that measures the height of the page indicator
        y = self.start_pos[1] + 10
        card_border = 4
        card_width = (
            self.bounding_coordinate[0]
            - self.start_pos[0]
            - self.cards_per_page * card_border
        ) // self.cards_per_page
        # Draw only the current page of cards
        for card in self.action_card_log[start_idx:end_idx]:
            self.font.draw_text(x, y, card, col=7, size="medium", max_width=card_width)
            x += card_width + card_border

        # !!! should change this to measure the height of the cards and page indicator
        navigation_start_y = self.start_pos[1] + BITS * 6 + card_border + 10
        self.draw_navigation_hints(x - card_width // 2, navigation_start_y)

    def draw_page_indicator(self, y_start) -> None:
        total_pages = (
            len(self.action_card_log) + self.cards_per_page - 1
        ) // self.cards_per_page
        page_text = f"Page {self.current_card_page + 1}/{total_pages}"
        pyxel.text(self.start_pos[0], y_start, page_text, col=7)

    def draw_navigation_hints(self, x_start_next, y_start) -> None:
        if self.current_card_page > 0:
            pyxel.text(self.start_pos[0], y_start, "<- Previous", col=7)
        if (self.current_card_page + 1) * self.cards_per_page < len(
            self.action_card_log
        ):
            pyxel.text(x_start_next, y_start, "-> Next", col=7)


class InitiativeBarView(ViewSection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sprite_names: list[str] = []
        self.healths: list[int] = []
        self.teams: list[bool] = []
        # !!! we should rename bits or something b/c this feels sort of arbitrary
        self.horiz_gap = 12
        self.sprite_width = BITS  # BITS is the sprite width constant
        self.font_offset = BITS // 4
        self.vertical_gap = BITS  # Gap between rows
        self.sprite_manager = SpriteManager()

    def _draw(self) -> None:
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
        usable_width = (
            self.bounding_coordinate[0] - self.start_pos[0] - (self.sprite_width // 2)
        )
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
            screen_center_x = (self.bounding_coordinate[0] - self.start_pos[0]) // 2
            start_x = screen_center_x - (row_width // 2)

            for i, sprite_name in enumerate(row_items):
                actual_index = i if row_num == 0 else i + items_per_row

                # Calculate x and y positions
                x_pos = start_x + (i * (self.sprite_width + self.horiz_gap))
                y_pos = row_num * self.vertical_gap + self.start_pos[1]

                # Draw sprite
                draw_sprite(
                    x_pos,
                    y_pos,
                    self.sprite_manager.get_sprite(sprite_name, AnimationFrame.SOUTH),
                    colkey=0,
                    scale=0.5,
                )

                # Draw health text
                pyxel.text(
                    x_pos + self.font_offset,
                    y_pos,
                    f"H:{self.healths[actual_index]}",
                    7,
                )

                # Draw team indicator line
                line_y = (
                    y_pos + BITS - self.sprite_width // 4
                )  # Position line below sprite
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


class SpriteView(ViewSection):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sprite_name = "wizard"
        self.sprite_manager = SpriteManager()
        self.drawable = True

    def _draw(self) -> None:
        draw_sprite(
            0,
            0,
            self.sprite_manager.get_sprite(self.sprite_name, AnimationFrame.SOUTH),
            colkey=0,
            scale=4,
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


def draw_grid(
    px_x: int,
    px_y: int,
    px_width: int,
    px_height: int,
    color: int = 3,
) -> None:
    pyxel.rect(px_x, px_y, px_width, px_height, color)
