import abc
import random
from gh_types import ActionCard

DIRECTION_MAP = {
    "w": [-1, 0],
    "s": [1, 0],
    "a": [0, -1],
    "d": [0, 1],
    "q": [-1, -1],
    "e": [-1, 1],
    "z": [1, -1],
    "c": [1, 1],
    "f": None
}

class Agent(abc.ABC):
    @abc.abstractmethod
    @staticmethod
    def select_action_card(disp, available_action_cards):
        pass

    @abc.abstractmethod
    def decide_if_move_first(self, action_card, board):
        pass

    @abc.abstractmethod
    def perform_movement(self, action_card, board):
        pass

    @abc.abstractmethod
    def select_attack_target(self, in_range_opponents):
        pass

class Ai(Agent):
    @staticmethod
    def select_action_card(disp, available_action_cards):
        return random.choice(available_action_cards)
    
class Human:
    @staticmethod
    def select_action_card(disp, available_action_cards) -> ActionCard:
        # let them pick a valid action_card
        disp.log_action_cards(available_action_cards)
        prompt = "Which action card would you like to pick? Type the number exactly."
        valid_inputs = [str(i) for i, _ in enumerate(available_action_cards)]

        action_card_num = disp.get_user_input(prompt=prompt, valid_inputs=valid_inputs)
        action_card_to_perform = available_action_cards.pop(int(action_card_num))

        disp.clear_log()
        return action_card_to_perform