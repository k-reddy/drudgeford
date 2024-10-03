import helpers 
from gh_types import ActionCard

class Display:
    def __init__(self) -> None:
        self.log = []
        pass

    def reload_display(self) -> None:
        self.draw_board()
        self.print_log()

    def draw_board(self) -> None:
        pass

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

    def ask_user_to_select_action_cards(self, action_cards, actor_name) -> ActionCard:
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
        
        # once action card is chosen, you want to clear the log, then print the card selected
        self.clear_log()
        self.add_to_log(f"{actor_name} is performing {action_card_to_perform.attack_name}")
        self.print_log()
        return action_card_to_perform


