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