import threading
from itertools import count

from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue
from pyxel_ui.engine import PyxelEngine


import backend.models.agent as agent
from backend.models.game_loop import GameLoop
import backend.models.character as character
import backend.models.display as display
from backend.models.level import Level
import backend.models.pyxel_backend as pyxel_backend


def main(num_players: int = 1, all_ai_mode=False):
    # pyxel setup
    shared_action_queue = PyxelTaskQueue()
    pyxel_view = PyxelEngine(shared_action_queue)

    # levels
    levels = [
        Level(
            floor_color_map=[(1, 3), (5, 11)],
            wall_color_map=[(1, 4), (13, 15)],
            monster_classes=[character.Treeman, character.MushroomMan, character.Fairy],
            pre_level_text="You decide to start off by exploring the nearby forest and quickly encounter some hostile enemies.",
            starting_elements=[],
        )
    ]

    disp = display.Display(all_ai_mode)
    print("starting")
    pyxel_manager = pyxel_backend.PyxelManager(shared_action_queue)

    new_char = character.Monk(
        "happy",
        disp,
        "🕺",
        agent.Human(),
        1,
        False,
        pyxel_manager.log,
    )

    game = GameLoop(
        disp, 1, all_ai_mode, pyxel_manager, levels[0], count(start=1), [new_char], True
    )
    threading.Thread(target=game.start_test).start()
    pyxel_view.start()


if __name__ == "__main__":
    main()
