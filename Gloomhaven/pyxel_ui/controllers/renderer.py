# renderer.py
import pyxel
import random

from pyxel_ui.constants import (
    BITS,
    FONT_PATH,
    GRID_COLOR,
    MAX_LOG_LINES,
)
from pyxel_ui.enums import AnimationFrame
from pyxel_ui.models.entity import Entity
from pyxel_ui.models.font import PixelFont
from pyxel_ui.utils import BACKGROUND_TILES, draw_tile
from pyxel_ui.views.sprite import Sprite, SpriteManager
from pyxel_ui.models.view_section import LogView, MapView


class Renderer:
    def __init__(self, canvas):
        print(f"{FONT_PATH=}")
        self.canvas = canvas
        self.sprite_manager = SpriteManager()
        self.font = PixelFont(pyxel, f"../{FONT_PATH}")
        self.mapview = MapView(
            self.font, 
            self.canvas.board_start_pos,
            [BITS*10, BITS*10]
            )

    # Card related methods grouped together
    def draw_action_cards(
        self, action_card_log, current_card_page, cards_per_page
    ) -> None:
        # Draw action cards
        start_idx = current_card_page * cards_per_page
        end_idx = min(start_idx + cards_per_page, len(action_card_log))

        x = 0
        y = self.canvas.board_end_pos[1] + BITS // 2

        # Draw only the current page of cards
        for line in action_card_log[start_idx:end_idx]:
            self.font.draw_text(x, y, line, col=7, size="medium", max_width=BITS * 6)
            x += BITS * 6 + 4

        if action_card_log:
            self.draw_page_indicator(
                y,
                action_card_log,
                cards_per_page,
                current_card_page,
            )
            self.draw_navigation_hints(
                y,
                end_idx,
                action_card_log,
                cards_per_page,
                current_card_page,
            )

    def draw_page_indicator(
        self,
        y,
        action_card_log,
        cards_per_page,
        current_card_page,
    ) -> None:
        indicator_y = y + BITS * 4
        total_pages = (len(action_card_log) + cards_per_page - 1) // cards_per_page
        page_text = f"Page {current_card_page + 1}/{total_pages}"
        pyxel.text(0, indicator_y, page_text, col=7)

    def draw_navigation_hints(
        self,
        y,
        end_idx,
        action_card_log,
        cards_per_page,
        current_card_page,
    ) -> None:
        indicator_y = y + BITS * 4
        if current_card_page > 0:
            pyxel.text(BITS * 3, indicator_y, "<- Previous", col=7)
        if (current_card_page + 1) * cards_per_page < len(action_card_log):
            pyxel.text(BITS * (end_idx - 1) * 4, indicator_y, "-> Next", col=7)

    # End card methods
    
    def draw_health_and_iniative_bar(
        self,
        sprite_names: list[str],
        healths: list[int],
        teams: list[bool],
    ) -> None:
        """
        Draw a bar showing health and initiative for sprites, with team indicators.

        Args:
            sprite_names: List of sprite names to display
            healths: List of health values corresponding to sprites
            teams: List of boolean values (True for monster team, False for player team)
        """
        horiz_gap = 12
        sprite_width = BITS  # BITS is the sprite width constant
        font_offset = BITS // 4
        vertical_gap = BITS  # Gap between rows

        # Calculate maximum items per row based on screen width
        item_width = sprite_width + horiz_gap
        # Leave some margin on both sides
        usable_width = pyxel.width - (sprite_width // 2)
        items_per_row = max(1, usable_width // item_width)

        # Calculate items for each row
        first_row = sprite_names[:items_per_row]
        second_row = sprite_names[items_per_row:]

        for row_num, row_items in enumerate([first_row, second_row]):
            if not row_items:
                continue

            # Calculate total width needed for this row
            item_width = sprite_width + horiz_gap
            row_width = item_width * len(row_items)

            # Center alignment calculation for this row
            screen_center_x = pyxel.width // 2
            start_x = screen_center_x - (row_width // 2)

            for i, sprite_name in enumerate(row_items):
                actual_index = i if row_num == 0 else i + items_per_row

                # Calculate x and y positions
                x_pos = start_x + (i * (sprite_width + horiz_gap))
                y_pos = row_num * vertical_gap

                # Draw sprite
                self.draw_sprite(
                    x_pos,
                    y_pos,
                    self.sprite_manager.get_sprite(sprite_name, AnimationFrame.SOUTH),
                    colkey=0,
                    scale=0.5,
                )

                # Draw health text
                pyxel.text(x_pos + font_offset, y_pos, f"H:{healths[actual_index]}", 7)

                # Draw team indicator line
                line_y = y_pos + BITS - sprite_width // 4  # Position line below sprite
                line_color = (
                    8 if teams[actual_index] else 11
                )  # Red (8) for monsters, Green (11) for players
                pyxel.line(
                    x_pos + sprite_width // 4,
                    line_y,
                    x_pos + sprite_width - sprite_width // 4,
                    line_y,
                    line_color,
                )
            # self.canvas.board_start_pos[1] = BITS*2 if second_row else BITS

    def draw_log(
        self, log: list[str], round_number: int, acting_character_name: str
    ) -> None:
        logview = LogView(self.font,[BITS*11, BITS],[BITS*19, BITS*9])
        logview.log = log
        logview.round_number=round_number
        logview.acting_character_name=acting_character_name
        logview.draw()


    def draw_map(self, valid_floor_coordinates: list[tuple[int, int]]) -> None:
        self.mapview.tile_width_px = self.canvas.tile_width_px
        self.mapview.tile_height_px = self.canvas.tile_height_px
        self.mapview.valid_map_coordinates = valid_floor_coordinates
        self.mapview.draw()

    def draw_sprite(self, x, y, sprite: Sprite, colkey=0, scale=1) -> None:
        self.mapview.draw_sprite(x,y,sprite, colkey, scale)

    def draw_sprites(self, entities: list[Entity]) -> None:
        """draws entity sprites with a notion of priority"""
        self.mapview.entities = entities
        self.mapview.draw_sprites()
        
