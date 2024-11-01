import character
from pyxel_ui.models.system_task import SystemTask
from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue


class PyxelManager:
    def __init__(self, shared_action_queue: PyxelTaskQueue):
        self.shared_action_queue = shared_action_queue

    def load_board(self, locations):
        # get some board metadata that we'll need
        board_width = len(locations)
        board_height = len(locations[0])

        entities = []
        for row_num, row in enumerate(locations):
            for col_num, el in enumerate(row):
                if not el:
                    continue
                if isinstance(el, character.Character):
                    entities.append({
                        "id": el.id,
                        "position": (col_num, row_num),
                        # "name": type(el).__name__
                        "name": "knight"
                    })
        
        payload = {
            "map_width": board_width,
            "map_height": board_height,
            "entities": entities
        }
        print(payload)
        task = SystemTask(type="board_init", payload=payload)
        self.shared_action_queue.enqueue(task)


    # def main() -> None:
    #     # Create the PyxelView instance with the shared queue
    #     pyxel_view = PyxelView(SHARED_ACTION_QUEUE)

    #     # Start the thread that enqueues actions
    #     threading.Thread(target=test_load_board).start()
    #     # enqueue_actions()
    #     # Start the Pyxel game loop (on the main thread)
    #     pyxel_view.start()

    # if __name__ == "__main__":
    #     main()