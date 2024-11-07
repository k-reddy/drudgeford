import pyxel

from pyxel_ui.constants import (
    BITS,
    FONT_PATH,
)
from pyxel_ui.models.entity import Entity
from pyxel_ui.models.font import PixelFont
from pyxel_ui.views.sprite import Sprite, SpriteManager
from pyxel_ui.models import view_section as view

class ViewManager:
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
        
    def update_log(
            self, 
            log: list[str]):
        self.log_view.log = log

    def update_round_turn(self, round_number: int, acting_character_name: str):
        self.log_view.round_number = round_number
        self.log_view.acting_character_name = acting_character_name

    def update_initiative_bar(self, sprite_names: list[str], healths: list[int], teams: list[bool]):
        self.initiative_bar_view.sprite_names = sprite_names
        self.initiative_bar_view.healths = healths
        self.initiative_bar_view.teams = teams

    def update_action_card_log(self, action_card_log: list[str]):
        self.action_card_view.action_card_log = action_card_log