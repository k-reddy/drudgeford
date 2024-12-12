import os
import sys
import traceback
import time
from backend.models.campaign_manager import Campaign
from server.tcp_server import TCPServer, ClientType


def main(num_players: int = 1, all_ai_mode=False):
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = None

    try:
        if os.getenv("TERM") is None:
            os.environ["TERM"] = "xterm"

        print(f"Game started at port {port}, waiting for Player 1 to connect")

        server = TCPServer(port=port)
        server.start()

        while True:
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

        campaign = Campaign(num_players, all_ai_mode, server, port)
        campaign.start_campaign()

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received...")
        if server is not None:
            server.running = False  # This will prevent new shutdown timers
            try:
                # Close all client connections first to prevent new timers
                with server.lock:
                    for client in list(server.clients.values()):
                        try:
                            client.socket.close()
                        except:
                            pass
                server.server_socket.close()  # Then close server socket
            except:
                pass

    except Exception as e:
        print(f"\nAn error occurred in game on port {port}: {str(e)}")
        traceback.print_exc()
    finally:
        print(f"\nShutting down game on port {port}...")
        if server is not None:
            try:
                server.stop()  # Still try regular shutdown for cleanup
            except Exception as shutdown_error:
                print(
                    f"Error during server shutdown on port {port}: {str(shutdown_error)}"
                )

        print(f"Game on port {port} shut down complete")


if __name__ == "__main__":
    main()
