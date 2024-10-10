import character
from board import Board
import os
from game_loop import GameLoop
import display


def main():
    # set up terminal
    if os.getenv("TERM") is None:
        os.environ["TERM"] = "xterm"

    help_message = '''Welcome to the game! Here's how it works:
- You and the monster will attack each other once per turn in a random order
- You can only attack if you are within range of your enemy
- You pick your attacks, and the monster's are randomly generated
- Each attack has a movement associated with it. If you're not in range, you'll move that amount toward your enemy
- If you end in range, you will attack. If not, you won't attack this turn.
- Whoever runs out of health first loses

Good luck!'''

    
    disp = display.Display()

    # get some user input before starting the game
    player_name = disp.get_user_input(prompt="What's player 1's character's name? ")
    player_name_2 = disp.get_user_input(prompt="What's player 2's character's name? ")
    # default to happy :D
    player_name = "Happy" if player_name == "" else player_name
    player_name_2 = "Glad" if player_name_2 == "" else player_name_2
    disp.clear_display()
    want_help = disp.get_user_input(prompt="Hit enter to start or type help for instructions ")
    if want_help == "help":
        disp.clear_display_and_print_message(help_message)
        disp.get_user_input(prompt="Hit enter to continue")
        disp.clear_display()

    monsters = []
    names = ["Tree Man", "Evil Blob", "Living Skeleton"]
    emoji = ["🌵", "🪼 ", "💀"]
    for i in range(3):
        monster = character.Monster(names[i], 3, disp, emoji[i])
        monsters.append(monster)
    player_1 = character.Player(player_name, 10, disp, "🧙")
    player_2 = character.Player(player_name_2, 10, disp, "🕺")
    board = Board(10, monsters, [player_1, player_2], disp)
    game = GameLoop(board, disp)
    game.start()


if __name__ == "__main__":
    main()
