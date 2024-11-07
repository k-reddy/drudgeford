from collections import deque
from typing import Optional

from .tasks import Task, BoardInitTask

# all tasks are children of Task except BoardInitTask
task_type = Task | BoardInitTask

class PyxelTaskQueue:
    """
    Manages a queue of character actions, ensuring actions are processed in a
    first-in, first-out (FIFO) order.

    Attributes:
        queue (deque): A deque to efficiently store and retrieve actions.
    """

    def __init__(self):
        self.queue = deque()

    def enqueue(self, action: task_type) -> None:
        self.queue.append(action)

    def is_empty(self) -> bool:
        return not len(self.queue)

    def dequeue(self) -> task_type:
        if not self.is_empty():
            return self.queue.popleft()
        raise IndexError("Cannot pop from empty queue")

    def clear(self) -> None:
        self.queue.clear()

    def peek(self) -> Optional[task_type]:
        if self.is_empty():
            return None
        return self.queue[0]
