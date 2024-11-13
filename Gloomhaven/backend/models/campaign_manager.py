import threading
from dataclasses import dataclass
from itertools import count
from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue
from pyxel_ui.engine import PyxelEngine
from backend.models.game_loop import GameLoop
from backend.models.display import Display
from backend.models.pyxel_backend import PyxelManager
from backend.models.level import Level
import backend.models.character as character
import backend.models.agent as agent
from backend.utils.utilities import GameState
import pickle
from backend.utils.utilities import get_campaign_filenames
from backend.utils.config import SAVE_FILE_DIR 
import os

@dataclass
class CampaignState:
    remaining_levels: int
    player_classes: list[str]
    player_names: list[str]
    num_players: int
    all_ai_mode: bool
    id_gen_start: int

class Campaign:
    '''
    a campaign is a series of games, each of which has level metadata
    '''
    def __init__(self, disp: Display, num_players_default: int, all_ai_mode: bool):
        self.current_level: Level
        shared_action_queue = PyxelTaskQueue()
        self.pyxel_view = PyxelEngine(shared_action_queue)
        self.pyxel_manager = PyxelManager(shared_action_queue)
        self.disp = disp
        self.num_players = num_players_default
        self.all_ai_mode = all_ai_mode
        self.id_generator = count(start=1)
        self.available_chars = []
        self.player_chars = []
        self.levels = []
        self.initialized = False

    def load_campaign(self, filename):
        # get the data needed to recreate the campaign
        with open(SAVE_FILE_DIR+filename, 'rb') as f:
            campaign_state = pickle.load(f)

        # recreate it
        self.initialized = True
        self.id_generator = count(start=campaign_state.id_gen_start)
        self.make_levels()
        self.levels = self.levels[-campaign_state.remaining_levels:]
        self.all_ai_mode = campaign_state.all_ai_mode
        self.num_players = campaign_state.num_players
        self.player_chars = self.load_player_characters(
            campaign_state.player_names,
            campaign_state.player_classes
        )

    def start_campaign(self):
        # if we load a campaign, we don't want to reset everything
        if not self.initialized:
            self.set_num_players()
            self.set_up_player_chars()
            self.make_levels()
            self.initialized = True
        threading.Thread(target=self.run_levels).start()
        self.pyxel_view.start()


    def run_level(self, level: Level):
        self.current_level = level
        self.pyxel_manager.set_level_map_colors(
            self.current_level.floor_color_map,
            self.current_level.wall_color_map
        )
        game = GameLoop(
            self.disp, 
            self.num_players, 
            self.all_ai_mode, 
            self.pyxel_manager, 
            self.current_level,
            self.id_generator,
            self.player_chars)
        return game.start()
    
    def make_levels(self):
        self.levels.append(Level(
            floor_color_map=[(1,3), (5,11)],
            wall_color_map=[(1,4), (13,15)],
            monster_classes=[character.Treeman, character.MushroomMan, character.Fairy],
            pre_level_text="You decide to start off by exploring the nearby forest and quickly encounter some hostile enemies."
        ))
        self.levels.append(Level(
            floor_color_map=[(1,8), (5,2)],
            wall_color_map=[],# (1,2), (13,14)
            monster_classes=[character.Demon, character.Fiend, character.FireSprite],
            pre_level_text="Uh oh, the Orchestrator has tossed you into a hellish fire realm. You'd better defeat these enemies to save your life!"
        ))

    def run_levels(self):
        for i, _ in enumerate(self.levels):
            output = self.run_level(self.levels.pop(i))

            # if you don't win the level, end here
            if output != GameState.WIN:
                return
            
            self.offer_to_save_campaign()

    def set_num_players(self):
        if not self.all_ai_mode:
            self.num_players = int(
                    self.disp.get_user_input(
                        "Let's set up the game. How many players are playing? Type 1, 2, or 3.", ["1", "2", "3"]
                    )
                )

    def select_player_character(self, player_num):
        # don't get input for all ai mode
        if self.all_ai_mode:
            return self.available_chars.pop()
        
        self.disp.print_message(f"It's time to pick Player {player_num}'s character. Here are your options:\n",True)
        # print the backstory for every available char
        for i, char in enumerate(self.available_chars):
            self.disp.print_message(f"{i}: {char.__class__.__name__}",False)
            self.disp.print_message(f"{char.backstory}\n", False)

        # let user pick a character
        player_char_num = int(self.disp.get_user_input(prompt="Type the number of the character you want to play. ", valid_inputs=[f"{j}" for j,_ in enumerate(self.available_chars)]))
        player_char = self.available_chars.pop(player_char_num)

        # reset default name if player provides a name
        player_name = self.disp.get_user_input(prompt="What's your character's name? ")
        if player_name != "":
            player_char.name = player_name

        return player_char

    def set_up_player_chars(self):
        emojis = ["🧙", "🕺", "🐣", "🐣"]
        default_names = ["Happy", "Glad", "Jolly", "Cheery"]
        char_classes = [character.Monk, character.Necromancer, character.Miner, character.Wizard]
        
        # set up characters players can choose from
        for char_class, emoji, default_name in zip(char_classes, emojis, default_names):
            player_agent = agent.Ai() if self.all_ai_mode else agent.Human()
            self.available_chars.append(char_class(default_name, self.disp, emoji, player_agent, char_id = next(self.id_generator), is_monster=False, log=self.pyxel_manager.log))
        
        for i in range(self.num_players):
            self.player_chars.append(self.select_player_character(i))

        if not self.all_ai_mode:
            self.disp.clear_display()

    def load_player_characters(self, player_names, char_classes):
        emojis = ["🧙", "🕺", "🐣", "🐣"]
        
        # recreate the same characters 
        player_chars = []
        for char_class_name, player_name, emoji in zip(char_classes, player_names, emojis):
            char_class = getattr(character, char_class_name)
            player_agent = agent.Ai() if self.all_ai_mode else agent.Human()
            player_chars.append(char_class(player_name, self.disp, emoji, player_agent, char_id = next(self.id_generator), is_monster=False, log=self.pyxel_manager.log))
        return player_chars
    
    def offer_to_save_campaign(self):
        user_input = self.disp.get_user_input("Would you like to save your progress? Type (y)es or (n)o. ",["y","n"])
        should_save = True if user_input == "y" else False
        if should_save:
            self.save_campaign()

    def get_unused_filename(self):
        file_names = get_campaign_filenames()
        i=0
        filename = f"campaign_{i}.pickle"
        while True:
            if filename in file_names:
                i += 1
                filename = f"campaign_{i}.pickle"
            else:
                break
        return filename
    
    def save_campaign(self):
        # Create a simple dict with just the essential data
        campaign_state = CampaignState(
            remaining_levels=len(self.levels),
            player_classes=[type(char).__name__ for char in self.player_chars],  
            player_names=[char.name for char in self.player_chars],
            num_players=self.num_players,
            all_ai_mode=self.all_ai_mode,
            id_gen_start=next(self.id_generator)
        )
        filename = self.get_unused_filename()
        os.makedirs(SAVE_FILE_DIR, exist_ok=True)
        with open(SAVE_FILE_DIR+filename, 'wb') as f:
            pickle.dump(campaign_state, f)
        self.disp.get_user_input(f"Successfully saved {filename}. Hit enter to continue. ")