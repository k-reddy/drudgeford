import os
import backend.models.display as display
from backend.models.campaign_manager import Campaign
from backend.utils.utilities import get_campaign_filenames
from backend.models.level import GAME_PLOT
import textwrap
from backend.utils.config import TEXT_WIDTH

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
    help_message = textwrap.fill("""Welcome to the game! Here's how it works:
- All players are on the same team against the AI monsters - a green line under the character in the health bar denotes a player, red denotes a monster
- The game is turn based, and the turn order is randomly determined each round (see the health bar for round order)
- Each turn, you will pick an attack card. Once you use a card, it's gone until you use all your cards, so choose wisely!           
- Movement on the card is how far you can move, strength is how much damage your attack will do, and range is how many squares away you can be and still hit a monster (range 1 is adjacent)
- Every time you attack, you'll draw an 'attack modifier card.' This adds some randomness to your damage. Certain cards (bless, curse) add good/bad modifiers randomly to your deck, and others (charge attack) determine what the next modifier you draw will be
- Some cards place elements/obstacles on the map, like traps and fire. Most of these do damage.
- The exceptions are ice, which gives you a 25% chance of slipping and losing your turn when you step on it, and shadow, which gives all attacks a 10% chance of missing for each square of shadow they pass through

Good luck!""", TEXT_WIDTH)
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
