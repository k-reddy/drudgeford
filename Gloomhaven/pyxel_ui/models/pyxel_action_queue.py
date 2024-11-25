from .pyxel_task_queue import PyxelTaskQueue
from .action import Action


class PyxelActionQueue(PyxelTaskQueue):
    """
    Specialized queue for handling user inputs or frontend-to-backend actions.
    """

    def enqueue(self, action: Action) -> None:
        # Enforce Action type for inputs
        if not isinstance(action, Action):
            raise TypeError("Only Action instances can be enqueued in ActionQueue.")
        super().enqueue(action)
