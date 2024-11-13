import threading
from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue
from pyxel_ui.engine import PyxelEngine
from backend.models.game_loop import GameLoop
from backend.models.display import Display
from backend.models.pyxel_backend import PyxelManager
from backend.models.level import Level
import backend.models.character as character

class Campaign:
    '''
    a campaign is a series of games, each of which has level metadata
    '''
    def __init__(self, disp: Display, num_players: int, all_ai_mode: bool):
        self.current_level: Level
        shared_action_queue = PyxelTaskQueue()
        self.pyxel_view = PyxelEngine(shared_action_queue)
        self.pyxel_manager = PyxelManager(shared_action_queue)
        self.disp = disp
        self.num_players = num_players
        self.all_ai_mode = all_ai_mode

    def start_campaign(self):
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
            self.current_level)
        game.start()
    
    def run_levels(self):
        level_1 = Level(
            floor_color_map=[(1,3), (5,11)],
            wall_color_map=[(1,4), (13,15)],
            monster_classes=[character.Treeman, character.MushroomMan, character.Fairy]
        )
        self.run_level(level_1)
        # # level 2
        # level = Level(
        #     floor_color_map=[(1,8), (5,2)],
        #     wall_color_map=[(1,2), (13,14)],
        #     monster_classes=[character.Demon, character.Fiend, character.FireSprite]
        # )
