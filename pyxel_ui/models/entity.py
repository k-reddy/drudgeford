from dataclasses import dataclass
from ..enums import AnimationFrame


@dataclass
class Entity:
    """
    Represents a entity in the game with its position, name, and animation state.

    Attributes:
        name (str): The name of the entity.
        x (int): The x-coordinate of the entity's position on the grid or canvas.
        y (int): The y-coordinate of the entity's position on the grid or canvas.
        animation_frame (AnimationFrame): The current animation state of the entity.
        alive (bool): Whether the entity is alive (default is True).
    """

    id: int
    name: str
    x: int
    y: int
    z: int
    animation_frame: AnimationFrame
    # 0 upward, with higher priority number displaying on top
    priority: int
    alive: bool = True
    scale: int = 1
    # Degrees counter-clockwise
    rotation: int = 0

    def update_position(self, x: int, y: int) -> None:
        """
        Updates the entity's position on the canvas.

        Args:
            x (int): The new x-coordinate for the entity.
            y (int): The new y-coordinate for the entity.
        """
        self.x = x
        self.y = y

    def update_scale(self, scale: int) -> None:
        self.scale = scale

    def update_rotation(self, rotation: int) -> None:
        self.rotation = rotation
