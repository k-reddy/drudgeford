import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from .task_jsonifier import TaskJsonifier
from pyxel_ui.models import tasks
from backend.models import character
from backend.models import agent


test_entities = [
    {"id": 1, "position": (0, 0), "name": "skeleton", "priority": 10},
    {"id": 3, "position": (4, 2), "name": "necromancer", "priority": 10},
    {"id": 2, "position": (3, 2), "name": "wizard", "priority": 10},
    {"id": 4, "position": (4, 4), "name": "fire", "priority": 0},
]

load_characters_dict = {
    "healths": [1, 2, 3],
    "sprite_names": ["joh", "js", "pw"],
    "teams": [False, False, True],
    "max_healths": [3, 3, 3],
}

board_init_dict = {
    "map_height": 2,
    "map_width": 3,
    "valid_map_coordinates": [(1, 2), (5, 2)],
    "wall_color_map": [(4, 2)],
    "floor_color_map": None,
}

add_to_personal_log_dict = {"string_to_add": "", "clear": False}
# remaining_inputs = 1
# add_to_personal_log_dict = {
#     "string_to_add": f"Waiting for {remaining_inputs} more player{'s' if remaining_inputs>1 else ''} to hit enter",
#     "clear": False,
# }

emojis = ["🧙", "🕺", "🐣", "🐣"]
default_names = ["Happy", "Glad", "Jolly", "Cheery"]
char_classes = [
    character.Monk,
    character.Necromancer,
    character.Miner,
    character.Wizard,
]
available_chars = []
# set up characters players can choose from
for char_class, emoji, default_name in zip(char_classes, emojis, default_names):
    player_agent = agent.Human()
    available_chars.append(
        char_class(
            default_name,
            [],
            emoji,
            player_agent,
            char_id=1,
            is_monster=False,
            log=[],
        )
    )
character_picker_dict = {
    "names": [x.__class__.__name__ for x in available_chars],
    "sprite_names": [x.pyxel_sprite_name for x in available_chars],
    "backstories": [x.backstory for x in available_chars],
}

action_cards = available_chars[1].action_cards
action_card_log = []
for i, action_card in enumerate(action_cards):
    action_card_log.append(f"""{i}: {action_card}""")


@pytest.mark.parametrize(
    ["data", "task_class"],
    [
        # pytest.param({"log": ["hello", "sup"]}, tasks.LoadLogTask, id="test_log"),
        # pytest.param({"log": ["hel\nlo", "sup"]}, tasks.LoadLogTask, id="test_newline"),
        # pytest.param(
        #     {"entities": test_entities}, tasks.AddEntitiesTask, id="test_add_entities"
        # ),
        # pytest.param({"entity_id": 1}, tasks.RemoveEntityTask, id="test_rem_entities"),
        # pytest.param(
        #     load_characters_dict, tasks.LoadCharactersTask, id="test_load_char"
        # ),
        # pytest.param(board_init_dict, tasks.BoardInitTask, id="test_board_init"),
        # pytest.param({}, tasks.ResetViewManager, id="test_reset_view_manager"),
        # pytest.param(
        #     add_to_personal_log_dict,
        #     tasks.AddToPersonalLog,
        #     id="test_empty_string_jsonifier",
        # ),
        # pytest.param(
        #     character_picker_dict, tasks.ShowCharacterPickerTask, id="char_picker"
        # ),
        pytest.param(
            {"action_card_log": action_card_log},
            tasks.LoadActionCardsTask,
            id="actioncards",
        )
    ],
)
def test_jsonifier(data, task_class):
    test_task = task_class(**data)
    tj = TaskJsonifier()
    json_task = tj.convert_task_to_json(test_task)
    unjsoned_task = tj.make_task_from_json(json_task)
    print(json_task)
    print(unjsoned_task)
    assert isinstance(unjsoned_task, task_class)
    assert unjsoned_task.__dict__ == data
