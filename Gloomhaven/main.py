import os
import threading
from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue
from pyxel_ui.engine import PyxelEngine

from backend.models.game_loop import GameLoop
import backend.models.display as display
import backend.models.pyxel_backend as pyxel_backend


def main(num_players: int = 1, all_ai_mode=False):
    # pyxel setup
    shared_action_queue = PyxelTaskQueue()
    pyxel_view = PyxelEngine(shared_action_queue)

    # set up terminal
    if os.getenv("TERM") is None:
        os.environ["TERM"] = "xterm"

    disp = display.Display(all_ai_mode)
    pyxel_manager = pyxel_backend.PyxelManager(shared_action_queue)
    pyxel_manager.set_level_map_colors(
        floor_color_map = [(1,3), (5,11)],
        wall_color_map = [(1,4), (13,15)]
    )
    if not all_ai_mode:
        disp.clear_display()
    # if players want game help, display instructions
    provide_help_if_desired(disp, all_ai_mode)

    game = GameLoop(disp, num_players, all_ai_mode, pyxel_manager)
    threading.Thread(target=game.start).start()
    pyxel_view.start()


def provide_help_if_desired(disp, all_ai_mode):
    help_message = """Welcome to the game! Here's how it works:
- You and the monster will attack each other once per turn in a random order
- You can only attack if you are within range of your enemy
- You pick your attacks, and the monster's are randomly generated
- Each attack has a movement associated with it. If you're not in range, you'll move that amount toward your enemy
- If you end in range, you will attack. If not, you won't attack this turn.
- Whoever runs out of health first loses

Good luck!"""
    want_help = False
    if not all_ai_mode:
        user_input = disp.get_user_input(
            prompt="Hit enter to start or type help for instructions "
        )
        if user_input == "help":
            want_help = True
    if want_help:
        disp.clear_display_and_print_message(help_message)
        disp.get_user_input(prompt="Hit enter to continue")
        disp.clear_display()


if __name__ == "__main__":
    main()
