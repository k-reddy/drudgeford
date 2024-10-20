from dataclasses import dataclass
from ..enums import AnimationFrame


@dataclass
class Character:
    """
    Represents a character in the game with its position, name, and animation state.

    Attributes:
        name (str): The name of the character.
        x (int): The x-coordinate of the character's position on the grid or canvas.
        y (int): The y-coordinate of the character's position on the grid or canvas.
        animation_frame (AnimationFrame): The current animation state of the character.
        alive (bool): Whether the character is alive (default is True).
    """

    name: str
    x: int
    y: int
    animation_frame: AnimationFrame
    alive: bool = True

    def update_position(self, x: int, y: int):
        """
        Updates the character's position on the canvas.

        Args:
            x (int): The new x-coordinate for the character.
            y (int): The new y-coordinate for the character.
        """
        self.x = x
        self.y = y
