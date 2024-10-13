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
    num_players = 1
    players = []
    emoji = ["🧙", "🕺", "🐣"]
    default_names = ["Happy", "Glad", "Jolly"]

    # get some user input before starting the game
    multi_player = True if disp.get_user_input("Would you like to play multi-player? (y)es or (n)o ", ["y", "n"]) == "y" else False
    if multi_player:
        num_players = int(disp.get_user_input("How many players? Type 1, 2, or 3.", ["1", "2", "3"]))
    for i in range(num_players):
        player_name = disp.get_user_input(prompt=f"What's Player {i+1}'s character's name? ")
        # default to happy :D
        player_name = player_name if player_name != "" else default_names[i]
        players.append(character.Player(player_name, 10, disp, emoji[i]))
    disp.clear_display()
    want_help = disp.get_user_input(prompt="Hit enter to start or type help for instructions ")
    if want_help == "help":
        disp.clear_display_and_print_message(help_message)
        disp.get_user_input(prompt="Hit enter to continue")
        disp.clear_display()

    monsters = []
    names = ["Tree Man", "Evil Blob", "Living Skeleton", "Evil Eye"]
    emoji = ["🌵", "🪼 ", "💀", "🧿"]
    healths = [3,3,5,5]
    for i in range(num_players+1):
        monster = character.Monster(names[i], healths[i], disp, emoji[i])
        monsters.append(monster)
    board = Board(10, monsters, players, disp)
    game = GameLoop(board, disp)
    game.start()


if __name__ == "__main__":
    main()
