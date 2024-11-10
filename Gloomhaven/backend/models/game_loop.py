import random
from itertools import count
from enum import Enum, auto
import backend.models.character as character
from backend.utils.config import DEBUG
from backend.models.display import Display
import backend.models.agent
from backend.models.board import Board
from backend.models.obstacle import SlipAndLoseTurn
from backend.models.pyxel_backend import PyxelManager
from backend.models.level import Level


class GameState(Enum):
    START = auto()
    RUNNING = auto()
    WIN = auto()
    GAME_OVER = auto()
    EXHAUSTED = auto()


class GameLoop:
    def __init__(self, disp: Display, num_players: int, all_ai_mode: bool, pyxel_manager: PyxelManager, level: Level):
        self.id_generator = count(start=1)
        self.pyxel_manager = pyxel_manager
        self.level=level
        players = self.set_up_players(disp, num_players, all_ai_mode)
        monsters = self.set_up_monsters(disp, len(players))
        self.board = Board(10, monsters, players, disp, pyxel_manager, self.id_generator)
        self.game_state = GameState.START
        self.disp = disp
        self.all_ai_mode = all_ai_mode

    def start(self) -> GameState:
        self.game_state = GameState.RUNNING
        
        message = """Welcome to your quest.
As you enter the dungeon, you see a terrifying monster ahead! 
Kill it or be killed..."""
        if not self.all_ai_mode:
            self.disp.print_message(message=message, clear_display=True)
            self.disp.get_user_input(
                prompt="Time to start the game! Hit enter to continue\n"
            )

        round_number = 1
        while self.game_state == GameState.RUNNING:
            self.run_round(round_number)
            # print(self.game_state)
            round_number += 1
            self.board.round_num = round_number
        # once we're no longer playing, end the game
        # print(f"{self.game_state.name=}")
        return self._end_game()

    def run_round(self, round_num: int) -> None:
        # clear the elements from the board that have "expired"
        self.board.update_terrain()
        self.board.update_character_statuses()
        # randomize who starts the turn
        random.shuffle(self.board.characters)
        # using this copy, since we can edit this list during a round, messing up indexing
        round_character_list = self.board.characters
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
            self.run_turn(acting_character, round_num)
            # !!! ideally the following lines would go in end_turn(), which is called at the end of run turn but then I don't know how to quit the for loop
            # !!! also the issue here is that if you kill all the monsters, you still move if you decide to
            # move after acting, which is not ideal
            self.check_and_update_game_state()
            if self.game_state != GameState.RUNNING:
                return
        self._end_round()

    def run_turn(self, acting_character: character.Character, round_num: int) -> None:
        try:
            if acting_character.shield[0]>0:
                self.pyxel_manager.log.append((f"{acting_character.name} has shield {acting_character.shield[0]}"))
            if not acting_character.team_monster:
                self.pyxel_manager.load_action_cards(acting_character.available_action_cards)
            action_card = acting_character.select_action_card()
            move_first = acting_character.decide_if_move_first(action_card)
            actions = [
                # if you start in fire, take damage first
                lambda: self.board.deal_terrain_damage_current_location(acting_character),
                lambda: acting_character.perform_movement(action_card.movement, action_card.jump, self.board),
                lambda: action_card.perform_attack(acting_character, self.board, round_num),
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
                self.disp.get_user_input(
                    prompt=f"{acting_character.name} slipped! Hit enter to continue"
                )

        self._end_turn()

    def check_and_update_game_state(self) -> None:
        # if all the monsters are dead, player wins
        if all(not x.team_monster for x in self.board.characters):
            self.game_state = GameState.WIN
        # if all the players are dead, player loses
        elif all(x.team_monster for x in self.board.characters):
            self.game_state = GameState.GAME_OVER

    def _end_game(self) -> GameState:
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
        if not self.all_ai_mode:
            self.disp.print_message(message, clear_display=False)
        return self.game_state

    def _end_turn(self) -> None:
        if not self.all_ai_mode:
            self.disp.get_user_input(prompt="End of turn. Hit enter to continue")
            self.pyxel_manager.load_action_cards([])
            self.pyxel_manager.log.clear() 

    def _end_round(self) -> None:
        for char in self.board.characters:
            self.refresh_character_cards(char)
        if not self.all_ai_mode:
            self.disp.get_user_input(prompt="End of round. Hit Enter to continue")
            self.pyxel_manager.log.clear() 

    def refresh_character_cards(self, char: character.Character) -> None:
        # If players don't have remaining action cards, short rest. Note: this should never happen to monsters - we check for that below
        if len(char.available_action_cards) == 0:
            self.pyxel_manager.log.append("No more action cards left, time to short rest!")
            char.short_rest()

        # if player has no cards after short resting, they're done!
        if len(char.available_action_cards) == 0:
            if not char.team_monster:
                self.pyxel_manager.log.append("Drat, you ran out of cards and got exhausted")
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
        message = """You defeated the monster!! Victory!
    \\o/   Victory!
     |
    / \\
   /   \\
        """
        return message


    def set_up_players(self, disp, num_players, all_ai_mode):
        players = []
        emoji = ["🧙", "🕺", "🐣"]
        default_names = ["Happy", "Glad", "Jolly"]
        char_classes = [character.Monk, character.Necromancer, character.Miner, character.Wizard, ]
        random.shuffle(char_classes)

        # get some user input before starting the game
        num_players = (
            int(
                disp.get_user_input(
                    "How many players are playing? Type 1, 2, or 3.", ["1", "2", "3"]
                )
            )
            if not all_ai_mode
            else num_players
        )
        for i in range(num_players):
            player_name = (
                disp.get_user_input(prompt=f"What's Player {i+1}'s character's name? ")
                if not all_ai_mode
                else ""
            )
            # default to happy :D
            player_name = player_name if player_name != "" else default_names[i]
            player_agent = backend.models.agent.Ai() if all_ai_mode else backend.models.agent.Human()
            players.append(char_classes[i](player_name, disp, emoji[i], player_agent, char_id = next(self.id_generator), is_monster=False, log=self.pyxel_manager.log))
        if not all_ai_mode:
            disp.clear_display()
        return players


    def set_up_monsters(self, disp, num_players):
        monsters = []
        emoji = ["🌵", "🪼 ", "💀", "🧟"]
        for i in range(num_players + 2):
            class_num = i%len(self.level.monster_classes)
            monster_name = self.level.monster_classes[class_num].__name__
            monster = self.level.monster_classes[class_num](monster_name, disp, emoji[class_num], backend.models.agent.Ai(), char_id = next(self.id_generator), is_monster=True, log=self.pyxel_manager.log)
            monsters.append(monster)
        return monsters
