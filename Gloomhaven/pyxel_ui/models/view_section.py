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
        """
        We initialize view sections to be active but not drawable,
        meaning they are taking up space on the screen, but we draw
        a blank space where they are until told otherwise
        """
        self.font = font
        self.start_pos = start_pos
        self.bounding_coordinate = bounding_coordinate
        self.end_pos = self.bounding_coordinate
        self.drawable = False
        self.active = True
        self.font_color = 7

    def clear_bounds(self) -> None:
        """a function to clear the view's area before redrawing itself"""
        if not self.active:
            return

        pyxel.rect(
            self.start_pos[0],
            self.start_pos[1],
            self.end_pos[0] - self.start_pos[0],
            self.end_pos[1] - self.start_pos[1],
            0,
        )

    def redraw(self) -> None:
        if not self.active:
            return
        self._redraw()

    def _redraw(self) -> None:
        self.draw()

    def draw(self) -> None:
        if not self.active:
            return
        self.clear_bounds()
        if not self.drawable:
            return

        self._draw()

    @abc.abstractmethod
    def _draw(self):
        pass


class BorderView(ViewSection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _draw(self) -> None:
        self.clear_bounds()


class LogView(ViewSection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._log: list[str] = []
        self.is_log_changed = False
        self.round_number: int = 0
        self.acting_character_name: str = ""
        # !!! I want to set this dynamically based on the amount of space we have
        self.max_log_lines: int = MAX_LOG_LINES
        self.text_pixels: list[tuple[int, int]] = None
        self.font_color = 7
        self.display_round_turn = True

    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, new_log: list[str]):
        """Prevents unnecessary redraws by rejecting log updates when content has not changed"""
        if new_log != self._log:
            self._log = new_log
            self.is_log_changed = True

    def _redraw(self) -> None:
        self.draw()
        # self.clear_bounds()
        # if not self.log and self.round_number <= 0:
        #     return
        # self.font.redraw_text(self.font_color, self.text_pixels)

    def _draw(self) -> None:
        # if not self.is_log_changed:
        #     return

        self.text_pixels = []

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
            self.text_pixels.extend(
                self.font.draw_text(
                    self.start_pos[0],
                    y_pos,
                    text,
                    col=self.font_color,
                    size=size,
                    max_width=self.bounding_coordinate[0] - self.start_pos[0],
                )
            )
            return y_pos + get_line_height(text)

        current_y = self.start_pos[1]
        available_height = self.bounding_coordinate[1] - self.start_pos[1]

        # Try to draw header
        if self.display_round_turn:
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

        self.is_log_changed = False


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


class CarouselView(ViewSection):
    """
    A view that scrolls through a carousel and has text
    The text pixels cache the current text for redrawing
    (which we do when we pass the cursor over the view section
    rather than fully drawing the text over again in order to
    speed things up)

    Requires you to specify how to draw items, and draw items
    must cache all text pixels in self.text_pixels or
    text will disappear from the screen as you move the cursor
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # !!! we should probably set a card width and then
        # set cards per page dynamically rather than the other
        # way around
        self.items: list[str] = []
        self.current_card_page = 0
        self.cards_per_page = 3
        self.text_pixels: list[tuple[int, int]] = None

    def _redraw(self) -> None:
        # self.clear_bounds()
        # if not self.items:
        #     return
        # self.font.redraw_text(7, self.text_pixels)
        self.draw()

    def _draw(self) -> None:
        self.text_pixels = []
        self.draw_page_indicator(self.start_pos[1])
        self.draw_items()
        self.draw_navigation_hints()

    @abc.abstractmethod
    def draw_items(self):
        pass

    def draw_page_indicator(self, y_start) -> None:
        total_pages = (len(self.items) + self.cards_per_page - 1) // self.cards_per_page
        page_text = f"Page {self.current_card_page + 1}/{total_pages}"
        pyxel.text(self.start_pos[0], y_start, page_text, col=self.font_color)

    def draw_navigation_hints(self) -> None:
        y_start = self.end_pos[1] - 20
        if self.current_card_page > 0:
            pyxel.text(self.start_pos[0], y_start, "<- Previous", col=self.font_color)
        if (self.current_card_page + 1) * self.cards_per_page < len(self.items):
            pyxel.text(self.end_pos[0] - 30, y_start, "-> Next", col=self.font_color)

    def go_to_next_page(self):
        if (self.current_card_page + 1) * self.cards_per_page < len(self.items):
            self.current_card_page += 1
            self.draw()

    def go_to_prev_page(self):
        if self.current_card_page > 0:
            self.current_card_page -= 1
            self.draw()


class ActionCardView(CarouselView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw_items(self) -> None:
        # Draw action cards
        start_idx = self.current_card_page * self.cards_per_page
        end_idx = min(start_idx + self.cards_per_page, len(self.items))

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
        for card in self.items[start_idx:end_idx]:
            self.text_pixels.extend(
                self.font.draw_text(
                    x, y, card, col=self.font_color, size="medium", max_width=card_width
                )
            )
            x += card_width + card_border


class InitiativeBarView(ViewSection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sprite_names: list[str] = []
        self.healths: list[int] = []
        self.max_healths: list[int] = []
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
            max_healths: List of max health values corresponding to sprites
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
                    f"{self.healths[actual_index]}/{self.max_healths[actual_index]}",
                    7,
                )

                # Draw team indicator line
                line_y = (
                    y_pos + BITS - self.sprite_width // 4
                )  # Position line below sprite
                line_color = (
                    8 if self.teams[actual_index] else 11
                )  # Red (8) for monsters, Green (11) for players

                # make line length relative to remaining health
                line_length = self.sprite_width - 2 * self.sprite_width // 4
                adjusted_length = round(
                    line_length
                    * self.healths[actual_index]
                    / self.max_healths[actual_index]
                )
                pyxel.line(
                    x_pos + self.sprite_width // 4,
                    line_y,
                    x_pos + self.sprite_width // 4 + adjusted_length,
                    line_y,
                    line_color,
                )


class SpriteView(ViewSection):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sprite_name = "wizard"
        self.sprite_manager = SpriteManager()
        self.drawable = True
        self.sprite_width = BITS
        self.sprite_x = (
            self.bounding_coordinate[0] - self.start_pos[0]
        ) / 2 - self.sprite_width
        self.sprite_y = 100

    def _draw(self) -> None:
        draw_sprite(
            self.sprite_x,
            self.sprite_y,
            self.sprite_manager.get_sprite(self.sprite_name, AnimationFrame.SOUTH),
            colkey=0,
            scale=4,
        )


class CharacterPickerView(CarouselView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cards_per_page = 1

    def draw_items(self):
        # Draw cards
        start_idx = self.current_card_page * self.cards_per_page
        end_idx = min(start_idx + self.cards_per_page, len(self.items))

        x = self.start_pos[0]
        # !!! ideally put something here that measures the height of the page indicator
        y = self.start_pos[1] + 200
        padding = 50
        card_border = 4
        card_width = (
            self.bounding_coordinate[0]
            - self.start_pos[0]
            - self.cards_per_page * card_border
        ) // self.cards_per_page
        # Draw only the current page of cards
        for i, card in enumerate(self.items[start_idx:end_idx]):
            sprite = SpriteView(self.font, [0, 10], self.end_pos)
            sprite.sprite_name = card["sprite_name"]
            sprite.draw()
            card_num = i + start_idx
            header = f"{card_num}: {card['name']}"
            self.font.draw_text(
                self.end_pos[0] / 2
                - self.font.get_text_width(header, size="large") / 2,
                y,
                header,
                col=self.font_color,
                size="large",
                max_width=card_width,
            )
            self.font.draw_text(
                x + padding,
                y + 30,
                card["backstory"],
                col=self.font_color,
                size="medium",
                max_width=card_width - padding,
            )
            x += card_width + card_border


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
    dither: float = 0.4,
) -> None:
    pyxel.dither(dither)
    pyxel.rect(px_x, px_y, px_width, px_height, color)
    pyxel.dither(1)
