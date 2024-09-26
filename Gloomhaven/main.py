import helpers
import character
import board
import os


def main():
    # set up terminal
    if os.getenv('TERM') is None:
        os.environ['TERM'] = 'xterm'

    # get some user input before starting the game
    player_name = input("What's your character's name? ")
    helpers.clear_terminal()
    want_help = input("Hit enter to start or type help for instructions ")
    helpers.clear_terminal()
    if want_help == 'help':
        helpers.give_help()
    monster = character.Character("Tree Man", 10, False, [2, 3])
    player = character.Character(player_name, 10, True, [0, 0])
    board.Board(5, monster, player)


if __name__ == "__main__":
    main()
