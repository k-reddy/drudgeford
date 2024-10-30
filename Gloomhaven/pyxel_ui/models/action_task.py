from collections import deque
from dataclasses import dataclass
from typing import Optional

from ..enums import Direction


@dataclass
class ActionTask:
    """
    Represents an action performed by a sprite in the game, including movement
    and animation details.

    Attributes:
        sprite (str): The name of the sprite performing the action.
        animation_type (str): The type of animation for the action (e.g., 'walk', 'attack').
        direction (Direction): The direction of movement.
        from_grid_pos (tuple): The starting position on the grid (x, y).
        to_grid_pos (tuple): The target position on the grid (x, y).
        duration_ms (int): The duration of the action in milliseconds (default is 1000 ms).
        action_steps (Optional[deque[tuple[int, int]]]): A sequence of pixel positions
            representing the path of the action (optional).
    """

    sprite: str
    animation_type: str
    direction: Direction
    from_grid_pos: tuple
    to_grid_pos: tuple
    duration_ms: int = 1000
    action_steps: Optional[deque[tuple[int, int]]] = None
