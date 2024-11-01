import threading
import character
from pyxel_ui.models.system_task import SystemTask
from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue
from pyxel_ui.pyxel_main import PyxelView
from itertools import count


SHARED_ACTION_QUEUE = PyxelTaskQueue()

def test_load_board():
    locations = [["x","x","KNIGHT"]]
    load_board(locations)

def load_board(locations):
    # get some board metadata that we'll need
    board_height = len(locations)
    board_width = len(locations[0])
    id_generator = count(start=1)

    entities = {}
    for row_num, row in enumerate(locations):
        for col_num, el in enumerate(row):
            if not el:
                continue
            if el == "KNIGHT":
            # if isinstance(el, character.Character):
                entities["id"] = {
                    # "id": el.id,
                    "id": 1,
                    "position": (row_num, col_num),
                    # "name": type(el).__name__
                    "name": "knight"
                }
     
    payload = {
        "map_width": board_width,
        "map_height": board_height,
        "entities": entities
    }

    task = SystemTask(type="board_init", payload=payload)
    SHARED_ACTION_QUEUE.enqueue(task)


def main() -> None:
    # Create the PyxelView instance with the shared queue
    pyxel_view = PyxelView(SHARED_ACTION_QUEUE)

    # Start the thread that enqueues actions
    threading.Thread(target=test_load_board).start()
    # enqueue_actions()
    # Start the Pyxel game loop (on the main thread)
    pyxel_view.start()

if __name__ == "__main__":
    main()