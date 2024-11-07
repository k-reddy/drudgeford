import pyxel

from collections import deque
from statistics import mean
import time

from .constants import (
    BITS,
    WALL_THICKNESS,
    WINDOW_LENGTH,
)
from .models.action_task import ActionTask
from .models.update_tasks import (
    AddEntityTask,
    RemoveEntityTask,
    LoadCharactersTask,
    LoadLogTask,
    LoadActionCardsTask,
    LoadRoundTurnInfoTask,
)

from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue
from .models.canvas import Canvas
from .models.entity import Entity
from pyxel_ui.controllers.renderer import Renderer
from pyxel_ui.controllers.view_manager import ViewManager
from pyxel_ui.controllers.task_processor import TaskProcessor
from .utils import generate_wall_bank


# phase 1, generate play space based on 64x64 character. add wall boundaries
# phase 2, create move queue and read from them to move character around on grid
# phase 3, integrate with GH backend - set up new task types for use with message queue
# phase 4, start UI, allow for mouse hover to highlight grid boxes
# phase 5, add log and be able to write to it.
# phase 6, add way to dynamically shape walls as obstacles.

# TODO(john): enable mouse control
# TODO(john): create highlighting class and methods.
# TODO(john): allow mouse to highlight grid sections
# TODO: limit re-draw to areas that will change.


class PyxelEngine:
    def __init__(self, task_queue: PyxelTaskQueue):
        self.current_task = None
        self.entities: dict[int, Entity] = {}
        self.is_board_initialized = False

        # Controllers and queues
        self.task_queue = task_queue
        self.view_manager = None
        self.task_processor = None
        self.renderer = None

        # Init game state attributes
        self.initiative_bar_sprite_names = []
        self.initiative_bar_healths = []
        self.initiative_bar_teams = []
        self.log = []
        self.action_card_log = []
        self.current_card_page = 0  # Track which page of cards we're viewing
        self.cards_per_page = 3  # Number of cards to show at once
        self.round_number = 0
        self.acting_character_name = ""

        # To measure framerate and loop duration
        self.start_time: float = time.time()
        self.loop_durations: deque[float] = deque(maxlen=WINDOW_LENGTH)

    def init_pyxel_map(self, width, height, valid_floor_coordinates):
        self.board_tile_width = width
        self.board_tile_height = height
        self.valid_floor_coordinates = valid_floor_coordinates

        # TODO(John): replace these hardcoded numbers.
        pyxel.init(
            self.board_tile_width * BITS + 32 + BITS * 12,
            self.board_tile_height * BITS + BITS * 8,
        )
        pyxel.load("../my_resource.pyxres")

        self.canvas = Canvas(
            board_tile_width=self.board_tile_width,
            board_tile_height=self.board_tile_height,
            tile_width_px=BITS,
            tile_height_px=BITS,
            wall_sprite_thickness_px=WALL_THICKNESS,
        )
        self.view_manager = ViewManager(self.canvas)
        self.task_processor = TaskProcessor(self.entities, self.canvas)
        self.renderer = Renderer(self.view_manager)

        self.dungeon_walls = generate_wall_bank(self.canvas)

    def start(self):
        print("Starting Pyxel game loop...")
        # init pyxel canvas and map that align with those of GH backend
        # canvas + map = board
        # we always do these first 3 tasks in the same order
        while not self.is_board_initialized:
            if not self.current_task and not self.task_queue.is_empty():
                self.current_task = self.task_queue.dequeue()
                self.process_board_initialization_task()
                self.task_processor.process_entity_loading_task(self.current_task)  
                self.current_task = None  # clear
                self.is_board_initialized = True

        pyxel.run(self.update, self.draw)

    def process_board_initialization_task(self) -> None:
        assert self.current_task, "Attempting to process empty system task"
        height = self.current_task.payload["map_height"]
        width = self.current_task.payload["map_width"]
        valid_floor_coordinates = self.current_task.payload["valid_floor_coordinates"]
        self.init_pyxel_map(width, height, valid_floor_coordinates)

    def update(self):
        self.start_time = time.time()
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if not self.is_board_initialized:
            return

        if not self.current_task and not self.task_queue.is_empty():
            temp_task = self.task_queue.dequeue()
            if isinstance(temp_task, ActionTask):
                self.current_task = (
                    self.task_processor.convert_and_append_move_steps_to_action(
                        temp_task
                    )
                )
                return
            else:
                self.current_task = temp_task
                return

        if self.current_task:
            if isinstance(self.current_task, ActionTask):
                self.task_processor.process_action(self.current_task)
            elif isinstance(self.current_task, RemoveEntityTask):
                self.task_processor.process_remove_entity_task(self.current_task)
                self.current_task = None
            elif isinstance(self.current_task, AddEntityTask):
                self.task_processor.process_entity_loading_task(self.current_task)
                self.current_task = None
            elif isinstance(self.current_task, (LoadCharactersTask, LoadLogTask, LoadActionCardsTask, LoadRoundTurnInfoTask)):
                self.current_task.perform(self.view_manager)
                self.current_task = None

        # Add controls for scrolling
        if pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D):
            # Go to next page if there are more cards to show
            if (self.current_card_page + 1) * self.cards_per_page < len(
                self.action_card_log
            ):
                self.current_card_page += 1

        if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A):
            # Go to previous page if we're not at the start
            if self.current_card_page > 0:
                self.current_card_page -= 1

    def draw(self):
        # pyxel.cls(0)
        
        # # draw map background and grid
        self.view_manager.update_map(self.valid_floor_coordinates)

        self.view_manager.update_sprites(self.entities)

        # Calculate duration and framerate
        # loop_duration = time.time() - self.start_time
        # self.loop_durations.append(loop_duration)

        # if len(self.loop_durations) > 0:
        #     avg_duration = mean(self.loop_durations)
        #     loops_per_second = 1 / avg_duration if avg_duration > 0 else 0
        #     avg_duration_ms = avg_duration * 1000
        #     rate_stats = f"LPS: {loops_per_second:.2f} - DUR: {avg_duration_ms:.2f} ms"
        #     # pyxel.text(10, 20, rate_stats, 7)
