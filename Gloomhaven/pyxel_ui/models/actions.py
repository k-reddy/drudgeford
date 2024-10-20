from collections import deque
from dataclasses import dataclass
from typing import Optional

from ..enums import Direction


@dataclass
class Action:
    """
    Represents an action performed by a character in the game, including movement
    and animation details.

    Attributes:
        character (str): The name of the character performing the action.
        animation_type (str): The type of animation for the action (e.g., 'walk', 'attack').
        direction (Direction): The direction of movement.
        from_grid_pos (tuple): The starting position on the grid (x, y).
        to_grid_pos (tuple): The target position on the grid (x, y).
        duration_ms (int): The duration of the action in milliseconds (default is 1000 ms).
        action_steps (Optional[deque[tuple[int, int]]]): A sequence of pixel positions
            representing the path of the action (optional).
    """

    character: str
    animation_type: str
    direction: Direction
    from_grid_pos: tuple
    to_grid_pos: tuple
    duration_ms: int = 1000
    action_steps: Optional[deque[tuple[int, int]]] = None


class PyxelActionQueue:
    """
    Manages a queue of character actions, ensuring actions are processed in a
    first-in, first-out (FIFO) order.

    Attributes:
        queue (deque): A deque to efficiently store and retrieve actions.
    """

    def __init__(self):
        self.queue = deque()

    def enqueue(self, action: Action) -> None:
        self.queue.append(action)

    def is_empty(self) -> bool:
        return not len(self.queue)

    def dequeue(self) -> Action:
        if not self.is_empty():
            return self.queue.popleft()
        raise IndexError("Cannot pop from empty queue")

    def clear(self) -> None:
        self.queue.clear()

    def peek(self) -> Optional[Action]:
        if self.is_empty():
            return None
        return self.queue[0]
