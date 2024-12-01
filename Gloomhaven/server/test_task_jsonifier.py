import pytest
from .task_jsonifier import TaskJsonifier
from ..pyxel_ui.models import tasks

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
}

board_init_dict = {
    "map_height": 2,
    "map_width": 3,
    "valid_map_coordinates": [(1, 2), (5, 2)],
    "wall_color_map": [(4, 2)],
    "floor_color_map": None,
}


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
        pytest.param(board_init_dict, tasks.BoardInitTask, id="test_board_init"),
        pytest.param(None, tasks.ResetViewManager, id="test_reset_view_manager"),
    ],
)
def test_jsonifier(data, task_class):
    test_task = task_class(**data)
    tj = TaskJsonifier()
    json_task = tj.convert_task_to_json(test_task)
    unjsoned_task = tj.make_task_from_json(json_task)
    assert isinstance(unjsoned_task, task_class)
    assert unjsoned_task.__dict__ == data
