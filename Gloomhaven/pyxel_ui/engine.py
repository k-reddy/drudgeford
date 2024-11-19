import pyxel

from collections import deque
import time

from pyxel_ui.constants import (
    WINDOW_LENGTH,
    DEFAULT_PYXEL_WIDTH,
    DEFAULT_PYXEL_HEIGHT,
    MAP_TILE_HEIGHT_PX,
    MAP_TILE_WIDTH_PX,
)
from .models.action import MoveAction
from .models.tasks import ActionTask
from pyxel_ui.models.pyxel_action_queue import PyxelActionQueue
from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue
from pyxel_ui.controllers.view_manager import ViewManager
from .utils import round_down_to_nearest_multiple

# TODO(john): enable mouse control
# TODO(john): create highlighting class and methods.
# TODO(john): allow mouse to highlight grid sections
# TODO: limit re-draw to areas that will change.


class PyxelEngine:
    def __init__(self, task_queue: PyxelTaskQueue, action_queue: PyxelActionQueue):
        self.current_task = None
        self.is_board_initialized = False

        self.last_mouse_pos = (-1, -1)

        self.hover_grid = None

        # Controllers and queues
        self.action_queue = action_queue
        self.task_queue = task_queue
        self.view_manager = None

        # To measure framerate and loop duration
        self.start_time: float = time.time()
        self.loop_durations: deque[float] = deque(maxlen=WINDOW_LENGTH)
        pyxel.init(DEFAULT_PYXEL_WIDTH, DEFAULT_PYXEL_HEIGHT)
        pyxel.load("../my_resource.pyxres")
        self.view_manager = ViewManager(DEFAULT_PYXEL_WIDTH, DEFAULT_PYXEL_HEIGHT)
        self.mouse_tile_pos = None

    # def generate_hover_grid(self, width_px: int =32, height_px:int =32) -> list

    def start(self):
        pyxel.mouse(True)

        pyxel.run(self.update, self.draw)

    def update(self):
        # self.start_time = time.time()

        if not self.current_task and not self.task_queue.is_empty():
            self.current_task = self.task_queue.dequeue()

        if self.current_task:
            self.current_task.perform(self.view_manager)
            # don't clear the task if it's an action task and has steps to do
            if (
                isinstance(self.current_task, ActionTask)
                and self.current_task.action_steps
            ):
                return
            self.current_task = None

        # Handle cursor redraws and grid
        curr_mouse_x, curr_mouse_y = pyxel.mouse_x, pyxel.mouse_y
        if self.last_mouse_pos != (curr_mouse_x, curr_mouse_y):
            last_mouse_x, last_mouse_y = self.last_mouse_pos
            if view := self.view_manager.get_view_for_coordinate_px(
                last_mouse_x, last_mouse_y
            ):
                view.redraw()

            # Grid concerns
            grid_left_px = round_down_to_nearest_multiple(
                curr_mouse_x, MAP_TILE_WIDTH_PX, self.view_manager.view_border
            )
            grid_top_px = round_down_to_nearest_multiple(
                curr_mouse_y, MAP_TILE_HEIGHT_PX, self.view_manager.view_border
            )
            # draw the grid only if it's on mapview
            # store valid current map tile pos
            if tile_pos := self.view_manager.get_valid_map_coords_for_cursor_pos(
                grid_left_px, grid_top_px
            ):
                self.view_manager.draw_grid(
                    grid_left_px, grid_top_px, MAP_TILE_WIDTH_PX, MAP_TILE_HEIGHT_PX
                )
                self.mouse_tile_pos = tile_pos
            else:
                self.mouse_tile_pos = None

            self.last_mouse_pos = (curr_mouse_x, curr_mouse_y)

        # User Input Land
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # Add controls for scrolling
        # !!! this is a yucky fix
        if pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D):
            # Go to next page if there are more cards to show
            if (
                self.view_manager.action_card_view.current_card_page + 1
            ) * self.view_manager.action_card_view.cards_per_page < len(
                self.view_manager.action_card_view.action_card_log
            ):
                self.view_manager.action_card_view.current_card_page += 1
                self.view_manager.action_card_view.draw()

        # !!! another yucky fix
        if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A):
            # Go to previous page if we're not at the start
            if self.view_manager.action_card_view.current_card_page > 0:
                self.view_manager.action_card_view.current_card_page -= 1
                self.view_manager.action_card_view.draw()

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.mouse_tile_pos:
                tile_pos_x, tile_pos_y = self.mouse_tile_pos
                print(f"{tile_pos_x}, {tile_pos_y}")
                move_action = MoveAction(1, (tile_pos_x, tile_pos_y))
                self.action_queue.enqueue(move_action)

    def draw(self):
        """everything in the task queue draws itself,
        so there's nothing to draw here - this ensures
        we're not redrawing the canvas unless there's something
        new to draw!
        """
        # Calculate duration and framerate
        # loop_duration = time.time() - self.start_time
        # self.loop_durations.append(loop_duration)

        # if len(self.loop_durations) > 0:
        #     avg_duration = mean(self.loop_durations)
        #     loops_per_second = 1 / avg_duration if avg_duration > 0 else 0
        #     avg_duration_ms = avg_duration * 1000
        #     rate_stats = f"LPS: {loops_per_second:.2f} - DUR: {avg_duration_ms:.2f} ms"
        #     # pyxel.text(10, 20, rate_stats, 7)
        return
