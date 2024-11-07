import pyxel

from collections import deque
from statistics import mean
import time

from .constants import (
    WINDOW_LENGTH,
    DEFAULT_PYXEL_WIDTH,
    DEFAULT_PYXEL_HEIGHT,
    MAP_TILE_HEIGHT_PX,
    MAP_TILE_WIDTH_PX
)
from .models.tasks import BoardInitTask, ActionTask

from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue
from .models.entity import Entity
from pyxel_ui.controllers.view_manager import ViewManager

# TODO(john): enable mouse control
# TODO(john): create highlighting class and methods.
# TODO(john): allow mouse to highlight grid sections
# TODO: limit re-draw to areas that will change.

class PyxelEngine:
    def __init__(self, task_queue: PyxelTaskQueue):
        self.current_task = None
        self.is_board_initialized = False

        # Controllers and queues
        self.task_queue = task_queue
        self.view_manager = None

        # To measure framerate and loop duration
        self.start_time: float = time.time()
        self.loop_durations: deque[float] = deque(maxlen=WINDOW_LENGTH)

    def init_pyxel_map(self, map_width_tiles, map_height_tiles, valid_floor_coordinates):
        self.valid_floor_coordinates = valid_floor_coordinates
        pyxel_width = max(DEFAULT_PYXEL_WIDTH, map_width_tiles*MAP_TILE_WIDTH_PX)
        pyxel_height = max(DEFAULT_PYXEL_HEIGHT, map_height_tiles*MAP_TILE_HEIGHT_PX*1.5)
        pyxel.init(pyxel_width, pyxel_height)
        pyxel.load("../my_resource.pyxres")

        self.view_manager = ViewManager(pyxel_width, pyxel_height)

    def start(self):
        print("Starting Pyxel game loop...")
        # init pyxel canvas and map that align with those of GH backend
        # canvas + map = board
        while not self.is_board_initialized:
            if not self.current_task and not self.task_queue.is_empty():
                self.current_task = self.task_queue.dequeue()
                # ensure our first task is board initialization
                if isinstance(self.current_task, BoardInitTask):
                    self.init_pyxel_map(
                        self.current_task.map_width, 
                        self.current_task.map_height, 
                        self.current_task.valid_map_coordinates
                    )
                    self.current_task = None  # clear
                    self.is_board_initialized = True

        pyxel.run(self.update, self.draw)

    def update(self):
        self.start_time = time.time()
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if not self.is_board_initialized:
            return

        if not self.current_task and not self.task_queue.is_empty():
            self.current_task = self.task_queue.dequeue()

        if self.current_task:
            self.current_task.perform(self.view_manager)
            # don't clear the task if it's an action task and has steps to do
            if isinstance(self.current_task, ActionTask) and self.current_task.action_steps:
                return
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
        # # draw map background and grid
        self.view_manager.update_map(self.valid_floor_coordinates)

        # Calculate duration and framerate
        # loop_duration = time.time() - self.start_time
        # self.loop_durations.append(loop_duration)

        # if len(self.loop_durations) > 0:
        #     avg_duration = mean(self.loop_durations)
        #     loops_per_second = 1 / avg_duration if avg_duration > 0 else 0
        #     avg_duration_ms = avg_duration * 1000
        #     rate_stats = f"LPS: {loops_per_second:.2f} - DUR: {avg_duration_ms:.2f} ms"
        #     # pyxel.text(10, 20, rate_stats, 7)
