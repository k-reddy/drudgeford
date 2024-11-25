import abc
import random
from backend.models.action_model import ActionCard
from typing import Callable
from backend.models.pyxel_backend import PyxelManager

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
    @staticmethod
    @abc.abstractmethod
    def select_action_card(pyxel_manager: PyxelManager, available_action_cards: list[ActionCard], client_id: str|None =None) -> ActionCard:
        pass

    @staticmethod
    @abc.abstractmethod
    def decide_if_move_first(pyxel_manager: PyxelManager, client_id: str|None =None) -> bool:
        pass

    @staticmethod
    @abc.abstractmethod
    def select_attack_target(pyxel_manager, in_range_opponents: list, board, char, client_id: str|None =None):
        pass

    @staticmethod
    @abc.abstractmethod
    def perform_movement(char, movement: int, is_jump: bool, board, client_id: str|None =None):
        pass 

    @staticmethod
    @abc.abstractmethod
    def move_other_character(char_to_move, mover_loc, movement: int, is_jump: bool, board, movement_check, client_id: str|None =None):
        pass


class Ai(Agent):
    @staticmethod
    def select_action_card(pyxel_manager: PyxelManager, available_action_cards: list[ActionCard], client_id: str|None =None) -> ActionCard:
        action_card_num = random.randrange(len(available_action_cards))
        return available_action_cards.pop(action_card_num)
    
    @staticmethod
    def decide_if_move_first(pyxel_manager: PyxelManager, client_id: str|None =None) -> bool:
        # monster always moves first - won't move if they're within range
        return True
    
    @staticmethod
    def select_attack_target(pyxel_manager, in_range_opponents: list, board, char, client_id: str|None =None):
        # monster picks a random opponent
        shortest_dist = 1000
        nearest_opponent = None
        attacker_location = board.find_location_of_target(char)
        # pick the closest opponent
        for opponent in in_range_opponents:
            opponent_location = board.find_location_of_target(opponent)
            opponent_dist = len(board.get_shortest_valid_path(attacker_location, opponent_location))
            if opponent_dist < shortest_dist:
                nearest_opponent = opponent
                shortest_dist = opponent_dist
        return nearest_opponent
    
    @staticmethod
    def perform_movement(char, movement, is_jump, board, client_id: str|None =None):
        targets = board.find_opponents(char)
        target = Ai.select_attack_target(None, targets, board, char)
        target_loc = board.find_location_of_target(target)
        board.move_character_toward_location(char, target_loc, movement, is_jump)

    @staticmethod
    # !!! found bug: this is a pull, not a push/movement
    def move_other_character(char_to_move, mover_loc, movement: int, is_jump: bool, board, movement_check, client_id: str|None =None):
        board.move_character_toward_location(
            char_to_move, 
            mover_loc,
            movement,
            is_jump
        )
    
class Human(Agent):
    @staticmethod
    def select_action_card(pyxel_manager: PyxelManager, available_action_cards: list[ActionCard], client_id: str|None =None) -> ActionCard:
        # let them pick a valid action_card
        prompt = "Which action card would you like to pick? Type the number exactly."
        valid_inputs = [str(i) for i, _ in enumerate(available_action_cards)]

        action_card_num = pyxel_manager.get_user_input(prompt=prompt, valid_inputs=valid_inputs, client_id=client_id)
        action_card_to_perform = available_action_cards.pop(int(action_card_num))
        # load the new action cards now that you've popped from the list
        pyxel_manager.load_action_cards(
                available_action_cards, client_id
        )

        return action_card_to_perform
    
    @staticmethod
    def decide_if_move_first(pyxel_manager: PyxelManager, client_id: str|None =None) -> bool:
        key_press = pyxel_manager.get_user_input(prompt="Type 1 to move first or 2 to perform actions first.", valid_inputs=["1","2"], client_id=client_id)
        return key_press == "1"
    
    @staticmethod
    def select_attack_target(pyxel_manager, in_range_opponents: list, board, char, client_id: str|None =None):
        if len(in_range_opponents) == 1:
            return in_range_opponents[0]
        # show in range opponents
        board.pyxel_manager.log.append("Characters in range: ")
        for i, opponent in enumerate(in_range_opponents):
            board.pyxel_manager.log.append(f"{i}: {opponent.emoji} {opponent.name}")
        board.pyxel_manager.log.append("\n")

        # get user input on which to attack
        prompt = "Please type the number of the character you want to target"
        valid_inputs = [str(i) for i, _ in enumerate(in_range_opponents)]
        target_num = pyxel_manager.get_user_input(prompt=prompt, valid_inputs=valid_inputs, client_id=client_id)
        return in_range_opponents[int(target_num)]
    
    @staticmethod
    def perform_movement(char, movement, is_jump, board, client_id: str|None =None, additional_movement_check: Callable[[tuple[int, int], tuple[int, int]], bool] | None=None):
        remaining_movement = movement
        orig_prompt = "Click where you want to move."
        prompt = orig_prompt
        while remaining_movement > 0:
            new_row, new_col = char.pyxel_manager.get_user_input(prompt=prompt+f"\nMovement remaining: {remaining_movement}", is_mouse = True,client_id=client_id)

            # if direction == "f":
            #     break

            # get your currnet and new locations, then find out if the move is legal
            current_loc = board.find_location_of_target(char)
            # new_row, new_col = [
            #     a + b for a, b in zip(current_loc, DIRECTION_MAP[direction])
            # ]
            # perform any additional movement checks

            additional_movement_check_result = additional_movement_check(current_loc, (new_row, new_col)) if additional_movement_check else True
            
            legal_move = board.is_legal_move(new_row, new_col)
            if legal_move and additional_movement_check_result:
                # do this instead of update location because it deals with terrain
                squares_moved = board.move_character_toward_location(char, (new_row, new_col), remaining_movement, is_jump)
                # !!! change this to length of movement
                remaining_movement -= squares_moved
                prompt = orig_prompt
                continue
            else:
                prompt = "Invalid square (obstacle, character, or board edge) - try again\n" + prompt
                
        # board doesn't deal damage to jumping Humans, because they move step by step, so deal final damage here
        if is_jump:
            board.deal_terrain_damage_current_location(char)
        board.pyxel_manager.log.append("Movement done! \n")

    @staticmethod
    def move_other_character(char_to_move, mover_loc, movement: int, is_jump: bool, board, movement_check, client_id: str|None =None):
        Human.perform_movement(
            char_to_move,
            movement,
            False,
            board,
            client_id,
            movement_check,
        )