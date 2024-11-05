import os
from backend.models.action_model import ActionCard
from backend.models.character import Character
import backend.models.obstacle as obstacle

EMPTY_CELL = "|      "


class Display:
    def __init__(self, all_ai_mode: bool) -> None:
        pass

    def get_user_input(self, prompt: str, valid_inputs=None):
        user_input = input(prompt)

        # if there's no validation, return any input given
        if valid_inputs is None:
            return user_input

        while user_input not in valid_inputs:
            user_input = input("Invalid key pressed. Try again.")

        return user_input

    def print_message(self, message, clear_display=True) -> None:
        if clear_display:
            self.clear_display()
        print(message)

    def clear_display(self) -> None:
        # Check if the system is Windows
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")
        return
