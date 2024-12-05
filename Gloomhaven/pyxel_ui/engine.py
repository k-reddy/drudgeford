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
from .models.tasks import ActionTask, ShowCharacterPickerTask, InputTask, LoadCampaign
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
    def __init__(self, port, host):
        self.server_client = TCPClient(ClientType.FRONTEND, port=port, host=host)
        self.tj = TaskJsonifier()
        self.current_task = None

        # self.last_mouse_pos = (-1, -1)

        self.hover_grid = None

        # Controller
        self.view_manager = None
        # self.current_view_manager = None

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
        ui_time = time.time() - self.start_time
        get_task_time = -1
        unjsonify_time = -1
        perform_time = -1
        start_time = time.time()
        if not self.current_task:
            jsonified_task = self.server_client.get_task()
            get_task_time = time.time() - start_time
            start_time = time.time()

            self.current_task = self.tj.make_task_from_json(jsonified_task)
            unjsonify_time = time.time() - start_time

        if self.current_task:
            start_time = time.time()
            task_output = self.current_task.perform(
                self.view_manager, self.keyboard_manager
            )
            # don't clear the task if it's an action task and has steps to do
            if (
                isinstance(self.current_task, ActionTask)
                and self.current_task.action_steps
            ):
                return
            # if we're asked for a campaign, send what we get to the server
            elif isinstance(self.current_task, LoadCampaign):
                self.server_client.post_user_input(task_output)
            self.current_task = None
            perform_time = time.time() - start_time
        print("------")
        print(f"ui time: {ui_time}")
        print(f"perform time: {perform_time}")
        print(f"get_task_time : {get_task_time}")
        print(f"unjsonify time: {unjsonify_time}")
        print("------")

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
