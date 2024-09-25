import helpers
import character
import board
import os


def main():
    if os.getenv('TERM') is None:
        os.environ['TERM'] = 'xterm'
    player_name = input("What's your character's name? ")
    helpers.clear_terminal()
    monster = character.Character("Tree Man", 10, False, [2, 3])
    player = character.Character(player_name, 10, True, [0, 0])
    board.Board(5, monster, player)


if __name__ == "__main__":
    main()
