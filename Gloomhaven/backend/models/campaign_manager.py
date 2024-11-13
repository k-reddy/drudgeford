import threading
from itertools import count
from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue
from pyxel_ui.engine import PyxelEngine
from backend.models.game_loop import GameLoop
from backend.models.display import Display
from backend.models.pyxel_backend import PyxelManager
from backend.models.level import Level
import backend.models.character as character
import backend.models.agent as agent

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

    def start_campaign(self):
        self.set_num_players()
        self.set_up_player_chars()
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
        game.start()
    
    def run_levels(self):
        level_1 = Level(
            floor_color_map=[(1,3), (5,11)],
            wall_color_map=[(1,4), (13,15)],
            monster_classes=[character.Treeman, character.MushroomMan, character.Fairy]
        )
        # level 2
        level_2 = Level(
            floor_color_map=[(1,8), (5,2)],
            wall_color_map=[],# (1,2), (13,14)
            monster_classes=[character.Demon, character.Fiend, character.FireSprite]
        )
        self.run_level(level_1)
        self.run_level(level_2)

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
        emoji = ["🧙", "🕺", "🐣", "🐣"]
        default_names = ["Happy", "Glad", "Jolly", "Cheery"]
        char_classes = [character.Monk, character.Necromancer, character.Miner, character.Wizard]
        
        # set up characters players can choose from
        for i, char_class in enumerate(char_classes):
            player_agent = agent.Ai() if self.all_ai_mode else agent.Human()
            self.available_chars.append(char_class(default_names[i], self.disp, emoji[i], player_agent, char_id = next(self.id_generator), is_monster=False, log=self.pyxel_manager.log))
        
        for i in range(self.num_players):
            self.player_chars.append(self.select_player_character(i))

        if not self.all_ai_mode:
            self.disp.clear_display()