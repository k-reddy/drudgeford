import threading
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Add parent directory to path
from pyxel_ui.engine import PyxelEngine
from pyxel_ui.models import tasks
from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue

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
move_duration = 700
test_map=False
test_other_areas = True
width = 6
height = 8

def enqueue_actions():
    """Simulate external enqueueing of actions asynchronously."""
    import time

    valid_floor_coordinates = []
    for x in range(0, width):
        for y in range(0, height):
            valid_floor_coordinates.append((x, y))
    board_load_task = tasks.BoardInitTask(map_height=10, map_width=10,
                                        valid_map_coordinates=valid_floor_coordinates)
    shared_action_queue.enqueue(board_load_task)
    entities = [
            {"id": 1, "position": (0, 0), "name": "skeleton", "priority": 10},
            {"id": 3, "position": (4, 2), "name": "necromancer", "priority": 10},
            {"id": 2, "position": (3, 2), "name": "wizard", "priority": 10},
            {"id": 4, "position": (4, 4), "name": "fire", "priority": 0},
        ]
    shared_action_queue.enqueue(tasks.AddEntitiesTask(entities=entities))
    
    if test_map:
        print("Enqueuing actions...")
        # Create some test actions
        print("move 1: skele 0,0 to 1,0 to 1,1")
        shared_action_queue.enqueue(
            tasks.ActionTask(1, (0, 0), (1, 0), move_duration)
        )
        shared_action_queue.enqueue(
            tasks.ActionTask(1, (1, 0), (1, 1), move_duration)
        )
        time.sleep(4)

        print("move2 wizard 3,2 to 3,3")
        shared_action_queue.enqueue(
            tasks.ActionTask(2, (3, 2), (3, 3), move_duration)
        )
        
        time.sleep(4)
        print("remove wizard")
        shared_action_queue.enqueue(tasks.RemoveEntityTask(2))
        print("add miner")
        shared_action_queue.enqueue(tasks.AddEntitiesTask([
                        {"id": 5, "position": (4, 6), "name": "miner", "priority": 10}
                    ]))

        print("ActionTasks enqueued successfully.")
        print("yaaaay")

    if test_other_areas:
        # Non-map tests
        task = tasks.LoadActionCardsTask(["some cool test cards\nhi\notherhi",
                                        "some cool test cards\nhi\notherhi",
                                        "some cool test cards\nhi\notherhi",
                                        "pg2 WOAH\nhi\notherhi"])
        shared_action_queue.enqueue(task)

        task = tasks.LoadCharactersTask([2,2,2], ["skeleton","wizard","necromancer"],[True, False, False])
        shared_action_queue.enqueue(task)

        task = tasks.LoadRoundTurnInfoTask(2,"sally")
        shared_action_queue.enqueue(task)

        task = tasks.LoadLogTask(["what's up i'm a log","it's so cool to log"])
        shared_action_queue.enqueue(task)

        time.sleep(3)
        task = tasks.LoadRoundTurnInfoTask(3,"not sally")
        shared_action_queue.enqueue(task)

        task = tasks.LoadLogTask(["new log heyyyy","it's STILL so cool to log"])
        shared_action_queue.enqueue(task)

        time.sleep(2)
        
        task = tasks.LoadLogTask(["uh oh a death"])
        shared_action_queue.enqueue(task)
        shared_action_queue.enqueue(tasks.RemoveEntityTask(3))
        task = tasks.LoadCharactersTask([2,2], ["skeleton","wizard",],[True, False])
        shared_action_queue.enqueue(task)
        


def main() -> None:
    # Create the PyxelEngine instance with the shared queue
    pyxel_view = PyxelEngine(shared_action_queue)

    # Start the thread that enqueues actions
    threading.Thread(target=enqueue_actions).start()
    # enqueue_actions()
    # Start the Pyxel game loop (on the main thread)
    pyxel_view.start()


# Run the main function
if __name__ == "__main__":
    main()
