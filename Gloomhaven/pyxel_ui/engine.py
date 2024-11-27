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
from .models.tasks import ActionTask, InputTask, LoadCampaign
from pyxel_ui.controllers.view_manager import ViewManager
from .utils import round_down_to_nearest_multiple
from server.tcp_client import TCPClient, ClientType
from server.task_jsonifier import TaskJsonifier
from .controllers.user_input_manager import UserInputManager

# TODO(john): enable mouse control
# TODO(john): create highlighting class and methods.
# TODO(john): allow mouse to highlight grid sections
# TODO: limit re-draw to areas that will change.


class PyxelEngine:
    def __init__(self, port):
        self.server_client = TCPClient(ClientType.FRONTEND, port=port)
        self.tj = TaskJsonifier()
        self.current_task = None

        # self.last_mouse_pos = (-1, -1)

        self.hover_grid = None

        # Controller
        self.view_manager = None

        # To measure framerate and loop duration
        self.start_time: float = time.time()
        self.loop_durations: deque[float] = deque(maxlen=WINDOW_LENGTH)
        pyxel.init(DEFAULT_PYXEL_WIDTH, DEFAULT_PYXEL_HEIGHT)
        pyxel.load("../my_resource.pyxres")
        self.view_manager = ViewManager(DEFAULT_PYXEL_WIDTH, DEFAULT_PYXEL_HEIGHT)
        # self.mouse_tile_pos = None
        self.keyboard_manager = UserInputManager(self.view_manager, self.server_client)

    # def generate_hover_grid(self, width_px: int =32, height_px:int =32) -> list

    def start(self):
        pyxel.mouse(True)

        pyxel.run(self.update, self.draw)

    def update(self):
        self.start_time = time.time()
        self.keyboard_manager.update()

        if not self.current_task:
            jsonified_task = self.server_client.get_task()
            self.current_task = self.tj.make_task_from_json(jsonified_task)

        if self.current_task:
            task_output = self.current_task.perform(
                self.view_manager, self.keyboard_manager
            )
            # don't clear the task if it's an action task and has steps to do
            if (
                isinstance(self.current_task, ActionTask)
                and self.current_task.action_steps
            ):
                return
            # if we're asked for user input or a campaign, send what we get to the server
            # elif isinstance(self.current_task, (InputTask, LoadCampaign)):
            elif isinstance(self.current_task, LoadCampaign):
                self.server_client.post_user_input(task_output)
            self.current_task = None

        # Handle cursor redraws and grid
        # curr_mouse_x, curr_mouse_y = pyxel.mouse_x, pyxel.mouse_y
        # if self.last_mouse_pos != (curr_mouse_x, curr_mouse_y):
        #     last_mouse_x, last_mouse_y = self.last_mouse_pos
        #     if view := self.view_manager.get_view_for_coordinate_px(
        #         last_mouse_x, last_mouse_y
        #     ):
        #         view.redraw()

        #     # Grid concerns
        #     grid_left_px = round_down_to_nearest_multiple(
        #         curr_mouse_x, MAP_TILE_WIDTH_PX, self.view_manager.view_border
        #     )
        #     grid_top_px = round_down_to_nearest_multiple(
        #         curr_mouse_y, MAP_TILE_HEIGHT_PX, self.view_manager.view_border
        #     )
        #     # draw the grid only if it's on mapview
        #     # store valid current map tile pos
        #     if tile_pos := self.view_manager.get_valid_map_coords_for_cursor_pos(
        #         grid_left_px, grid_top_px
        #     ):
        #         self.view_manager.draw_grid(
        #             grid_left_px, grid_top_px, MAP_TILE_WIDTH_PX, MAP_TILE_HEIGHT_PX
        #         )
        #         self.mouse_tile_pos = tile_pos
        #     else:
        #         self.mouse_tile_pos = None

        #     self.last_mouse_pos = (curr_mouse_x, curr_mouse_y)

        # User Input Land
        # if self.accept_mouse_input and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
        #     if self.mouse_tile_pos:
        #         tile_pos_x, tile_pos_y = self.mouse_tile_pos
        #         # BUG: location seems to be relative to character starting position so
        #         # the target location will always be off by some amount, e.g. always 2 over.
        #         # move_action = MoveAction(1, (int(tile_pos_y), int(tile_pos_x)))
        #         self.view_manager.reset_keyboard()
        #         self.accept_mouse_input = False
        #         self.server_client.post_user_input(f"{tile_pos_y}, {tile_pos_x}")
        #         # self.action_queue.enqueue(move_action)

    def draw(self):
        """everything in the tasks draws itself,
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
