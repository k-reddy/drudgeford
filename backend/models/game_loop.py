import random
import copy
import backend.models.character as character
from backend.utils.config import DEBUG
from backend.models.display import Display
import backend.models.agent
from backend.models.board import Board
from backend.models.obstacle import SlipAndLoseTurn, EntrappedAndLoseTurn
from backend.models.pyxel_backend import PyxelManager
from backend.models.level import Level
from backend.utils.utilities import GameState, DieAndEndTurn


class GameLoop:
    def __init__(
        self,
        num_players: int,
        all_ai_mode: bool,
        pyxel_manager: PyxelManager,
        level: Level,
        id_generator,
        players,
        is_test: bool = False,
    ):
        self.id_generator = id_generator
        self.pyxel_manager = pyxel_manager
        self.level = level
        self.num_players = num_players
        self.players = players
        self.all_ai_mode = all_ai_mode
        monsters = self.set_up_monsters()
        self.board = Board(
            10,
            monsters,
            players,
            pyxel_manager,
            self.id_generator,
            level.starting_elements,
        )
        self.game_state = GameState.START

    def start(self) -> GameState:
        self.game_state = GameState.RUNNING
        # load everyone's action cards
        for player in self.players:
            self.pyxel_manager.load_action_cards(
                player.available_action_cards, player.client_id
            )
        round_number = 1
        while self.game_state == GameState.RUNNING:
            self.run_round(round_number)
            print(self.game_state)
            round_number += 1
            self.board.round_num = round_number
        # once we're no longer playing, end the game
        # print(f"{self.game_state.name=}")
        return self._end_game()

    def start_test(self) -> GameState:
        self.game_state = GameState.RUNNING

        round_number = 1
        while self.game_state == GameState.RUNNING:
            self.run_round(round_number, True)
            # print(self.game_state)
            round_number += 1
            self.board.round_num = round_number
        # once we're no longer playing, end the game
        # print(f"{self.game_state.name=}")
        return self._end_game()

    def run_round(self, round_num: int, is_test: bool = False) -> None:
        # clear the elements from the board that have "expired"
        self.board.update_terrain()
        # if we don't shuffle the actual list, we will create ordering issues
        # b/c when we kill a character, we send a copy of characters over to
        # pyxel, same when we update healths
        random.shuffle(self.board.characters)
        round_character_list = list(self.board.characters)
        self.pyxel_manager.load_characters(self.board.characters)
        for acting_character in round_character_list:
            # since we use a copy, we need to make sure the character is still alive
            if acting_character not in self.board.characters:
                return
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

            self.pyxel_manager.load_round_turn_info(round_num, acting_character.name)
            if is_test:
                print("run turn move only")
                self.run_turn_move_only(acting_character, round_num)
            else:
                self.run_turn(acting_character, round_num)
            self.check_and_update_game_state()
            if self.game_state != GameState.RUNNING:
                return
        self._end_round()

    def run_turn_move_only(
        self, acting_character: character.Character, round_num: int
    ) -> None:
        get_input = True
        try:
            action_card = acting_character.select_action_card()
            move_first = acting_character.decide_if_move_first(action_card)
            actions = [
                # if you start in fire, take damage first
                lambda: self.board.deal_terrain_damage_current_location(
                    acting_character
                ),
                lambda: acting_character.perform_movement(
                    action_card.movement, action_card.jump, self.board
                ),
                lambda: action_card.perform_attack(
                    acting_character, self.board, round_num
                ),
            ]
            # if not move_first, swap the order of movement and attack
            if not move_first:
                actions[1], actions[2] = actions[2], actions[1]

            for action in actions:
                action()
                # after every action, make sure that we shouldn't end the game now
                self.check_and_update_game_state()
                if self.game_state != GameState.RUNNING:
                    return
                # make sure we shouldn't end the player's turn now - if they died, they won't be in characters list
                if acting_character not in self.board.characters:
                    self._end_turn()
                    return
        except SlipAndLoseTurn:
            if not self.all_ai_mode:
                self.pyxel_manager.get_user_input(
                    prompt=f"{acting_character.name} slipped! Hit enter to continue",
                )
        except EntrappedAndLoseTurn:
            if not self.all_ai_mode:
                self.pyxel_manager.get_user_input(
                    prompt=f"{acting_character.name} trapped in web! Hit enter to continue",
                )
        except DieAndEndTurn:
            pass

        self._end_turn()

    def run_turn(self, acting_character: character.Character, round_num: int) -> None:
        self.board.acting_character = acting_character
        try:
            # reset any statuses that should expire on their turn
            self.board.update_character_statuses(acting_character)
            if acting_character.shield[0] > 0:
                self.pyxel_manager.log.append(
                    (f"{acting_character.name} has shield {acting_character.shield[0]}")
                )
            # take damage from elements before starting turn
            self.board.deal_terrain_damage_current_location(acting_character)
            # if they lost their turn, skip it
            if acting_character.lose_turn:
                acting_character.lose_turn = False
                self.pyxel_manager.log.append(
                    f"{acting_character.name} was knocked down and lost their turn."
                )
                self._end_turn()
                return
            # before they pick a card, show them the shields of all their enemies:
            self.display_enemy_shield_info(acting_character)
            action_card = acting_character.select_action_card()
            self.pyxel_manager.log.append(
                f"{acting_character.name} chose {action_card.attack_name}\n"
            )
            # print the action card
            self.pyxel_manager.log.append(action_card)
            actions = [
                lambda: acting_character.perform_movement(
                    action_card.movement, action_card.jump, self.board
                ),
                lambda: action_card.perform_attack(
                    acting_character, self.board, round_num
                ),
            ]
            if action_card.movement == 0:
                actions = [actions[1]]
            else:
                move_first = acting_character.decide_if_move_first(action_card)
                # if not move_first, swap the order of movement and attack
                if not move_first:
                    actions.reverse()

            for action in actions:
                action()
                # after every action, make sure that we shouldn't end the game now
                self.check_and_update_game_state()
                if self.game_state != GameState.RUNNING:
                    return
                # make sure we shouldn't end the player's turn now - if they died, they won't be in characters list
                if acting_character not in self.board.characters:
                    self._end_turn()
                    return
        except SlipAndLoseTurn:
            if not self.all_ai_mode:
                self.pyxel_manager.log.append(
                    f"{acting_character.name} slipped and lost their turn!"
                )
                self.pyxel_manager.pause_for_all_players(
                    num_players=self.num_players,
                    prompt=f"{acting_character.name} slipped! Hit enter to continue",
                )
        except EntrappedAndLoseTurn:
            if not self.all_ai_mode:
                self.pyxel_manager.log.append(
                    f"{acting_character.name} trapped in web and lost their turn!"
                )
                self.pyxel_manager.pause_for_all_players(
                    num_players=self.num_players,
                    prompt=f"{acting_character.name} trapped in web! Hit enter to continue",
                )
        except DieAndEndTurn:
            pass

        self._end_turn()

    def display_enemy_shield_info(self, acting_character: character.Character) -> None:
        """
        prints shield info to the log if any enemies have shields
        """
        shield_info = [
            f"{char.name}: {char.shield[0]}"
            for char in self.board.characters
            if char.team_monster != acting_character.team_monster and char.shield[0] > 0
        ]
        if shield_info:
            self.pyxel_manager.log.append(f"Enemy Shields: {', '.join(shield_info)}")

    def check_and_update_game_state(self) -> None:
        # if all the monsters are dead, player wins
        if all(not x.team_monster for x in self.board.characters):
            self.game_state = GameState.WIN
        # if all the players are dead, player loses
        elif all(x.team_monster for x in self.board.characters):
            self.game_state = GameState.GAME_OVER

    def _end_game(self) -> GameState:
        # print("resetting view manager")
        # self.pyxel_manager.reset_view_manager()
        # print("done")
        message = ""
        if self.game_state == GameState.GAME_OVER:
            message = self._lose_game_dead()
        elif self.game_state == GameState.WIN:
            message = self._win_game()
        elif self.game_state == GameState.EXHAUSTED:
            message = self._lose_game_exhausted()
        else:
            raise ValueError(
                f"trying to end game when status is {self.game_state.name}"
            )
        return self.game_state, message

    def _end_turn(self) -> None:
        self.board.acting_character = None
        if not self.all_ai_mode:
            self.pyxel_manager.pause_for_all_players(
                self.num_players,
                prompt="End of turn. Hit enter to continue",
            )
            self.pyxel_manager.log.clear()

    def _end_round(self) -> None:
        if not self.all_ai_mode:
            # 0 because that's the default round number
            self.pyxel_manager.load_round_turn_info(0, None)
        for char in self.board.characters:
            self.refresh_character_cards(char)
        if not self.all_ai_mode:
            self.pyxel_manager.pause_for_all_players(
                num_players=self.num_players,
                prompt="End of round. Hit enter to continue",
            )
            self.pyxel_manager.log.clear()

    def refresh_character_cards(self, char: character.Character) -> None:
        # If players don't have remaining action cards, short rest. Note: this should never happen to monsters - we check for that below
        short_rest = False
        if len(char.available_action_cards) == 0:
            self.pyxel_manager.add_to_personal_log(
                "No more action cards left, time to short rest!",
                clear=True,
                client_id=char.client_id,
            )
            short_rest = True
        else:
            short_rest = char.decide_if_short_rest()

        if short_rest:
            char.short_rest()

        # if player has no cards after short resting, they're done!
        if len(char.available_action_cards) == 0:
            if not char.team_monster:
                self.pyxel_manager.log.append(
                    "Drat, you ran out of cards and got exhausted"
                )
                self.game_state = GameState.EXHAUSTED
            else:
                raise ValueError("Monsters getting exhausted...")

    def _lose_game_dead(self) -> str:
        message = """You died...GAME OVER
     .-.
    (o o)  
     |-|  
    /   \\
   |     |
    \\___/"""
        return message

    def _lose_game_exhausted(self) -> str:
        message = """You got exhausted...GAME OVER
     .-.
    (o o)  
     |-|  
    /   \\
   |     |
    \\___/"""
        return message

    def _win_game(self) -> str:
        message = """You defeated the monsters!! Victory!
    \\o/   Victory!
     |
    / \\
   /   \\
        """
        return message

    def set_up_monsters(self):
        monsters = []
        emoji = ["🌵", "🪼 ", "💀", "🧟"]
        player_enemy_num_mapping = {1: 3, 2: 5, 3: 6}
        for i in range(player_enemy_num_mapping[self.num_players]):
            class_num = i % len(self.level.monster_classes)
            monster_name = self.level.monster_classes[class_num].__name__
            monster = self.level.monster_classes[class_num](
                monster_name,
                self.pyxel_manager,
                emoji[class_num],
                backend.models.agent.Ai(),
                char_id=next(self.id_generator),
                is_monster=True,
                log=self.pyxel_manager.log,
            )
            # if you have more than 1 player, make half of the enemies stronger
            # relative to num_players
            if self.num_players > 1 and i % 2 == 0:
                monster.max_health += self.num_players
                monster.health += self.num_players
            monsters.append(monster)
        return monsters
