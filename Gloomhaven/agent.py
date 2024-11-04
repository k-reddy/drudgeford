import abc
import random
from gh_types import ActionCard
from display import Display
from typing import Callable

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
    def select_action_card(disp: Display, available_action_cards: list[ActionCard]) -> ActionCard:
        pass

    @staticmethod
    @abc.abstractmethod
    def decide_if_move_first(disp: Display) -> bool:
        pass

    @staticmethod
    @abc.abstractmethod
    def select_attack_target(disp, in_range_opponents: list, board, char):
        pass

    @staticmethod
    @abc.abstractmethod
    def perform_movement(char, movement: int, is_jump: bool, board):
        pass 

    @staticmethod
    def move_other_character(char_to_move, mover_loc, movement: int, is_jump: bool, board, movement_check):
        pass


class Ai(Agent):
    @staticmethod
    def select_action_card(disp: Display, available_action_cards: list[ActionCard]) -> ActionCard:
        action_card_num = random.randrange(len(available_action_cards))
        return available_action_cards.pop(action_card_num)
    
    @staticmethod
    def decide_if_move_first(disp: Display) -> bool:
        # monster always moves first - won't move if they're within range
        return True
    
    @staticmethod
    def select_attack_target(disp, in_range_opponents: list, board, char):
        # monster picks a random opponent
        shortest_dist = 1000
        nearest_opponent = None
        attacker_location = board.find_location_of_target(char)
        for opponent in in_range_opponents:
            opponent_location = board.find_location_of_target(opponent)
            opponent_dist = len(board.get_shortest_valid_path(attacker_location, opponent_location))
            if opponent_dist < shortest_dist:
                nearest_opponent = opponent
                shortest_dist = opponent_dist
        return nearest_opponent
    
    @staticmethod
    def perform_movement(char, movement, is_jump, board):
        targets = board.find_opponents(char)
        target = Ai.select_attack_target(None, targets, board, char)
        target_loc = board.find_location_of_target(target)
        board.move_character_toward_location(char, target_loc, movement, is_jump)

    @staticmethod
    # !!! found bug: this is a pull, not a push/movement
    def move_other_character(char_to_move, mover_loc, movement: int, is_jump: bool, board, movement_check):
        board.move_character_toward_location(
            char_to_move, 
            mover_loc,
            movement,
            is_jump
        )
    
class Human(Agent):
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
        key_press = disp.get_user_input(prompt="Type 1 to move first or 2 to perform actions first.", valid_inputs=["1","2"])
        return key_press == "1"
    
    @staticmethod
    def select_attack_target(disp, in_range_opponents: list, board, char):
        # show in range opponents
        disp.add_to_log("Opponents in range: ")
        for i, opponent in enumerate(in_range_opponents):
            disp.add_to_log(f"{i}: {opponent.emoji} {opponent.name}")

        # get user input on which to attack
        prompt = "Please type the number of the opponent you want to attack"
        valid_inputs = [str(i) for i, _ in enumerate(in_range_opponents)]
        target_num = disp.get_user_input(prompt=prompt, valid_inputs=valid_inputs)
        disp.add_to_log("")
        return in_range_opponents[int(target_num)]
    
    @staticmethod
    def perform_movement(char, movement, is_jump, board, additional_movement_check: Callable[[tuple[int, int], tuple[int, int]], bool] | None=None):
        remaining_movement = movement
        while remaining_movement > 0:
            char.disp.add_to_log(f"\nMovement remaining: {remaining_movement}")    
            prompt = "Type w for up, a for left, d for right, s for down, (q, e, z or c) to move diagonally, or f to finish. "
            direction = char.disp.get_user_input(prompt=prompt, valid_inputs=DIRECTION_MAP.keys())
            
            if direction == "f":
                break

            # get your currnet and new locations, then find out if the move is legal
            current_loc = board.find_location_of_target(char)
            new_row, new_col = [
                a + b for a, b in zip(current_loc, DIRECTION_MAP[direction])
            ]
            # perform any additional movement checks

            additional_movement_check_result = additional_movement_check(current_loc, (new_row, new_col)) if additional_movement_check else True
            
            legal_move = board.is_legal_move(new_row, new_col)
            if legal_move and additional_movement_check_result:
                # do this instead of update location because it deals with terrain
                board.move_character_toward_location(char, (new_row, new_col), 1, is_jump)
                remaining_movement -= 1
                continue
            else:
                char.disp.add_to_log(
                    "Invalid movement direction (obstacle, character, or board edge) - try again"
                )
        # board doesn't deal damage to jumping Humans, because they move step by step, so deal final damage here
        if is_jump:
            board.deal_terrain_damage_current_location(char)
        char.disp.add_to_log("Movement done! \n")

    @staticmethod
    def move_other_character(char_to_move, mover_loc, movement: int, is_jump: bool, board, movement_check):
        Human.perform_movement(
            char_to_move,
            movement,
            False,
            board,
            movement_check
        )