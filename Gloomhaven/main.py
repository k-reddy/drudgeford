import character
from board import Board
import os
from game_loop import GameLoop
import display
import agent
from config import ALL_AI_MODE
import random


def main(num_players = int | None):
    # set up terminal
    if os.getenv("TERM") is None:
        os.environ["TERM"] = "xterm"
    
    disp = display.Display()
    # get user input and set up number of players and names
    players = set_up_players(disp, num_players)
    # if players want game help, display instructions
    provide_help_if_desired(disp)
    # set up monsters
    monsters = set_up_monsters(len(players), disp)
    
    board = Board(10, monsters, players, disp)
    game = GameLoop(board, disp)
    game.start()

def set_up_players(disp, num_players):
    num_players = 1
    players = []
    emoji = ["🧙", "🕺", "🐣"]
    default_names = ["Happy", "Glad", "Jolly"]

    # get some user input before starting the game
    num_players = int(disp.get_user_input("How many players are playing? Type 1, 2, or 3.", ["1", "2", "3"])) if not ALL_AI_MODE else num_players
    for i in range(num_players):
        player_name = disp.get_user_input(prompt=f"What's Player {i+1}'s character's name? ") if not ALL_AI_MODE else ""
        # default to happy :D
        player_name = player_name if player_name != "" else default_names[i]
        player_agent = agent.Ai() if ALL_AI_MODE else agent.Human()
        players.append(character.Player(player_name, 10, disp, emoji[i], player_agent))
    disp.clear_display()
    return players

def provide_help_if_desired(disp):
    help_message = '''Welcome to the game! Here's how it works:
- You and the monster will attack each other once per turn in a random order
- You can only attack if you are within range of your enemy
- You pick your attacks, and the monster's are randomly generated
- Each attack has a movement associated with it. If you're not in range, you'll move that amount toward your enemy
- If you end in range, you will attack. If not, you won't attack this turn.
- Whoever runs out of health first loses

Good luck!'''

    want_help = disp.get_user_input(prompt="Hit enter to start or type help for instructions ") if not ALL_AI_MODE else False
    if want_help == "help":
        disp.clear_display_and_print_message(help_message)
        disp.get_user_input(prompt="Hit enter to continue")
        disp.clear_display()

def set_up_monsters(num_players, disp):
    monsters = []
    names = ["Tree Man", "Evil Blob", "Living Skeleton", "Evil Eye"]
    emoji = ["🌵", "🪼 ", "💀", "🧿"]
    healths = [3,3,5,5]
    for i in range(num_players+1):
        monster = character.Monster(names[i], healths[i], disp, emoji[i], agent.Ai())
        monsters.append(monster)
    return monsters
if __name__ == "__main__":
    main()
