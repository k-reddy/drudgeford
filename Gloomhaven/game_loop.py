import random
from character import CharacterType, Monster, Player
import helpers
from enum import Enum, auto
from config import DEBUG
from display import Display


class GameState(Enum):
    START = auto()
    RUNNING = auto()
    WIN = auto()
    GAME_OVER = auto()


class GameLoop:
    def __init__(self, board, disp: Display):
        self.board = board
        self.game_state = GameState.START
        self.disp = disp

    def start(self):
        self.game_state = GameState.RUNNING

        print(
            "Welcome to your quest, " + self.board.get_player().name + ". \n",
            "As you enter the dungeon, you see a terrifying monster ahead! \n",
            "Kill it or be killed...\n",
        )
        input("Time to start the game! Hit enter to continue\n")
        
        round_number = 1
        while self.game_state == GameState.RUNNING:
            self.disp.update_round_number(round_number)
            self.run_round()
            print(self.game_state)
            round_number += 1
        # once we're no longer playing, end the game
        if self.game_state != GameState.RUNNING:
            print(f"{self.game_state.name=}")
            self._end_game()

    def run_round(self) -> None:
        # randomize who starts the turn
        random.shuffle(self.board.characters)
        for i, acting_character in enumerate(self.board.characters):
            # randomly pick who starts the round
            if DEBUG:
                # For testing pathfinding. should create debug mode
                character1_pos = self.board.find_location_of_target(
                    self.board.characters[0]
                )
                character2_pos = self.board.find_location_of_target(
                    self.board.characters[1]
                )
                print(f"{character1_pos=} - {character2_pos=}")
                optimal_path = self.board.get_shortest_valid_path(
                    character1_pos, character2_pos
                )
                print(f"{optimal_path=}")
                # end pathfinding test

            self.disp.update_acting_character_name(acting_character.name)
            self.run_turn(acting_character)
            # !!! ideally the following lines would go in end_turn(), which is called at the end of run turn but then I don't know how to quit the for loop
            # !!! also the issue here is that if you kill all the monsters, you still move if you decide to
            # move after acting, which is not ideal
            self.check_and_update_game_state()
            if self.game_state != GameState.RUNNING:
                return
        self.get_user_input(prompt="End of round. Hit Enter to continue")
        helpers.clear_terminal()

    def run_turn(self, acting_character: CharacterType) -> None:
        # if you start in fire, take damage first
        row, col = self.board.find_location_of_target(acting_character)
        self.board.deal_terrain_damage(acting_character, row, col)

        action_card = acting_character.select_action_card()

        move_first = acting_character.decide_if_move_first(action_card, self.board)

        if move_first:
            acting_character.perform_movement(action_card, self.board)
            in_range_opponents = self.board.find_in_range_opponents(
                acting_character, action_card
            )
            target = acting_character.select_attack_target(in_range_opponents)
            self.board.attack_target(action_card, acting_character, target)
        else:
            in_range_opponents = self.board.find_in_range_opponents(
                acting_character, action_card
            )
            target = acting_character.select_attack_target(in_range_opponents)
            self.board.attack_target(action_card, acting_character, target)
            acting_character.perform_movement(action_card, self.board)

        self._end_turn()

    def check_and_update_game_state(self) -> None:
        # if all the monsters are dead, player wins
        if all(not isinstance(x, Monster) for x in self.board.characters):
            self.game_state = GameState.WIN
        # if all the players are dead, player loses
        elif all(not isinstance(x, Player) for x in self.board.characters):
            self.game_state = GameState.GAME_OVER

    def _end_game(self) -> None:
        if self.game_state == GameState.GAME_OVER:
            self._lose_game()
        elif self.game_state == GameState.WIN:
            self._win_game()
        else:
            raise ValueError(
                f"trying to end game when status is {self.game_state.name}"
            )

    def _end_turn(self) -> None:
        self.disp.get_user_input(prompt="End of turn. Hit enter to continue")
        self.disp.clear_log()

    def _lose_game(self):
        helpers.clear_terminal()
        print(
            """You died...GAME OVER
    .-.
    (o o)  
    |-|  
    /   \\
    |     |
    \\___/"""
        )

    def _win_game(self) -> None:
        helpers.clear_terminal()
        print("You defeated the monster!!")
        print(
            "\n" r"    \o/   Victory!\n" "     |\n" "    / \\n" "   /   \\n" "        "
        )
