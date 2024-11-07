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
from pyxel_ui.views.sprite import Sprite, SpriteManager
from pyxel_ui.models import view_section as view

class Renderer:
    def __init__(self, view_manager):
        self.view_manager = view_manager

    # Card related methods grouped together
    def draw_action_cards(
        self, action_card_log, current_card_page, cards_per_page
    ) -> None:
        self.view_manager.action_card_view.action_card_log = action_card_log
        self.view_manager.action_card_view.current_card_page=current_card_page
        self.view_manager.action_card_view.cards_per_page=cards_per_page
        self.view_manager.action_card_view.draw()

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
        self.view_manager.initiative_bar_view.sprite_names=sprite_names
        self.view_manager.initiative_bar_view.healths=healths
        self.view_manager.initiative_bar_view.teams=teams
        self.view_manager.initiative_bar_view.draw()

    def draw_log(
        self, log: list[str], round_number: int, acting_character_name: str
    ) -> None:
        self.view_manager.log_view.log = log
        self.view_manager.log_view.round_number=round_number
        self.view_manager.log_view.acting_character_name=acting_character_name
        self.view_manager.log_view.draw()

    def draw_map(self, valid_floor_coordinates: list[tuple[int, int]]) -> None:
        self.view_manager.map_view.tile_width_px = self.view_manager.canvas.tile_width_px
        self.view_manager.map_view.tile_height_px = self.view_manager.canvas.tile_height_px
        self.view_manager.map_view.valid_map_coordinates = valid_floor_coordinates
        self.view_manager.map_view.draw()

    def draw_sprite(self, x, y, sprite: Sprite, colkey=0, scale=1) -> None:
        view.draw_sprite(x,y,sprite, colkey, scale)

    def draw_sprites(self, entities: list[Entity]) -> None:
        """draws entity sprites with a notion of priority"""
        self.view_manager.map_view.entities = entities
        self.view_manager.map_view.draw_sprites()
        
