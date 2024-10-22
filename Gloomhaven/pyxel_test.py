import threading
from typing import Optional, List
from pyxel_ui.pyxel_main import PyxelView
from pyxel_ui.models.actions import Action, PyxelActionQueue
from pyxel_ui.enums import Direction

"""
average frame time = 0.0343 sec
colors (for aseprite use)
0,0,0 this is transparency
43,51,95
126,32,114
25,149,156
139,72,82
57,92,152
169,193,255


238,238,238 sucks


212,24,108
211,132,65
233,195,91
112,198,169
118,150,222
163,163,163
255,151,152
237,199,176

"""

shared_action_queue = PyxelActionQueue()
board_width_tiles = 6
board_height_tiles = 5
move_duration = 700


def enqueue_actions():
    """Simulate external enqueueing of actions asynchronously."""
    import time

    time.sleep(1)
    print("Enqueuing actions...")

    # Create some test actions
    print("move 1")
    shared_action_queue.enqueue(
        Action("knight", "walk", Direction.EAST, (0, 0), (1, 0), move_duration)
    )
    shared_action_queue.enqueue(
        Action("knight", "walk", Direction.EAST, (1, 0), (1, 1), move_duration)
    )
    time.sleep(2)
    print("move2")
    shared_action_queue.enqueue(
        Action("knight", "walk", Direction.EAST, (1, 1), (1, 2), move_duration)
    )
    shared_action_queue.enqueue(
        Action("knight", "walk", Direction.EAST, (1, 2), (2, 2), move_duration)
    )
    shared_action_queue.enqueue(
        Action("knight", "walk", Direction.EAST, (2, 2), (1, 2), move_duration)
    )
    time.sleep(3)
    print("move3")
    shared_action_queue.enqueue(
        Action("knight", "walk", Direction.EAST, (1, 2), (1, 3), move_duration)
    )
    shared_action_queue.enqueue(
        Action("knight", "walk", Direction.EAST, (1, 3), (2, 4), move_duration)
    )
    shared_action_queue.enqueue(
        Action("knight", "walk", Direction.EAST, (2, 4), (2, 3), move_duration)
    )

    print("Actions enqueued successfully.")
    print("yaaaay")


def main() -> None:
    # Create the PyxelView instance with the shared queue
    test_map: List[List[Optional[str]]] = [
        [None for _ in range(board_width_tiles)] for _ in range(board_height_tiles)
    ]
    pyxel_view = PyxelView(test_map, shared_action_queue)

    # Start the thread that enqueues actions
    threading.Thread(target=enqueue_actions).start()

    # Start the Pyxel game loop (on the main thread)
    pyxel_view.start()


# Run the main function
if __name__ == "__main__":
    main()
