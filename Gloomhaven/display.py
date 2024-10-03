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

