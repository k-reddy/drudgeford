import os
import backend.models.display as display
from backend.models.campaign_manager import Campaign
from backend.utils.utilities import get_campaign_filenames
from backend.models.level import GAME_PLOT
from server.tcp_server import TCPServer, ClientType
from backend.models.pyxel_backend import PyxelManager


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
    
    print("Game started, waiting for Player 1 to connect")
    # start the server and wait for a connection from a frontend client
    # right now, the server and client defaults are the same
    # if we change this, we'll need to pass through the port etc.
    server = TCPServer()
    server.start()
    while True:
        if len([1 for client in server.clients.values() if client.client_type == ClientType.FRONTEND]) == 1:
            print("Player 1 connected! Game running")
            break
    
    # offer to load a campaign - will have to re-implement this
    # potential_campaign_filename = offer_to_load_campaign(disp)
    # make a campaign
    campaign = Campaign(num_players, all_ai_mode, server)

    # # if there's a campaign to load, load it
    # if potential_campaign_filename:
    #     campaign.load_campaign(potential_campaign_filename)
    # otherwise, display the plot (since it's a new campaign)
    # if False:
    #     pass
    # else:
    #     # pyxel_manager.print_message(GAME_PLOT)
    #     # pyxel_manager.get_user_input(prompt="Hit enter to continue")
    #     # disp.clear_display()
    campaign.start_campaign()

if __name__ == "__main__":
    main()
