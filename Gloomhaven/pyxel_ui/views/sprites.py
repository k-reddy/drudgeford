from dataclasses import dataclass
from ..enums import AnimationFrame


@dataclass
class Sprite:
    """
    Represents a sprite with its location and dimensions on a sprite sheet.

    Attributes:
        img_bank (int): The index of the sprite sheet (or image bank) the sprite is stored in.
        u (int): The x-coordinate of the sprite within the sprite sheet.
        v (int): The y-coordinate of the sprite within the sprite sheet.
        w (int): The width of the sprite.
        h (int): The height of the sprite.
    """

    img_bank: int
    u: int
    v: int
    w: int
    h: int


class SpriteManager:
    """
    Manages all the sprites used in the game, allowing for easy retrieval by name and animation frame.

    Attributes:
        sprites (dict): A dictionary mapping character names and animation frames to Sprite objects.
    """

    def __init__(self):
        """
        Initializes the SpriteManager with predefined sprites.
        """
        self.sprites = {
            "knight": {
                AnimationFrame.SOUTH: Sprite(img_bank=0, u=0, v=0, w=64, h=64),
            },
        }

    def get_sprite(self, name, frame):
        """
        Retrieves a specific sprite based on character name and animation frame.

        Args:
            name (str): The name of the character.
            frame (AnimationFrame): The animation frame associated with the sprite.

        Returns:
            Sprite: The sprite object corresponding to the provided name and frame.
        """
        return self.sprites[name][frame]
