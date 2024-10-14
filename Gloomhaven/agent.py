import abc
import random
from gh_types import ActionCard

class Agent(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def select_action_card(disp, available_action_cards) -> ActionCard:
        pass

class Ai(Agent):
    @staticmethod
    def select_action_card(disp, available_action_cards) -> ActionCard:
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