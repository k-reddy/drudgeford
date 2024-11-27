import abc
import random
from typing import Optional
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
    "f": None,
}


class Agent(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def select_action_card(
        pyxel_manager: PyxelManager,
        available_action_cards: list[ActionCard],
        client_id: Optional[str] = None,
    ) -> ActionCard:
        pass

    @staticmethod
    @abc.abstractmethod
    def decide_if_move_first(
        pyxel_manager: PyxelManager, client_id: Optional[str] = None
    ) -> bool:
        pass

    @staticmethod
    @abc.abstractmethod
    def select_attack_target(
        pyxel_manager,
        in_range_opponents: list,
        board,
        char,
        client_id: Optional[str] = None,
    ):
        pass

    @staticmethod
    @abc.abstractmethod
    def perform_movement(
        char, movement: int, is_jump: bool, board, client_id: Optional[str] = None
    ):
        pass

    @staticmethod
    @abc.abstractmethod
    def move_other_character(
        char_to_move,
        mover_loc,
        movement: int,
        is_jump: bool,
        board,
        movement_check,
        client_id: Optional[str] = None,
        is_push=False,
    ):
        pass


class Ai(Agent):
    @staticmethod
    def select_action_card(
        pyxel_manager: PyxelManager,
        available_action_cards: list[ActionCard],
        client_id: Optional[str] = None,
    ) -> ActionCard:
        action_card_num = random.randrange(len(available_action_cards))
        return available_action_cards.pop(action_card_num)

    @staticmethod
    def decide_if_move_first(
        pyxel_manager: PyxelManager, client_id: Optional[str] = None
    ) -> bool:
        # monster always moves first - won't move if they're within range
        return True

    @staticmethod
    def select_attack_target(
        pyxel_manager,
        in_range_opponents: list,
        board,
        char,
        client_id: Optional[str] = None,
    ):
        # monster picks a random opponent
        shortest_dist = 1000
        nearest_opponent = None
        attacker_location = board.find_location_of_target(char)
        # pick the closest opponent
        for opponent in in_range_opponents:
            opponent_location = board.find_location_of_target(opponent)
            opponent_dist = len(
                board.get_shortest_valid_path(attacker_location, opponent_location)
            )
            if opponent_dist < shortest_dist:
                nearest_opponent = opponent
                shortest_dist = opponent_dist
        return nearest_opponent

    @staticmethod
    def perform_movement(
        char, movement, is_jump, board, client_id: Optional[str] = None
    ):
        targets = board.find_opponents(char)
        target = Ai.select_attack_target(None, targets, board, char)
        target_loc = board.find_location_of_target(target)
        board.move_character_toward_location(char, target_loc, movement, is_jump)

    @staticmethod
    def move_other_character(
        char_to_move,
        mover_loc,
        movement: int,
        is_jump: bool,
        board,
        movement_check,
        client_id: Optional[str] = None,
        is_push=False,
    ):
        if is_push:
            current_target_loc = board.find_location_of_target(char_to_move)
            directions = [v for v in DIRECTION_MAP.values() if v is not None]
            while movement > 0:
                # grab a random direction
                direction = directions[random.randint(0, len(directions))]
                # simulate moving that way and see if it passes the movement check
                new_target_loc = (a + b for a, b in zip(current_target_loc, direction))
                if movement_check(current_target_loc, new_target_loc):
                    # if so, move that way, update our location, and decrement move counter
                    board.move_character_to_location(
                        char_to_move, new_target_loc, movement, is_jump
                    )
                    current_target_loc = new_target_loc
                    movement -= 1
        # pull is very easy, just move toward puller
        else:
            board.move_character_toward_location(
                char_to_move, mover_loc, movement, is_jump
            )


class Human(Agent):
    @staticmethod
    def select_action_card(
        pyxel_manager: PyxelManager,
        available_action_cards: list[ActionCard],
        client_id: str,
    ) -> ActionCard:
        # let them pick a valid action_card
        prompt = "Which action card would you like to pick? Type the number exactly."
        valid_inputs = [str(i) for i, _ in enumerate(available_action_cards)]

        action_card_num = pyxel_manager.get_user_input(
            prompt=prompt, valid_inputs=valid_inputs, client_id=client_id
        )
        action_card_to_perform = available_action_cards.pop(int(action_card_num))
        # load the new action cards now that you've popped from the list
        pyxel_manager.load_action_cards(available_action_cards, client_id)

        return action_card_to_perform

    @staticmethod
    def decide_if_move_first(
        pyxel_manager: PyxelManager, client_id: Optional[str] = None
    ) -> bool:
        key_press = pyxel_manager.get_user_input(
            prompt="Type 1 to move first or 2 to perform actions first.",
            valid_inputs=["1", "2"],
            client_id=client_id,
        )
        return key_press == "1"

    @staticmethod
    def select_attack_target(
        pyxel_manager,
        in_range_opponents: list,
        board,
        char,
        client_id: Optional[str] = None,
    ):
        if len(in_range_opponents) == 1:
            return in_range_opponents[0]
        # show in range opponents and collect info
        valid_inputs = []
        prompt = (
            "Please click on the character you want to target.\nTargets in range:\n"
        )

        for opponent in in_range_opponents:
            prompt += f"{opponent.name}{': Shield ' + str(opponent.shield[0]) if opponent.shield[0] > 0 else ''}\n"
            valid_inputs.append(board.find_location_of_target(opponent))

        # get user input on which to attack
        row, col = pyxel_manager.get_user_input(
            prompt=prompt, valid_inputs=valid_inputs, client_id=client_id, is_mouse=True
        )
        return board.locations[row][col]

    @staticmethod
    def perform_movement(
        char,
        movement,
        is_jump,
        board,
        client_id: Optional[str] = None,
        additional_movement_check: Optional[
            Callable[[tuple[int, int], tuple[int, int]], bool]
        ] = None,
    ):
        remaining_movement = movement
        orig_prompt = "Click where you want to move. Click on your character to end movement. \n\n  - You can move step by step to control your path \n  - You can also click an endpoint, but it won't avoid traps\n  - If you have jump, pick the endpoint to jump over characters/traps\n"
        prompt = orig_prompt
        while remaining_movement > 0:
            current_loc = board.find_location_of_target(char)
            # only allow user to pick a square in range
            new_row, new_col = char.pyxel_manager.get_user_input(
                prompt=prompt + f"\nMovement remaining: {remaining_movement}",
                is_mouse=True,
                client_id=client_id,
            )
            # we ask them to click on their character if they want to finish their movement
            if current_loc == (new_row, new_col):
                return

            path_len = len(
                board.get_shortest_valid_path(
                    start=current_loc,
                    end=(new_row, new_col),
                    is_jump=is_jump,
                )
            )

            # perform any additional movement checks
            additional_movement_check_result = (
                additional_movement_check(current_loc, (new_row, new_col))
                if additional_movement_check
                else True
            )

            legal_move = board.is_legal_move(new_row, new_col)
            # don't let them pick out of range squares
            if legal_move and additional_movement_check_result and path_len <= movement:
                # do this instead of update location because it deals with terrain
                squares_moved = board.move_character_toward_location(
                    char, (new_row, new_col), remaining_movement, is_jump
                )
                remaining_movement -= squares_moved
                prompt = orig_prompt
                continue
            else:
                prompt = (
                    "Invalid square (obstacle, character, or out of movement range) - try again\n"
                    + prompt
                )

        # board doesn't deal damage to jumping Humans, because they move step by step, so deal final damage here
        if is_jump:
            board.deal_terrain_damage_current_location(char)
        board.pyxel_manager.log.append("Movement done!")

    @staticmethod
    def move_other_character(
        char_to_move,
        mover_loc,
        movement: int,
        is_jump: bool,
        board,
        movement_check,
        client_id: Optional[str] = None,
        is_push=False,
    ):
        Human.perform_movement(
            char_to_move,
            movement,
            False,
            board,
            client_id,
            movement_check,
        )
