from collections import deque

from pyxel_ui.models.entity import Entity
from pyxel_ui.models.canvas import Canvas
from pyxel_ui.models.action_task import ActionTask
from pyxel_ui.models.tasks import (
    AddEntitiesTask,
    RemoveEntityTask,
)
from pyxel_ui.constants import FRAME_DURATION_MS
from pyxel_ui.enums import AnimationFrame
from pyxel_ui.utils import generate_wall_bank
from pyxel_ui.controllers.view_manager import ViewManager
import time



class TaskProcessor:
    def __init__(self, canvas: Canvas, view_manager):
        self.canvas = canvas
        self.view_manager = view_manager

