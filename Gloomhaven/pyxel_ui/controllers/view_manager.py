import pyxel

from pyxel_ui.constants import (
    BITS,
    FONT_PATH,
)
from pyxel_ui.models.font import PixelFont
from pyxel_ui.views.sprite import SpriteManager
from pyxel_ui.models import view_section as view

class ViewManager:
    def __init__(self, pyxel_width, pyxel_height):
        self.view_border = 10
        self.sprite_manager = SpriteManager()
        self.font = PixelFont(pyxel, f"../{FONT_PATH}")
        self.canvas_width = pyxel_width
        self.canvas_height = pyxel_height
        self.map_view = view.MapView(
            self.font, 
            [self.view_border, BITS+self.view_border*2],
            [self.canvas_width, self.canvas_height]
            )
        # !!! eventually, we should reset these to get the end pos of the
        # other view and add the border, but we don't set end positions right now
        self.action_card_view = view.ActionCardView(
            self.font,
            [self.view_border, BITS*11+self.view_border*4],
            [self.canvas_width, self.canvas_height]
            )
        self.initiative_bar_view = view.InitiativeBarView(
            self.font, 
            start_pos=[0,self.view_border], 
            bounding_coordinate=[BITS*11, BITS]
        )
        self.log_view = view.LogView(
            self.font,
            [BITS*11, self.view_border],
            [self.canvas_width, self.canvas_height]
        )        
    def update_log(
            self, 
            log: list[str]):
        self.log_view.log = log
        self.log_view.draw()

    def update_round_turn(self, round_number: int, acting_character_name: str):
        self.log_view.round_number = round_number
        self.log_view.acting_character_name = acting_character_name
        self.log_view.draw()

    def update_initiative_bar(self, sprite_names: list[str], healths: list[int], teams: list[bool]):
        self.initiative_bar_view.sprite_names = sprite_names
        self.initiative_bar_view.healths = healths
        self.initiative_bar_view.teams = teams
        self.initiative_bar_view.draw()

    def update_action_card_log(self, action_card_log: list[str]):
        self.action_card_view.action_card_log = action_card_log
        self.action_card_view.draw()

    def update_map(self, valid_floor_coordinates: list[tuple[int, int]]) -> None:
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