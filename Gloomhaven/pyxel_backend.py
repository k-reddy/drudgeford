import character
from pyxel_ui.models.system_task import SystemTask
from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue
from pyxel_ui.models.action_task import ActionTask
from pyxel_ui.models.update_tasks import AddEntityTask, RemoveEntityTask
import obstacle


class PyxelManager:
    def __init__(self, shared_action_queue: PyxelTaskQueue):
        self.shared_action_queue = shared_action_queue
        self.move_duration = 700


    def load_board(self, locations, terrain):
        # get some board metadata that we'll need
        board_width = len(locations)
        board_height = len(locations[0])

        entities = []
        valid_floor_coordinates = []
        for row_num, row in enumerate(locations):
            for col_num, el in enumerate(row):
                if not el:
                    valid_floor_coordinates.append((col_num, row_num))
                    continue
                if isinstance(el, obstacle.Wall):
                    continue         
                if isinstance(el, character.Character) or isinstance(el, obstacle.TerrainObject):
                    entities.append({
                        "id": el.id,
                        "position": (col_num, row_num),
                        "name": el.pyxel_sprite_name,
                        "priority": 10
                    })
                valid_floor_coordinates.append((col_num, row_num))


        for row_num, row in enumerate(terrain):
            for col_num, el in enumerate(row):
                if not el:
                    continue
                if isinstance(el, obstacle.TerrainObject):
                    entities.append({
                        "id": el.id,
                        "position": (col_num, row_num),
                        "name": el.pyxel_sprite_name,
                        "priority": 5
                    })  
                      
        payload = {
            "map_width": board_width,
            "map_height": board_height,
            "entities": entities,
            "valid_floor_coordinates": valid_floor_coordinates
        }
        # print(payload)
        task = SystemTask(type="board_init", payload=payload)
        self.shared_action_queue.enqueue(task)

    def move_character(self, char, old_location, new_location):
        direction = "DIR HOLDER"
        task = ActionTask(
            "knight",
            char.id,
            "walk",
            direction,
            (old_location[1], old_location[0]),
            (new_location[1], new_location[0]),
            self.move_duration,            
        )
        self.shared_action_queue.enqueue(task)

    def add_entity(self, entity, row, col):
        task = AddEntityTask({"entities": [
                {
                    "id": entity.id,
                    "position": (col, row),
                    "name": entity.pyxel_sprite_name,
                    "priority": 20
                }
            ]
            })
        self.shared_action_queue.enqueue(task)
    
    def remove_entity(self, entity_id):
        task = RemoveEntityTask(entity_id)
        self.shared_action_queue.enqueue(task)
