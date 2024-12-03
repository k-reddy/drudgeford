import os
import sys
from backend.models.campaign_manager import Campaign
from server.tcp_server import TCPServer, ClientType


def main(num_players: int = 1, all_ai_mode=False):
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    # set up terminal
    if os.getenv("TERM") is None:
        os.environ["TERM"] = "xterm"

    print(f"Game started at port {port}, waiting for Player 1 to connect")
    # start the server and wait for a connection from a frontend client
    # right now, the server and client defaults are the same
    # if we change this, we'll need to pass through the port etc.
    server = TCPServer(port=port)
    server.start()

    while True:
        # cache a copy to prevent changing while iterating
        if (
            len(
                [
                    1
                    for client in list(server.clients.values())
                    if client.client_type == ClientType.FRONTEND
                ]
            )
            == 1
        ):
            print("Player 1 connected! Game running")
            break

    # make a campaign, which either starts afresh or loads an existing campaign
    # depending on what user wants to do
    campaign = Campaign(num_players, all_ai_mode, server, port)
    campaign.start_campaign()


if __name__ == "__main__":
    main()
