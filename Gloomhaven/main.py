import os
import backend.models.display as display
from backend.models.campaign_manager import Campaign

GAME_PLOT = '''Welcome to Drudgeford, your home since childhood. Recently, strange events have been plaguing your village. Crops wither overnight, shadows move against the sun, and ancient runes appear carved into doors. All in the town swear innocence but darkness spreads. You journey to nearby villages in search of information and hear rumors of a puppet master working from the shadows. You decide to seek out this mysterious force before your village succumbs to its influence.'''
def main(num_players: int = 1, all_ai_mode=False):
    # set up terminal
    if os.getenv("TERM") is None:
        os.environ["TERM"] = "xterm"

    disp = display.Display(all_ai_mode)
    if not all_ai_mode:
        disp.clear_display()
    # if players want game help, display instructions
    provide_help_if_desired(disp, all_ai_mode)
    disp.print_message(GAME_PLOT)
    disp.get_user_input(prompt="Hit enter to continue")
    disp.clear_display()

    Campaign(disp, num_players, all_ai_mode).start_campaign()
    # pyxel setup

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
