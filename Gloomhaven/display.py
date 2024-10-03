import helpers 
from gh_types import ActionCard
from character import Player, Monster

EMPTY_CELL = "|      "

class Display:
    def __init__(self) -> None:
        self.log = []
        self.locations = [[]]
        self.terrain = [[]]
        self.characters = []

    def reload_display(self) -> None:
        self._print_healths()
        self.draw_board()
        self.print_log()

    def update_locations(self, locations):
        self.locations = locations
    
    def update_terrain(self, terrain):
        self.terrain = terrain

    # draw the game board and display stats
    def draw_board(self) -> None:
        to_draw = ""
        top = ""
        for i, row in enumerate(self.locations):
            top = " ------" * len(row) + "\n"
            sides = ""
            for el in row:
                if isinstance(el, Player):
                    sides += "|  🧙  "
                elif isinstance(el, Monster):
                    sides += "|  🤖  "
                elif el == "X":
                    sides += "|  🪨   "
                else:
                    sides += EMPTY_CELL
            sides += EMPTY_CELL
            to_draw += top
            to_draw += sides + "\n"

            fire_sides = ""
            for el in enumerate(self.terrain[i]):
                if el == "FIRE":
                    fire_sides += "|  🔥  "
                else:
                    fire_sides += EMPTY_CELL
            fire_sides += EMPTY_CELL
            to_draw += fire_sides + "\n"
        # add the bottom
        to_draw += top
        print(to_draw)
    
    def _print_healths(self) -> None:
        for x in self.characters:
            self.add_to_log(f"{x.name} Health: {x.health}\n")
        self.print_log()

    def add_to_log(self, log_str: str) -> None:
        self.log.append(log_str)

    def print_log(self, num_lines = 10) -> None:
        for line in self.log[-num_lines:]:
            print(line)

    def log_action_cards(self, action_cards) -> None:
        self.add_to_log("Your action cards are: ")
        for i, action_card in enumerate(action_cards):
            self.add_to_log(f"{i}: {action_card}")

    def clear_log(self) -> None:
        self.log = []

    def ask_user_to_select_action_cards(self, action_cards) -> ActionCard:
        self.log_action_cards(action_cards)
        self.print_log()
        while True:
            user_input = input(
                "\nWhich action card would you like to pick? Type the number exactly."
            )
            try:
                action_card_num = int(user_input)
                helpers.clear_terminal()
                action_card_to_perform = action_cards.pop(action_card_num)
                break
            except (ValueError, IndexError):
                print("Oops, typo! Try typing the number again.")
        
        # once action card is chosen, you want to clear the log
        self.clear_log()
        return action_card_to_perform


