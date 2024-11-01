import threading
from typing import Optional, List
from pyxel_ui.pyxel_main import PyxelView
from pyxel_ui.models.action_task import ActionTask
from pyxel_ui.models.system_task import SystemTask
from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue
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

shared_action_queue = PyxelTaskQueue()
board_width_tiles = 6
board_height_tiles = 5
move_duration = 700


def enqueue_actions():
    """Simulate external enqueueing of actions asynchronously."""
    import time
    # test_map: List[List[Optional[str]]] = [
    #     [None for _ in range(board_width_tiles)] for _ in range(board_height_tiles)
    # ]
    # row_px, col_px = self.convert_grid_to_pixel_pos(
    #     self.current_task.payload.start_position[0],
    #     self.current_task.payload.start_position[1],
    # )

    # self.characters[self.current_task.payload.id] = Character(
    #     name="knight",
    #     x=row_px,
    #     y=col_px,
    #     z=10,
    #     animation_frame=AnimationFrame.SOUTH,
    #     alive=True,
    # )
    time.sleep(3)
    print("Enqueuing actions...")
    payload = {
        "map_width": 10,
        "map_height": 10,
        "entities": [
            {
                "id": 1,
                "position": (0, 0),
                "name": "skeleton",
                "priority": 0
            },
            {
                "id": 3,
                "position": (3, 2),
                "name": "spores",
                "priority": 1
            },
            {
                "id": 2,
                "position": (3, 2),
                "name": "wizard",
                "priority": 10
            },
            {
                "id": 4,
                "position": (3, 2),
                "name": "fire",
                "priority": 0
            },

        ],
    }

    task = SystemTask(type="board_init", payload=payload)
    shared_action_queue.enqueue(task)

    # Create some test actions
    time.sleep(7)
    print("move 1")
    shared_action_queue.enqueue(
        ActionTask("knight", 1, "walk", Direction.EAST, (0, 0), (1, 0), move_duration)
    )
    shared_action_queue.enqueue(
        ActionTask("knight", 1, "walk", Direction.EAST, (1, 0), (1, 1), move_duration)
    )
    time.sleep(2)

    print("move2")
    shared_action_queue.enqueue(
        ActionTask(
            "knight",
            2,
            "walk",
            Direction.EAST,
            (3, 2),
            (3, 3),
        )
    )
    shared_action_queue.enqueue(
        ActionTask("knight", 2, "walk", Direction.EAST, (3, 3), (2, 2), move_duration)
    )
    shared_action_queue.enqueue(
        ActionTask("knight", 2, "walk", Direction.EAST, (2, 2), (1, 2), move_duration)
    )
    # time.sleep(3)
    # print("move3")
    # shared_action_queue.enqueue(
    #     ActionTask("knight", 1, "walk", Direction.EAST, (1, 2), (1, 3), move_duration)
    # )
    # shared_action_queue.enqueue(
    #     ActionTask("knight", 1, "walk", Direction.EAST, (1, 3), (2, 4), move_duration)
    # )
    # shared_action_queue.enqueue(
    #     ActionTask("knight", 1, "walk", Direction.EAST, (2, 4), (2, 3), move_duration)
    # )

    print("ActionTasks enqueued successfully.")
    print("yaaaay")


def main() -> None:
    # Create the PyxelView instance with the shared queue
    pyxel_view = PyxelView(shared_action_queue)

    # Start the thread that enqueues actions
    threading.Thread(target=enqueue_actions).start()
    # enqueue_actions()
    # Start the Pyxel game loop (on the main thread)
    pyxel_view.start()


# Run the main function
if __name__ == "__main__":
    main()
