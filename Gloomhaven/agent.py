import abc
import random
from gh_types import ActionCard
from board import Board
from display import Display

class Agent(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def select_action_card(disp: Display, available_action_cards: list[ActionCard]) -> ActionCard:
        pass

    @staticmethod
    @abc.abstractmethod
    def decide_if_move_first(disp: Display) -> bool:
        pass

class Ai(Agent):
    @staticmethod
    def select_action_card(disp: Display, available_action_cards: list[ActionCard]) -> ActionCard:
        return random.choice(available_action_cards)
    
    @staticmethod
    def decide_if_move_first(disp: Display) -> bool:
        # monster always moves first - won't move if they're within range
        return True
    
class Human:
    @staticmethod
    def select_action_card(disp: Display, available_action_cards: list[ActionCard]) -> ActionCard:
        # let them pick a valid action_card
        disp.log_action_cards(available_action_cards)
        prompt = "Which action card would you like to pick? Type the number exactly."
        valid_inputs = [str(i) for i, _ in enumerate(available_action_cards)]

        action_card_num = disp.get_user_input(prompt=prompt, valid_inputs=valid_inputs)
        action_card_to_perform = available_action_cards.pop(int(action_card_num))

        disp.clear_log()
        return action_card_to_perform
    
    @staticmethod
    def decide_if_move_first(disp: Display) -> bool:
        key_press = disp.get_user_input(prompt="Type 1 to move first or 2 to attack first.", valid_inputs=["1","2"])
        return key_press == "1"