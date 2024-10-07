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
        self.acting_character_name = ""
        self.round_number = None

    def reload_display(self) -> None:
        helpers.clear_terminal()
        self.draw_board()
        self._print_round_and_turn_info()
        self._print_healths()
        print("\n")
        self.print_log()

    def update_locations(self, locations):
        self.locations = locations
    
    def update_terrain(self, terrain):
        self.terrain = terrain

    def update_acting_character_name(self, new_acting_character_name: str) -> None:
        self.acting_character_name = new_acting_character_name

    def update_round_number(self, new_round_number: int) -> None:
        self.round_number = new_round_number

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
        print_str = "Healths: "
        for x in self.characters:
            print_str += f"{x.name}: {x.health}, "
        print(print_str[:-2])
    
    def _print_round_and_turn_info(self) -> None:
        print(f"Round {self.round_number}, {self.acting_character_name}'s turn.")


    def add_to_log(self, log_str: str) -> None:
        self.log.append(log_str)
        self.reload_display()

    def print_log(self, num_lines = 10) -> None:
        for line in self.log[-num_lines:]:
            print(line)

    def log_action_cards(self, action_cards) -> None:
        self.add_to_log("Your action cards are: ")
        for i, action_card in enumerate(action_cards):
            self.add_to_log(f"{i}: {action_card}")

    def clear_log(self) -> None:
        self.log = []
    
    def get_user_input(self, prompt: str, valid_inputs=None):
        user_input = input(prompt)

        # if there's no validation, return any input given
        if valid_inputs is None:
            return user_input
        
        while user_input not in valid_inputs:
            user_input = input("Invalid key pressed. Try again.")
        
        return user_input



