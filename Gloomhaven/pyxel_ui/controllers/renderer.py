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
    def __init__(self, canvas):
        self.view_border = 10
        self.canvas = canvas
        self.sprite_manager = SpriteManager()
        self.font = PixelFont(pyxel, f"../{FONT_PATH}")
        self.map_view = view.MapView(
            self.font, 
            self.canvas.board_start_pos,
            [BITS*10, BITS*11]
            )
        # !!! eventually, we should reset these to get the end pos of the
        # other view and add the border, but we don't set end positions right now
        self.action_card_view = view.ActionCardView(
            self.font,
            [self.view_border, BITS*11+self.view_border],
            [pyxel.width, pyxel.height]
            )
        self.initiative_bar_view = view.InitiativeBarView(
            self.font, 
            start_pos=[0,self.view_border], 
            bounding_coordinate=[BITS*10, BITS]
        )
        self.log_view = view.LogView(
            self.font,
            [BITS*11, self.view_border],
            [pyxel.width, BITS*11])

    # Card related methods grouped together
    def draw_action_cards(
        self, action_card_log, current_card_page, cards_per_page
    ) -> None:
        self.action_card_view.action_card_log = action_card_log
        self.action_card_view.current_card_page=current_card_page
        self.action_card_view.cards_per_page=cards_per_page
        self.action_card_view.draw()

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
        self.initiative_bar_view.sprite_names=sprite_names
        self.initiative_bar_view.healths=healths
        self.initiative_bar_view.teams=teams
        self.initiative_bar_view.draw()

    def draw_log(
        self, log: list[str], round_number: int, acting_character_name: str
    ) -> None:
        self.log_view.log = log
        self.log_view.round_number=round_number
        self.log_view.acting_character_name=acting_character_name
        self.log_view.draw()

    def draw_map(self, valid_floor_coordinates: list[tuple[int, int]]) -> None:
        self.map_view.tile_width_px = self.canvas.tile_width_px
        self.map_view.tile_height_px = self.canvas.tile_height_px
        self.map_view.valid_map_coordinates = valid_floor_coordinates
        self.map_view.draw()

    def draw_sprite(self, x, y, sprite: Sprite, colkey=0, scale=1) -> None:
        view.draw_sprite(x,y,sprite, colkey, scale)

    def draw_sprites(self, entities: list[Entity]) -> None:
        """draws entity sprites with a notion of priority"""
        self.map_view.entities = entities
        self.map_view.draw_sprites()
        
