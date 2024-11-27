import textwrap
from pyxel_ui.engine import PyxelEngine
from backend.utils.config import TEXT_WIDTH


def provide_help_if_desired(all_ai_mode=False):
    help_message = [
        "Welcome to the game! Here's how it works:",
        "- All players are on the same team against the AI monsters - a green line under the character in the health bar denotes a player, red denotes a monster",
        "- The game is turn based, and the turn order is randomly determined each round (see the health bar for round order)",
        "- Each turn, you will pick an attack card. Once you use a card, it's gone until you use all your cards, so choose wisely!",
        "- Movement on the card is how far you can move, strength is how much damage your attack will do, and range is how many squares away you can be and still hit a monster (range 1 is adjacent)",
        "- Every time you attack, you'll draw an 'attack modifier card.' This adds some randomness to your damage. Certain cards (bless, curse) add good/bad modifiers randomly to your deck, and others (charge attack) determine what the next modifier you draw will be",
        "- Some cards place elements/obstacles on the map, like traps and fire. Most of these do damage.",
        "- The exceptions are ice, which gives you a 25% chance of slipping and losing your turn when you step on it, and shadow, which gives all attacks a 10% chance of missing for each square of shadow they pass through",
        "Good luck!",
    ]
    want_help = False
    if not all_ai_mode:
        user_input = input(
            "Welcome to the game. Hit enter to start or type help for instructions "
        )
        if user_input == "help":
            want_help = True
    if want_help:
        print("")
        for line in help_message:
            print(textwrap.fill(line, TEXT_WIDTH))
            print("")
        input("Hit enter to continue")


def main(dev_mode=False):
    if dev_mode:
        port = "8000"
    else:
        port = input("Please enter the port number")
        valid_ports = ["5000", "5001", "5002", "5003", "5004", "8000"]
        while port not in valid_ports:
            port = input("Please enter a valid port number")
    port = int(port)
    # if players want game help, display instructions
    provide_help_if_desired()
    pyxel_view = PyxelEngine(port)
    pyxel_view.start()


if __name__ == "__main__":
    main()
