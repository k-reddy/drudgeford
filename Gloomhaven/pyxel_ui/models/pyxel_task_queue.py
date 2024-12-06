from collections import deque
from typing import Optional
from .tasks import Task


class PyxelTaskQueue:
    """
    Manages a queue of game actions, ensuring actions are processed in a
    first-in, first-out (FIFO) order.

    Attributes:
        queue (deque): A deque to efficiently store and retrieve actions.
    """

    def __init__(self):
        self.queue = deque()

    def enqueue(self, action: Task) -> None:
        self.queue.append(action)

    def is_empty(self) -> bool:
        return not len(self.queue)

    def dequeue(self) -> Task:
        if not self.is_empty():
            return self.queue.popleft()
        raise IndexError("Cannot pop from empty queue")

    def clear(self) -> None:
        self.queue.clear()

    def peek(self) -> Optional[Task]:
        if self.is_empty():
            return None
        return self.queue[0]
