import pyxel

from pyxel_ui.constants import (
    BITS,
    FONT_PATH,
)
from pyxel_ui.models.font import PixelFont
from pyxel_ui.views.sprite import SpriteManager
from pyxel_ui.models import view_section as view


class CharacterPickerViewManager:

    def __init__(self, pyxel_width, pyxel_height):
        self.sprite_manager = SpriteManager()
        self.font = PixelFont(pyxel, f"../{FONT_PATH}")
        self.canvas_width = pyxel_width
        self.canvas_height = pyxel_height

        self.character_sprite = view.SpriteView(
            self.font, [0, 0], [self.canvas_width, self.canvas_height]
        )
        self.character_sprite.draw()
        self.views = []
