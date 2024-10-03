import random
import character
import helpers
from enum import Enum, auto
from config import DEBUG


class GameState(Enum):
    START = auto()
    RUNNING = auto()
    WIN = auto()
    GAME_OVER = auto()


class GameLoop:
    def __init__(self, board):
        self.board = board
        self.game_state = GameState.START

    def start(self):
        self.game_state = GameState.RUNNING

        print(
            "Welcome to your quest, " + self.board.get_player().name + ". \n",
            "As you enter the dungeon, you see a terrifying monster ahead! \n",
            "Kill it or be killed...\n",
        )
        input("Time to start the game! Hit enter to continue\n")

        while self.game_state == GameState.RUNNING:
            self.run_round()
            print(self.game_state)
        # once we're no longer playing, end the game
        if self.game_state != GameState.RUNNING:
            print(f"{self.game_state.name=}")
            self._end_game()

    def run_round(self):
        # randomize who starts the turn
        random.shuffle(self.board.characters)
        print("Start of Round!\n")
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

            print(f"It's {acting_character.name}'s turn!")
            self.run_turn(acting_character)
            # !!! ideally the following lines would go in end_turn(), which is called at the end of run turn but then I don't know how to quit the for loop
            # !!! also the issue here is that if you kill all the monsters, you still move if you decide to
            # move after acting, which is not ideal
            self.check_and_update_game_state()
            if self.game_state != GameState.RUNNING:
                return
        input("End of round. Hit Enter to continue")
        helpers.clear_terminal()

    def run_turn(self, acting_character):
        self.board.draw()
        # if you start in fire, take damage first
        row, col = self.board.find_location_of_target(acting_character)
        self.board.deal_terrain_damage(acting_character, row, col)

        action_card = acting_character.select_action_card()
        self.board.draw()
        move_first = acting_character.decide_if_move_first(action_card, self.board)

        if move_first:
            self.board.draw()
            acting_character.perform_movement(action_card, self.board)
            in_range_opponents = self.board.find_in_range_opponents(
                acting_character, action_card
            )
            self.board.draw()
            target = acting_character.select_attack_target(in_range_opponents)
            self.board.attack_target(action_card, acting_character, target)
        else:
            self.board.draw()
            in_range_opponents = self.board.find_in_range_opponents(
                acting_character, action_card
            )
            self.board.draw()
            target = acting_character.select_attack_target(in_range_opponents)
            self.board.attack_target(action_card, acting_character, target)
            acting_character.perform_movement(action_card, self.board)

        self._end_turn()

    def check_and_update_game_state(self):
        # if all the monsters are dead, player wins
        if all(not isinstance(x, character.Monster) for x in self.board.characters):
            self.game_state = GameState.WIN
        # if all the players are dead, player loses
        elif all(not isinstance(x, character.Player) for x in self.board.characters):
            self.game_state = GameState.GAME_OVER
        return

    def _end_game(self):
        if self.game_status == GameState.GAME_OVER:
            self._lose_game()
        elif self.game_status == GameState.WIN:
            self._win_game()
        else:
            raise ValueError(f"trying to end game when status is {self.game_status}")

    def _end_turn(self):
        input("End of turn. Hit enter to continue")
        helpers.clear_terminal()
        return

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
        return None

    def _win_game(self):
        helpers.clear_terminal()
        print("You defeated the monster!!")
        print(
            "\n" r"    \o/   Victory!\n" "     |\n" "    / \\n" "   /   \\n" "        "
        )
        return None
