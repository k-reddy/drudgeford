import backend.models.character as character
from pyxel_ui.models.system_task import SystemTask
from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue
from pyxel_ui.models.action_task import ActionTask
from pyxel_ui.models.update_tasks import AddEntityTask, RemoveEntityTask, LoadCharactersTask, LoadLogTask, LoadActionCardsTask
import backend.models.obstacle as obstacle
from ..utils.listwithupdate import ListWithUpdate
from .action_model import ActionCard

CHAR_PRIORITY = 20
OTHER_PRIORITY = 10

class PyxelManager:
    def __init__(self, shared_action_queue: PyxelTaskQueue):
        self.shared_action_queue = shared_action_queue
        self.move_duration = 700


    def load_board(self, locations, terrain):
        entities = []
        # get all the coordinates on the map
        valid_floor_coordinates = self.generate_valid_floor_coordinates(locations)
        # there are sometimes full rows and columns of nothing - set offsets and remove those rows/cols
        self.set_x_y_offset(valid_floor_coordinates)
        valid_floor_coordinates = [self.normalize_coordinate(coordinate) for coordinate in valid_floor_coordinates]
        # get some board metadata that we'll need

        for row_num, row in enumerate(locations):
            for col_num, el in enumerate(row):
                if not el:
                    continue   
                if isinstance(el, obstacle.Wall):
                    continue     
                if isinstance(el, character.Character) or isinstance(el, obstacle.TerrainObject):
                    entities.append({
                        "id": el.id,
                        "position": self.normalize_coordinate((col_num, row_num)),
                        "name": el.pyxel_sprite_name,
                        "priority": CHAR_PRIORITY
                    })


        for row_num, row in enumerate(terrain):
            for col_num, el in enumerate(row):
                if not el:
                    continue
                if isinstance(el, obstacle.TerrainObject):
                    entities.append({
                        "id": el.id,
                        "position": self.normalize_coordinate((col_num, row_num)),
                        "name": el.pyxel_sprite_name,
                        "priority": OTHER_PRIORITY
                    })  

        payload = {
            "map_width": self.board_width,
            "map_height": self.board_height,
            "entities": entities,
            "valid_floor_coordinates": valid_floor_coordinates
        }
        # print(payload)
        task = SystemTask(type="board_init", payload=payload)
        self.shared_action_queue.enqueue(task)

    def move_character(self, char, old_location, new_location):
        direction = "DIR HOLDER"
        task = ActionTask(
            char.pyxel_sprite_name,
            char.id,
            "walk",
            direction,
            self.normalize_coordinate((old_location[1], old_location[0])),
            self.normalize_coordinate((new_location[1], new_location[0])),
            self.move_duration,            
        )
        self.shared_action_queue.enqueue(task)

    def add_entity(self, entity, row, col):
        if isinstance(entity, character.Character):
            priority = CHAR_PRIORITY
        else:
            priority = OTHER_PRIORITY

        task = AddEntityTask({"entities": [
                {
                    "id": entity.id,
                    "position": self.normalize_coordinate((col, row)),
                    "name": entity.pyxel_sprite_name,
                    "priority": priority
                }
            ]
            })
        self.shared_action_queue.enqueue(task)
    
    def remove_entity(self, entity_id):
        task = RemoveEntityTask(entity_id)
        self.shared_action_queue.enqueue(task)

    def set_x_y_offset(self, coordinates: list[tuple[int, int]]):
        min_x = min(x for x, y in coordinates)
        min_y = min(y for x, y in coordinates)
        max_y = max(y for x, y in coordinates)
        max_x = max(x for x, y in coordinates)
        self.x_offset = min_x
        self.y_offset = min_y
        self.board_height = max_y-min_y+1
        self.board_width = max_x-min_x+1

    def normalize_coordinate(self, coordinate: tuple[int, int]):
        return (coordinate[0] - self.x_offset, coordinate[1] - self.y_offset)
    
    def generate_valid_floor_coordinates(self, locations):
        valid_floor_coordinates = []
        for row_num, row in enumerate(locations):
            for col_num, el in enumerate(row):
                if not el:
                    valid_floor_coordinates.append((col_num, row_num))
                    continue
                if isinstance(el, obstacle.Wall):
                    continue         
                valid_floor_coordinates.append((col_num, row_num))
        return valid_floor_coordinates
    
    def load_characters(self, characters: list[character.Character]):
        healths = [character.health for character in characters]
        sprite_names = [character.pyxel_sprite_name for character in characters]
        teams = [character.team_monster for character in characters]
        task = LoadCharactersTask(healths, sprite_names, teams)
        self.shared_action_queue.enqueue(task)

    def load_log(self, log: ListWithUpdate):
        task = LoadLogTask(log)
        self.shared_action_queue.enqueue(task)

    def load_action_cards(self, action_cards):
        action_card_log= []
        for i,action_card in enumerate(action_cards):
            action_card_log.append(f"{i}: {action_card}")
        task = LoadActionCardsTask(action_card_log=action_card_log)
        self.shared_action_queue.enqueue(task)