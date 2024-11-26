import backend.models.character as character
from pyxel_ui.models import tasks
import backend.models.obstacle as obstacle
from ..utils.listwithupdate import ListWithUpdate
from server.tcp_client import TCPClient, ClientType
from server.task_jsonifier import TaskJsonifier

CHAR_PRIORITY = 20
OTHER_PRIORITY = 10


class PyxelManager:
    def __init__(self, port):
        self.move_duration = 700
        self.log = ListWithUpdate([], self.load_log)
        self.floor_color_map = []
        self.wall_color_map = []
        self.tj = TaskJsonifier()
        self.server_client = TCPClient(ClientType.BACKEND, port=port)

    def load_board(self, locations, terrain):
        entities = []
        # get all the coordinates on the map
        valid_map_coordinates = self.generate_valid_map_coordinates(locations)
        # there are sometimes full rows and columns of nothing - set offsets and remove those rows/cols
        self.set_x_y_offset(valid_map_coordinates)
        valid_map_coordinates = [
            self.normalize_coordinate(coordinate)
            for coordinate in valid_map_coordinates
        ]
        # get some board metadata that we'll need

        for row_num, row in enumerate(locations):
            for col_num, el in enumerate(row):
                if not el:
                    continue
                if isinstance(el, obstacle.Wall):
                    continue
                if isinstance(el, character.Character) or isinstance(
                    el, obstacle.TerrainObject
                ):
                    entities.append(
                        {
                            "id": el.id,
                            "position": self.normalize_coordinate((col_num, row_num)),
                            "name": el.pyxel_sprite_name,
                            "priority": CHAR_PRIORITY,
                        }
                    )

        for row_num, row in enumerate(terrain):
            for col_num, el in enumerate(row):
                if not el:
                    continue
                if isinstance(el, obstacle.TerrainObject):
                    entities.append(
                        {
                            "id": el.id,
                            "position": self.normalize_coordinate((col_num, row_num)),
                            "name": el.pyxel_sprite_name,
                            "priority": OTHER_PRIORITY,
                        }
                    )
        tasks_to_send = []
        tasks_to_send.append(
            tasks.BoardInitTask(
                map_height=self.board_height,
                map_width=self.board_width,
                valid_map_coordinates=valid_map_coordinates,
                floor_color_map=self.floor_color_map,
                wall_color_map=self.wall_color_map,
            )
        )
        tasks_to_send.append(tasks.AddEntitiesTask(entities=entities))
        for task in tasks_to_send:
            self.jsonify_and_send_task(task)

    def clear_log(self):
        self.log = ListWithUpdate([], self.load_log)
        self.load_log(self.log)

    def move_character(self, char, old_location, new_location):
        task = tasks.ActionTask(
            char.id,
            self.normalize_coordinate((old_location[1], old_location[0])),
            self.normalize_coordinate((new_location[1], new_location[0])),
            self.move_duration,
        )
        self.jsonify_and_send_task(task)

    def add_entity(self, entity, row, col):
        if isinstance(entity, character.Character):
            priority = CHAR_PRIORITY
        else:
            priority = OTHER_PRIORITY

        task = tasks.AddEntitiesTask(
            entities=[
                {
                    "id": entity.id,
                    "position": self.normalize_coordinate((col, row)),
                    "name": entity.pyxel_sprite_name,
                    "priority": priority,
                }
            ]
        )
        self.jsonify_and_send_task(task)

    def remove_entity(self, entity_id):
        task = tasks.RemoveEntityTask(entity_id)
        self.jsonify_and_send_task(task)

    def set_x_y_offset(self, coordinates: list[tuple[int, int]]):
        min_x = min(x for x, y in coordinates)
        min_y = min(y for x, y in coordinates)
        max_y = max(y for x, y in coordinates)
        max_x = max(x for x, y in coordinates)
        self.x_offset = min_x
        self.y_offset = min_y
        self.board_height = max_y - min_y + 1
        self.board_width = max_x - min_x + 1

    def normalize_coordinate(self, coordinate: tuple[int, int]):
        return (coordinate[0] - self.x_offset, coordinate[1] - self.y_offset)

    def generate_valid_map_coordinates(self, locations):
        valid_map_coordinates = []
        for row_num, row in enumerate(locations):
            for col_num, el in enumerate(row):
                if not el:
                    valid_map_coordinates.append((col_num, row_num))
                    continue
                if isinstance(el, obstacle.Wall):
                    continue
                valid_map_coordinates.append((col_num, row_num))
        return valid_map_coordinates

    def load_characters(self, characters: list[character.Character]):
        healths = [character.health for character in characters]
        sprite_names = [character.pyxel_sprite_name for character in characters]
        teams = [character.team_monster for character in characters]
        task = tasks.LoadCharactersTask(healths, sprite_names, teams)
        self.jsonify_and_send_task(task)

    def load_log(self, log):
        task = tasks.LoadLogTask(log)
        self.jsonify_and_send_task(task)

    def add_to_personal_log(self, log, clear=True):
        task = tasks.AddToPersonalLog(log, clear)
        self.jsonify_and_send_task(task)

    def load_action_cards(self, action_cards, client_id="ALL_FRONTEND"):
        action_card_log = []
        for i, action_card in enumerate(action_cards):
            action_card_log.append(f"""{i}: {action_card}""")
        task = tasks.LoadActionCardsTask(action_card_log=action_card_log)
        self.jsonify_and_send_task(task, client_id)

    def load_round_turn_info(self, round_num, acting_character_name):
        task = tasks.LoadRoundTurnInfoTask(
            round_number=round_num, acting_character_name=acting_character_name
        )
        self.jsonify_and_send_task(task)

    def set_level_map_colors(
        self,
        floor_color_map: list[tuple[int, int]],
        wall_color_map: list[tuple[int, int]],
    ):
        self.floor_color_map = floor_color_map
        self.wall_color_map = wall_color_map

    def jsonify_and_send_task(self, task, client_id="ALL_FRONTEND"):
        json_task = self.tj.convert_task_to_json(task)
        self.server_client.post_task(json_task, client_id)

    def get_user_input(
        self, prompt, valid_inputs=None, client_id="ALL_FRONTEND", is_mouse=False
    ):
        # tell client to get user input
        task_class = tasks.MouseInputTask if is_mouse else tasks.InputTask
        print(task_class)
        task = task_class(prompt)

        self.jsonify_and_send_task(task, client_id)
        # get input back
        user_input = self.server_client.get_user_input()["input"]
        if is_mouse:
            user_input = self.process_mouse_input(user_input)

        if not valid_inputs:
            return user_input

        # if there's validation, keep asking for input until you get what you need
        while user_input not in valid_inputs:
            print(user_input)
            print(valid_inputs)
            task = task_class("Invalid selection pressed. Try again.\n" + prompt)
            self.jsonify_and_send_task(task, client_id)
            user_input = self.server_client.get_user_input()["input"]
            # process our new input if it's mouse input
            user_input = (
                self.process_mouse_input(user_input) if is_mouse else user_input
            )
        return user_input

    def print_message(self, message, client_id="ALL_FRONTEND"):
        task = tasks.PrintTerminalMessage(message)
        self.jsonify_and_send_task(task, client_id)

    def save_campign(self, campaign_state):
        task = tasks.SaveCampaign(campaign_state)
        self.jsonify_and_send_task(task)

    def get_campaign_to_load(self):
        """
        gets pickle file of the campaign data if user wants to load one,
        otherwise returns None
        only asks frontend_1 if they want to load to avoid conflicts
        """
        task = tasks.LoadCampaign()
        self.jsonify_and_send_task(task, "frontend_1")
        return self.server_client.get_user_input()["input"]

    def process_mouse_input(self, user_input):
        """
        This function converts string to a tuple of ints to represent
        coordinates and also converts from offset pyxel coordinates
        to the backend coordinates (which aren't offset)
        """
        new_row, new_col = user_input.split(",")
        new_row = int(float(new_row))
        new_col = int(float(new_col))
        new_row += self.y_offset
        new_col += self.x_offset
        return (new_row, new_col)
