import character
from board import Board
import os
from game_loop import GameLoop
import display
import agent
from config import ALL_AI_MODE
import random


def main(num_players: int | None = None):
    # set up terminal
    if os.getenv("TERM") is None:
        os.environ["TERM"] = "xterm"
    
    disp = display.Display()
    # if players want game help, display instructions
    provide_help_if_desired(disp)

    game = GameLoop(disp, num_players)
    return game.start()

def provide_help_if_desired(disp):
    help_message = '''Welcome to the game! Here's how it works:
- You and the monster will attack each other once per turn in a random order
- You can only attack if you are within range of your enemy
- You pick your attacks, and the monster's are randomly generated
- Each attack has a movement associated with it. If you're not in range, you'll move that amount toward your enemy
- If you end in range, you will attack. If not, you won't attack this turn.
- Whoever runs out of health first loses

Good luck!'''

    want_help = disp.get_user_input(prompt="Hit enter to start or type help for instructions ") if not ALL_AI_MODE else False
    if want_help == "help":
        disp.clear_display_and_print_message(help_message)
        disp.get_user_input(prompt="Hit enter to continue")
        disp.clear_display()

if __name__ == "__main__":
    main()
