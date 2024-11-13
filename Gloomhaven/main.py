import os
import backend.models.display as display
import pickle
from backend.models.campaign_manager import Campaign
from backend.utils.utilities import get_campaign_filenames

GAME_PLOT = '''Welcome to Drudgeford, your home since childhood. Recently, strange events have been plaguing your village. Crops wither overnight, shadows move against the sun, and ancient runes appear carved into doors. All in the town swear innocence but darkness spreads. You journey to nearby villages in search of information and hear rumors of a puppet master working from the shadows. You decide to seek out this mysterious force before your village succumbs to its influence.'''

def offer_to_load_campaign(disp):
    file_names = get_campaign_filenames()

    user_input = disp.get_user_input("Would you like to load an existing campaign? Type (y)es or hit enter to start new campaign.")
    if user_input != "y":
        return 
    
    if not file_names:
        disp.get_user_input("No existing campaign files. Hit enter to start new campaign") 
        return 
    filename = get_user_to_pick_filename(file_names, disp)
    return filename

def get_user_to_pick_filename(file_names, disp):
    disp.print_message("WARNING: do not load a file you got from the internet or any other file that isn't yours. This file type is not secure.")
    message = "Which game would you like to load? Type just the number\n"
    valid_inputs = []
    file_names.sort()
    for i, name in enumerate(file_names):
        message+=f"{i}: {name}\n"
        valid_inputs.append(str(i))
    file_num = int(disp.get_user_input(message, valid_inputs))
    return file_names[file_num]

def main(num_players: int = 1, all_ai_mode=False):
    # set up terminal
    if os.getenv("TERM") is None:
        os.environ["TERM"] = "xterm"

    # set up and clear display
    disp = display.Display(all_ai_mode)
    if not all_ai_mode:
        disp.clear_display()

    # if players want game help, display instructions
    provide_help_if_desired(disp, all_ai_mode)

    # make a campaign
    campaign = Campaign(disp, num_players, all_ai_mode)

    # offer to load a campaign
    potential_campaign_filename = offer_to_load_campaign(disp)
    # if there's a campaign to load, load it
    if potential_campaign_filename:
        campaign.load_campaign(potential_campaign_filename)
    # otherwise, display the plot (since it's a new campaign)
    else:
        disp.print_message(GAME_PLOT)
        disp.get_user_input(prompt="Hit enter to continue")
        disp.clear_display()
    campaign.start_campaign()


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
