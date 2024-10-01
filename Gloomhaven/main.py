import helpers
import character
from board import Board
import os


def main():
    # set up terminal
    if os.getenv("TERM") is None:
        os.environ["TERM"] = "xterm"

    # get some user input before starting the game
    player_name = input("What's your character's name? ")
    helpers.clear_terminal()
    want_help = input("Hit enter to start or type help for instructions ")
    helpers.clear_terminal()
    if want_help == "help":
        helpers.give_help()
    monster = character.Monster("Tree Man", 10)
    player = character.Player(player_name, 10)
    Board(5, monster, player)


if __name__ == "__main__":
    main()
