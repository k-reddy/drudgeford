import abc
import random
from typing import Optional
from backend.models.action_model import ActionCard
from typing import Callable
from backend.models.pyxel_backend import PyxelManager
from backend.utils import attack_shapes as shapes

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

    @staticmethod
    @abc.abstractmethod
    def decide_if_short_rest(pyxel_manager: PyxelManager, client_id: str) -> bool:
        pass

    @staticmethod
    @abc.abstractmethod
    def pick_rotated_attack_coordinates(
        board,
        shape: set,
        starting_coord: tuple[int, int],
        client_id: str,
        attacker_team_monster: bool,
        from_self: bool,
    ):
        pass

    @staticmethod
    @abc.abstractmethod
    def select_board_square_target(
        board, client_id, att_range, attacker, shape
    ) -> tuple[int, int]:
        pass


class Ai(Agent):
    @staticmethod
    def select_action_card(
        pyxel_manager: PyxelManager,
        available_action_cards: list[ActionCard],
        client_id: Optional[str] = None,
    ) -> ActionCard:
        action_card_num = random.randrange(len(available_action_cards))
        return available_action_cards[action_card_num]

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
    def decide_if_short_rest(pyxel_manager: PyxelManager, client_id: str) -> bool:
        return False

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
            directions_to_explore = directions.copy()
            while movement > 0 and directions_to_explore:
                # grab a random direction
                direction = directions_to_explore.pop(
                    random.randint(0, len(directions_to_explore) - 1)
                )
                # simulate moving that way and see if it passes the movement check
                new_target_loc = tuple(
                    a + b for a, b in zip(current_target_loc, direction)
                )
                if movement_check(current_target_loc, new_target_loc):
                    # if so, move that way, update our location, and decrement move counter
                    board.move_character_toward_location(
                        char_to_move, new_target_loc, movement, is_jump
                    )
                    current_target_loc = new_target_loc
                    movement -= 1
                    # ensure that our character is still alive
                    if char_to_move not in board.characters:
                        return
                    # reset our potential directions
                    directions_to_explore = directions
        # pull is very easy, just move toward puller
        else:
            board.move_character_toward_location(
                char_to_move, mover_loc, movement, is_jump
            )

    @staticmethod
    def pick_rotated_attack_coordinates(
        board,
        shape: set,
        starting_coord: tuple[int, int],
        client_id: str,
        attacker_team_monster: bool,
        from_self: bool,
    ):
        if from_self:
            shape_list = list(shapes.get_all_directional_rotations(shape).values())
        else:
            shape_list = list(shapes.get_cardinal_rotations(shape).values())
        # iterate until you hit someone
        for shape in shape_list:
            attack_coords = [
                (starting_coord[0] + coordinate[0], starting_coord[1] + coordinate[1])
                for coordinate in shape
            ]
            # if you hit an enemy, take this shape, otherwise keep trying other shapes
            for character in board.characters:
                if (
                    character.team_monster != attacker_team_monster
                    and board.find_location_of_target(character) in attack_coords
                ):
                    return attack_coords

        return attack_coords

    @staticmethod
    def select_board_square_target(
        board, client_id, att_range, attacker, shape
    ) -> tuple[int, int]:
        """
        ai will only throw elements at enemeies, so they find an enemy to target
        """
        in_range_enemies = board.find_in_range_opponents_or_allies(
            attacker, att_range, opponents=True
        )
        target = attacker.select_attack_target(in_range_enemies, board)
        if target is None:
            return None, None
        return board.find_location_of_target(target)


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
    def decide_if_short_rest(pyxel_manager: PyxelManager, client_id: str) -> bool:
        key_press = pyxel_manager.get_user_input(
            prompt="Type (s) then enter to short rest or just enter to continue.",
            valid_inputs=["s", ""],
            client_id=client_id,
        )
        print(key_press)
        return key_press == "s"

    @staticmethod
    def select_attack_target(
        pyxel_manager,
        in_range_opponents: list,
        board,
        char,
        client_id: Optional[str] = None,
    ):
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
        orig_prompt: str = "Click where you want to move. Click on your character to end movement. \n\n  - You can move step by step to control your path \n  - You can also click an endpoint, but it won't avoid traps\n  - If you have jump, pick the endpoint to jump over characters/traps\n",
    ):
        remaining_movement = movement
        prompt = orig_prompt
        while remaining_movement > 0:
            # if the character we're moving died, don't try to find them
            if char not in board.characters:
                return
            current_loc = board.find_location_of_target(char)

            if is_jump:
                # reachable position is a radius of remaining_movement around current_loc
                # reachable_paths is an empty dict
                reachable_positions, reachable_paths = (
                    board.find_all_jumpable_positions(current_loc, remaining_movement)
                )
            else:
                # send reachable positions and the shortest valid paths to get to them.
                reachable_positions, reachable_paths = board.find_all_reachable_paths(
                    current_loc, remaining_movement, False, additional_movement_check
                )

            # only allow user to pick a square in range
            new_row, new_col = char.pyxel_manager.get_user_input(
                prompt=prompt + f"\nMovement remaining: {remaining_movement}",
                is_mouse=True,
                client_id=client_id,
                reachable_positions=reachable_positions,
                reachable_paths=reachable_paths,
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
                prompt = "Invalid square (obstacle, character, or out of movement range) - try again"

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
        if is_push:
            push_pull_str = "push"
        elif movement_check:
            push_pull_str = "pull"
        # if there's no movement check, it's moving an ally
        else:
            push_pull_str = "move"
        Human.perform_movement(
            char_to_move,
            movement,
            False,
            board,
            client_id,
            movement_check,
            f"Click where you want to {push_pull_str} other character. Click on that character to end movement. \n\n  - You can move step by step to control enemy's path \n  - You can also click an endpoint if you don't want to control the path\n",
        )

    @staticmethod
    def pick_rotated_attack_coordinates(
        board,
        shape: set,
        starting_coord: tuple[int, int],
        client_id: str,
        attacker_team_monster: bool,
        from_self: bool,
    ):
        return board.pyxel_manager.pick_rotated_attack_coordinates(
            shape, starting_coord, client_id, from_self
        )

    @staticmethod
    def select_board_square_target(
        board, client_id, att_range, attacker, shape
    ) -> tuple[int, int]:
        attacker_loc = board.find_location_of_target(attacker)
        reachable_squares, _ = board.find_all_reachable_paths(
            start=attacker_loc, num_moves=att_range, exclude_walls_only=True
        )
        reachable_squares.append(attacker_loc)
        target_row, target_col = (-1, -1)
        board.pyxel_manager.draw_cursor_grid_shape(
            shape, attacker.client_id, reachable_squares
        )
        while (target_row, target_col) not in reachable_squares:
            target_row, target_col = board.pyxel_manager.get_user_input(
                prompt="Select a valid board square to attack",
                is_mouse=True,
                client_id=client_id,
            )
        board.pyxel_manager.turn_off_cursor_grid_shape(attacker.client_id)
        return target_row, target_col
