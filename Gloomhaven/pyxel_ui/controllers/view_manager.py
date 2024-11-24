import pyxel

from typing import Optional

from pyxel_ui.constants import (
    BITS,
    FONT_PATH,
)
from pyxel_ui.models.font import PixelFont
from pyxel_ui.views.sprite import SpriteManager
from pyxel_ui.models import view_section as view


class ViewManager:
    def __init__(
        self, pyxel_width, pyxel_height, floor_color_map=[], wall_color_map=[]
    ):
        self.view_border = 10
        self.sprite_manager = SpriteManager()
        self.font = PixelFont(pyxel, f"../{FONT_PATH}")
        self.canvas_width = pyxel_width
        self.canvas_height = pyxel_height
        self.initiative_bar_view = view.InitiativeBarView(
            self.font,
            start_pos=[self.view_border, self.view_border // 4],
            bounding_coordinate=[BITS * 11, BITS],
        )
        self.map_view = view.MapView(
            self.font,
            [
                self.initiative_bar_view.start_pos[0],
                self.initiative_bar_view.bounding_coordinate[1] + self.view_border,
            ],
            [
                self.initiative_bar_view.bounding_coordinate[0],
                BITS * 11 + self.view_border * 2,
            ],
            floor_color_map=floor_color_map,
            wall_color_map=wall_color_map,
        )
        self.log_view = view.LogView(
            self.font,
            [
                self.initiative_bar_view.bounding_coordinate[0],
                self.initiative_bar_view.start_pos[1],
            ],
            [
                self.canvas_width,
                self.map_view.bounding_coordinate[1] + self.view_border,
            ],
        )
        self.action_card_view = view.ActionCardView(
            self.font,
            [
                self.map_view.start_pos[0],
                self.map_view.bounding_coordinate[1] + self.view_border,
            ],
            [self.canvas_width, self.canvas_height],
        )
        self.views = [
            self.initiative_bar_view,
            self.map_view,
            self.log_view,
            self.action_card_view,
        ]

    def update_log(self, log: list[str]):
        # note: drawable set in update_round_turn()
        self.log_view.log = log
        self.log_view.draw()

    def update_round_turn(self, round_number: int, acting_character_name: str):
        self.log_view.round_number = round_number
        self.log_view.acting_character_name = acting_character_name
        if round_number > 0 and acting_character_name:
            self.log_view.drawable = True
        else:
            self.log_view.drawable = False
        self.log_view.draw()

    def update_initiative_bar(
        self, sprite_names: list[str], healths: list[int], teams: list[bool]
    ):
        self.initiative_bar_view.sprite_names = sprite_names
        self.initiative_bar_view.healths = healths
        self.initiative_bar_view.teams = teams
        if sprite_names:
            self.initiative_bar_view.drawable = True
        else:
            self.initiative_bar_view.drawable = False
        self.initiative_bar_view.draw()

    def update_action_card_log(self, action_card_log: list[str]):
        # reset the card page to 0 every time we load new action cards
        self.action_card_view.current_card_page = 0
        self.action_card_view.items = action_card_log
        if action_card_log:
            self.action_card_view.drawable = True
        else:
            self.action_card_view.drawable = False
        self.action_card_view.draw()

    def update_map(
        self,
        valid_floor_coordinates: list[tuple[int, int]],
        floor_color_map=[],
        wall_color_map=[],
    ) -> None:
        if valid_floor_coordinates:
            self.map_view.drawable = True
        else:
            self.map_view.drawable = False

        if floor_color_map:
            self.map_view.floor_color_map = floor_color_map
        if wall_color_map:
            self.map_view.wall_color_map = wall_color_map
        self.map_view.valid_map_coordinates = valid_floor_coordinates
        self.map_view.draw()
        self.map_view.draw_sprites()

    def update_sprites(self, entities: dict) -> None:
        """draws entity sprites with a notion of priority"""
        self.map_view.entities = entities
        self.map_view.draw()

    def remove_entity(self, entity_id: int) -> None:
        try:
            del self.map_view.entities[entity_id]
        except Exception as e:
            print(f"attempting to delete non-existent entity: {str(e)}")
            raise
        self.map_view.draw()

    def convert_grid_to_pixel_pos(self, tile_x: int, tile_y: int) -> tuple[int, int]:
        """Converts grid-based tile coordinates to pixel coordinates on the map."""
        return self.map_view.convert_grid_to_pixel_pos(tile_x, tile_y)

    def get_view_for_coordinate_px(
        self,
        px_x: int,
        px_y: int,
    ) -> Optional[view.ViewSection]:
        return next(
            (
                curr_view
                for curr_view in self.views
                if curr_view.start_pos[0] <= px_x < curr_view.end_pos[0]
                and curr_view.start_pos[1] <= px_y < curr_view.end_pos[1]
            ),
            None,
        )

    def draw_grid(self, px_x: int, px_y: int, px_width: int, px_height: int) -> None:
        view.draw_grid(px_x, px_y, px_width, px_height)

    def draw_whole_game(self):
        self.initiative_bar_view.draw()
        self.map_view.draw()
        self.log_view.draw()
        self.action_card_view.draw()

    def handle_btn_press(self, btn):
        if btn == pyxel.KEY_RIGHT:
            self.action_card_view.go_to_next_page()
        elif btn == pyxel.KEY_LEFT:
            self.action_card_view.go_to_prev_page()

    def clear_screen(self):
        pass
