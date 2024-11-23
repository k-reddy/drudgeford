import os
import backend.models.display as display
from backend.models.campaign_manager import Campaign
from backend.utils.utilities import get_campaign_filenames
from backend.models.level import GAME_PLOT
from server.tcp_server import TCPServer, ClientType
from backend.models.pyxel_backend import PyxelManager

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

    # make a campaign, which either starts afresh or loads an existing campaign
    # depending on what user wants to do 
    campaign = Campaign(num_players, all_ai_mode, server)
    campaign.start_campaign()

if __name__ == "__main__":
    main()
