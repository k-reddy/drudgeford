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
        print(f"{FONT_PATH=}")
        self.canvas = canvas
        self.sprite_manager = SpriteManager()
        self.font = PixelFont(pyxel, f"../{FONT_PATH}")
        self.mapview = view.MapView(
            self.font, 
            self.canvas.board_start_pos,
            [BITS*10, BITS*10]
            )

    # Card related methods grouped together
    def draw_action_cards(
        self, action_card_log, current_card_page, cards_per_page
    ) -> None:
        actioncardview = view.ActionCardView(
            self.font,
            [0, BITS*10],
            [BITS*20, BITS*20]
        )
        actioncardview.action_card_log = action_card_log
        actioncardview.current_card_page=current_card_page
        actioncardview.cards_per_page=cards_per_page
        actioncardview.draw()

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
        initiativebarview = view.InitiativeBarView(self.font, start_pos=[0,0], bounding_coordinate=[BITS*12, BITS*3])
        initiativebarview.sprite_names=sprite_names
        initiativebarview.healths=healths
        initiativebarview.teams=teams
        initiativebarview.draw()

    def draw_log(
        self, log: list[str], round_number: int, acting_character_name: str
    ) -> None:
        logview = view.LogView(self.font,[BITS*11, BITS],[BITS*19, BITS*9])
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
        view.draw_sprite(x,y,sprite, colkey, scale)

    def draw_sprites(self, entities: list[Entity]) -> None:
        """draws entity sprites with a notion of priority"""
        self.mapview.entities = entities
        self.mapview.draw_sprites()
        
