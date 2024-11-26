import threading
from dataclasses import dataclass
from itertools import count
import pickle
import os
import time

from backend.models.game_loop import GameLoop
from backend.models.pyxel_backend import PyxelManager
from backend.models.level import Level, campaign_levels
import backend.models.character as character
import backend.models.agent as agent
from backend.utils.utilities import GameState
from server.tcp_server import TCPServer, ClientType


@dataclass
class CampaignState:
    remaining_levels: int
    player_classes: list[str]
    player_names: list[str]
    num_players: int
    all_ai_mode: bool
    id_gen_start: int
    player_ids: list


class Campaign:
    """
    a campaign is a series of games, each of which has level metadata
    """

    def __init__(
        self, num_players_default: int, all_ai_mode: bool, server: TCPServer, port: int
    ):
        self.current_level: Level
        self.server = server
        self.pyxel_manager = PyxelManager(port)
        self.num_players = num_players_default
        self.all_ai_mode = all_ai_mode
        self.id_generator = count(start=1)
        self.available_chars = []
        self.player_chars = []
        # we need these to reconstruct our players between levels
        self.player_names = []
        self.player_classes = []
        self.player_ids = []
        self.levels = []
        self.initialized = False

        # see if the user wants to load an existing campaign
        # and do so if desired
        campaign_pickle_to_load = self.pyxel_manager.get_campaign_to_load()
        if campaign_pickle_to_load:
            self.load_campaign(campaign_pickle_to_load)

    def load_campaign(self, campaign_pickle_to_load):
        # get the data needed to recreate the campaign
        campaign_state = pickle.loads(campaign_pickle_to_load)
        # recreate it
        self.id_generator = count(start=campaign_state.id_gen_start)
        self.make_levels()
        self.levels = self.levels[-campaign_state.remaining_levels :]
        self.all_ai_mode = campaign_state.all_ai_mode
        self.num_players = campaign_state.num_players
        self.player_names = campaign_state.player_names
        self.player_classes = campaign_state.player_classes
        self.player_ids = campaign_state.player_ids
        # remember that we already have a set up campaign
        self.initialized = True

    def start_campaign(self):
        # if we load a campaign, we don't want to reset everything
        if not self.initialized:
            self.set_num_players()
            self.wait_for_all_players_to_join()
            self.set_up_player_chars()
            self.make_levels()
            self.initialized = True
        else:
            self.wait_for_all_players_to_join()
        self.run_levels()

    def wait_for_all_players_to_join(self):
        while True:
            # +1 because the backend also connects
            if len(self.server.clients) == self.num_players + 1:
                break
            else:
                self.pyxel_manager.print_message("Waiting for all players to join")
                time.sleep(3)

    def make_levels(self):
        self.levels = campaign_levels.copy()

    def run_level(self, level: Level):
        # reset our player characters between each level
        self.player_chars = self.load_player_characters()
        self.current_level = level
        if not self.all_ai_mode:
            self.pyxel_manager.print_message(message=self.current_level.pre_level_text)
        self.pyxel_manager.set_level_map_colors(
            self.current_level.floor_color_map, self.current_level.wall_color_map
        )
        game = GameLoop(
            self.num_players,
            self.all_ai_mode,
            self.pyxel_manager,
            self.current_level,
            self.id_generator,
            self.player_chars,
        )
        return game.start()

    def run_levels(self):
        for i, _ in enumerate(self.levels):
            output = self.run_level(self.levels.pop(i))

            # if you don't win the level, end here
            if output != GameState.WIN:
                return

            # otherwise, offer to save and continue to next level
            self.save_campaign()

    def set_num_players(self):
        if not self.all_ai_mode:
            self.num_players = int(
                self.pyxel_manager.get_user_input(
                    "How many players are playing? Type 1, 2, or 3.",
                    ["1", "2", "3"],
                    "frontend_1",
                )
            )

    def select_player_character(self, player_num):
        # don't get input for all ai mode
        if self.all_ai_mode:
            return self.available_chars.pop()

        # let other players know what's happening
        player_id = f"frontend_{player_num+1}"
        for client in self.server.clients.values():
            if (
                client.client_id != player_id
                and client.client_type == ClientType.FRONTEND
            ):
                self.pyxel_manager.print_message(
                    f"Waiting for player {player_num+1} to pick a character",
                    client.client_id,
                )

        # send the message only to the appropriate character
        self.pyxel_manager.print_message(
            "It's time to pick your character. Here are your options:\n", player_id
        )
        # print the backstory for every available char
        for i, char in enumerate(self.available_chars):
            self.pyxel_manager.print_message(
                f"{i}: {char.__class__.__name__}", player_id
            )
            self.pyxel_manager.print_message(f"{char.backstory}\n", player_id)

        # let user pick a character
        player_char_num = int(
            self.pyxel_manager.get_user_input(
                prompt="Type the number of the character you want to play. ",
                valid_inputs=[f"{j}" for j, _ in enumerate(self.available_chars)],
                client_id=player_id,
            )
        )
        player_char = self.available_chars.pop(player_char_num)

        # reset default name if player provides a name
        player_name = self.pyxel_manager.get_user_input(
            prompt="What's your character's name? ", client_id=player_id
        )
        if player_name != "":
            player_char.name = player_name
        # set the client_id
        player_char.client_id = player_id

        return player_char

    def set_up_player_chars(self):
        emojis = ["🧙", "🕺", "🐣", "🐣"]
        default_names = ["Happy", "Glad", "Jolly", "Cheery"]
        char_classes = [
            character.Monk,
            character.Necromancer,
            character.Miner,
            character.Wizard,
        ]

        # set up characters players can choose from
        for char_class, emoji, default_name in zip(char_classes, emojis, default_names):
            player_agent = agent.Ai() if self.all_ai_mode else agent.Human()
            self.available_chars.append(
                char_class(
                    default_name,
                    self.pyxel_manager,
                    emoji,
                    player_agent,
                    char_id=next(self.id_generator),
                    is_monster=False,
                    log=self.pyxel_manager.log,
                )
            )

        for i in range(self.num_players):
            self.player_chars.append(self.select_player_character(i))

        for char in self.player_chars:
            self.player_names.append(char.name)
            self.player_classes.append(type(char).__name__)
            self.player_ids.append(char.client_id)

    def load_player_characters(self):
        emojis = ["🧙", "🕺", "🐣", "🐣"]

        # recreate the same characters
        player_chars = []
        for char_class_name, player_name, emoji, player_id in zip(
            self.player_classes, self.player_names, emojis, self.player_ids
        ):
            char_class = getattr(character, char_class_name)
            player_agent = agent.Ai() if self.all_ai_mode else agent.Human()
            player_chars.append(
                char_class(
                    player_name,
                    self.pyxel_manager,
                    emoji,
                    player_agent,
                    char_id=next(self.id_generator),
                    is_monster=False,
                    log=self.pyxel_manager.log,
                    player_id=player_id,
                )
            )
        return player_chars

    def save_campaign(self):
        # Create a simple dict with just the essential data
        campaign_state = CampaignState(
            remaining_levels=len(self.levels),
            player_classes=[type(char).__name__ for char in self.player_chars],
            player_names=[char.name for char in self.player_chars],
            player_ids=[char.client_id for char in self.player_chars],
            num_players=self.num_players,
            all_ai_mode=self.all_ai_mode,
            id_gen_start=next(self.id_generator),
        )
        self.pyxel_manager.save_campign(campaign_state)
