import pyxel
import random

from collections import defaultdict, deque
import itertools
from statistics import mean
import time

from .enums import AnimationFrame
from .models.action_task import ActionTask
from .models.update_tasks import AddEntityTask, RemoveEntityTask

# from .models.system_task import SystemTask
from pyxel_ui.models.pyxel_task_queue import PyxelTaskQueue
from .models.canvas import Canvas
from .models.entity import Entity
from .models.walls import Wall
from .utils import BACKGROUND_TILES, generate_wall_bank
from .views.sprite import Sprite, SpriteManager


WALL_THICKNESS = 32
GRID_COLOR =0
FRAME_DURATION_MS = 34
# approx 2 sec of durations with no movement
WINDOW_LENGTH = 60
BITS = 32


# phase 1, generate play space based on 64x64 character. add wall boundaries
# phase 2, create move queue and read from them to move character around on grid
# phase 3, integrate with GH backend - set up new task types for use with message queue
# phase 4, start UI, allow for mouse hover to highlight grid boxes
# phase 5, add log and be able to write to it.
# phase 6, add way to dynamically shape walls as obstacles.

# TODO(john): track curr framerate to keep consistent move speeds
# this will be a bit tricky since we need to be aware of how movement
# affects framerate. could track high-low based on game states wait/move/log/effect
# TODO: limit re-draw to areas that will change.


def draw_tile(x, y, img_bank, u, v, w, h, colkey=0):
    pyxel.blt(x, y, img_bank, u, v, w, h, colkey)

class PyxelView:
    def __init__(self, task_queue: PyxelTaskQueue):
        # Init action queue system
        self.task_queue = task_queue
        self.current_task = None
        self.entities: dict[int, Entity] = {}
        self.sprite_manager = SpriteManager()
        self.is_board_initialized = False

        # To measure framerate and loop duration
        self.start_time: float = time.time()
        self.loop_durations: deque[float] = deque(maxlen=WINDOW_LENGTH)

    def init_pyxel_map(self, width, height, valid_floor_coordinates):
        self.board_tile_width = width
        self.board_tile_height = height
        self.valid_floor_coordinates=valid_floor_coordinates

        # TODO(John): replace these hardcoded numbers.
        pyxel.init(self.board_tile_width * BITS + 32, self.board_tile_height * BITS + 64)
        pyxel.load("../my_resource.pyxres")

        self.canvas = Canvas(
            board_tile_width=self.board_tile_width,
            board_tile_height=self.board_tile_height,
            tile_width_px=BITS,
            tile_height_px=BITS,
            wall_sprite_thickness_px=WALL_THICKNESS,
        )

        self.dungeon_walls = generate_wall_bank(self.canvas)

    def start(self):
        print("Starting Pyxel game loop...")
        # init pyxel canvas and map that align with those of GH backend
        # canvas + map = board
        while not self.is_board_initialized:
            if not self.current_task and not self.task_queue.is_empty():
                self.current_task = self.task_queue.dequeue()
                self.process_board_initialization_task()
                self.process_entity_loading_task()
                # self.process_add_entity_task()
                self.current_task = None  # clear
                self.is_board_initialized = True

        pyxel.run(self.update, self.draw)

    def draw_sprite(self, x: int, y: int, sprite: Sprite, colkey=0) -> None:
        pyxel.blt(x, y, sprite.img_bank, sprite.u, sprite.v, sprite.w, sprite.h, colkey)

    def draw_background(self, floor_tile_keys, valid_map_coordinates):
        directions = [
            {
                "coord": (1,0),
                "wall_tile_name": "new_wall_ns",
                "height": 32,
                "width": 4
             },
            {
                "coord": (-1,0),
                "wall_tile_name": "new_wall_ns",
                "height": 32,
                "width": 4
             },
             {
                "coord": (0,1),
                "wall_tile_name": "new_wall_ew",
                "height": 4,
                "width": 32
             },
             {
                "coord": (0,-1),
                "wall_tile_name": "new_wall_ew",
                "height": 4,
                "width": 32
             },
        ]

        # offset the map by wall thickness in x and y directions
        # draw the floor tiles where they belong
        # leave space for the walls and draw the floor
        floor_start_x = self.canvas.board_start_pos[0]
        floor_start_y = self.canvas.board_start_pos[1]

        # ensure we get the same floor tiles each time we draw the floor
        random.seed(100)

        for (x,y) in valid_map_coordinates:
            x_px = x*self.canvas.tile_width_px+ floor_start_x 
            y_px = y*self.canvas.tile_height_px + floor_start_y
            floor_tile = BACKGROUND_TILES[random.choice(floor_tile_keys)]

            draw_tile(x_px,y_px,**floor_tile)
        # come back through and draw the walls
        for (x,y) in valid_map_coordinates:
            x_px = x*self.canvas.tile_width_px+ floor_start_x 
            y_px = y*self.canvas.tile_height_px + floor_start_y
            for direction in directions:
                new_coord = tuple(a+b for a,b in zip((x,y), direction["coord"]))
                if new_coord in valid_map_coordinates:
                    continue
                x_px_new = x_px + self.canvas.tile_width_px*direction["coord"][0] if direction["coord"][0] > 0 else x_px + direction["width"]*direction["coord"][0]
                y_px_new = y_px + self.canvas.tile_height_px*direction["coord"][1] if direction["coord"][1] > 0 else y_px + direction["height"]*direction["coord"][1]
                draw_tile(
                    x_px_new,
                    y_px_new,
                    **BACKGROUND_TILES[direction["wall_tile_name"]],
                )

    def convert_grid_to_pixel_pos(self, tile_x: int, tile_y: int) -> tuple[int, int]:
        """Converts grid-based tile coordinates to pixel coordinates on the canvas."""
        pixel_x = self.canvas.board_start_pos[0] + (tile_x * self.canvas.tile_width_px)
        pixel_y = self.canvas.board_start_pos[1] + (tile_y * self.canvas.tile_height_px)
        return (pixel_x, pixel_y)

    def get_px_move_steps_between_tiles(
        self,
        start_tile_pos: tuple[int, int],
        end_tile_pos: tuple[int, int],
        tween_time: int,
    ) -> deque[tuple[int, int]]:
        """
        Calculates the pixel-based steps for movement between two tiles.

        Movement is broken into discrete steps, where the number of steps determines
        the speed of the animation. The steps are stored as tuples of (x, y) pixel coordinates.
        """
        assert tween_time > FRAME_DURATION_MS, "ActionTask smaller than frame rate"

        start_px_x, start_px_y = self.convert_grid_to_pixel_pos(*start_tile_pos)
        end_px_x, end_px_y = self.convert_grid_to_pixel_pos(*end_tile_pos)

        step_count = tween_time // FRAME_DURATION_MS
        diff_px_x = end_px_x - start_px_x
        diff_px_y = end_px_y - start_px_y

        return deque(
            (
                int(start_px_x + i / step_count * (diff_px_x)),
                int(start_px_y + i / step_count * (diff_px_y)),
            )
            for i in range(step_count + 1)
        )

    def convert_and_append_move_steps_to_action(self, action: ActionTask) -> ActionTask:
        """
        Converts grid-based movement coordinates into pixel-based steps and
        appends them to the action.
        """
        action.action_steps = self.get_px_move_steps_between_tiles(
            action.from_grid_pos, action.to_grid_pos, action.duration_ms
        )
        return action

    def process_action(self) -> None:
        assert self.current_task, "Attempting to process empty action"
        # print(f"{self.current_task.action_steps=}")

        if not self.current_task.action_steps:
            # print("ActionTask processing complete. Clearing...")
            self.current_task = None  # better than del; no dangling logic
            return

        px_pos_x, px_pos_y = self.current_task.action_steps.popleft()
        self.entities[self.current_task.entity_id].update_position(px_pos_x, px_pos_y)

    def process_remove_entity_task(self) -> None:
        assert self.current_task, "Attempting to process empty system task"
        del self.entities[self.current_task.entity_id]
        self.current_task = None 

    def process_board_initialization_task(self) -> None:
        assert self.current_task, "Attempting to process empty system task"
        height = self.current_task.payload["map_height"]
        width = self.current_task.payload["map_width"]
        valid_floor_coordinates = self.current_task.payload["valid_floor_coordinates"]
        self.init_pyxel_map(width, height, valid_floor_coordinates)

    def process_entity_loading_task(self) -> None:
        assert self.current_task, "Attempting to process empty system task"
        for entity in self.current_task.payload["entities"]:
            row_px, col_px = self.convert_grid_to_pixel_pos(
                entity["position"][0],
                entity["position"][1],
            )

            self.entities[entity["id"]] = Entity(
                id=entity["id"],
                name=entity["name"],
                x=row_px,
                y=col_px,
                z=10,
                priority=entity["priority"],
                animation_frame=AnimationFrame.SOUTH,
                alive=True,
            )
            
        # currently assuming payload is board.locations

    def update(self):
        self.start_time = time.time()
        # make a pyxel board with the right shape
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if not self.is_board_initialized:
            return
        # Check for new tasks here
        if not self.current_task and not self.task_queue.is_empty():
            temp_task = self.task_queue.dequeue()
            if isinstance(temp_task, ActionTask):
                self.current_task = self.convert_and_append_move_steps_to_action(
                    temp_task
                )
                # print(f"Has new action: {self.current_task}")
                return
            else:
                self.current_task = temp_task
                return

        if self.current_task:
            if isinstance(self.current_task, ActionTask):
                self.process_action()
            elif isinstance(self.current_task, RemoveEntityTask):
                self.process_remove_entity_task()
            elif isinstance(self.current_task, AddEntityTask):
                self.process_entity_loading_task()
                self.current_task=None
            

    def draw(self):
        pyxel.cls(0)
        dungeon_floor_tiles = [f"dungeon_floor_cracked_{i}" for i in range(1,13)]

        self.draw_background(dungeon_floor_tiles, self.valid_floor_coordinates)

        # draw grid only on valid floor coordinates
        for x, y in self.valid_floor_coordinates:
            pyxel.rectb(
                x*self.canvas.tile_width_px+self.canvas.board_start_pos[0],
                y*self.canvas.tile_height_px+self.canvas.board_start_pos[1],
                self.canvas.tile_width_px,
                self.canvas.tile_height_px,
                GRID_COLOR
            )

        # draw entity sprites with a notion of priority
        max_priority = max((entity.priority for entity in self.entities.values()), default=0)
        for i in range(0,max_priority+1):
            for _, entity in self.entities.items():
                if entity.priority == i:
                    self.draw_sprite(
                        entity.x,
                        entity.y,
                        self.sprite_manager.get_sprite(entity.name, entity.animation_frame),
                    )

        # Draw framerate and frame duration.

        # Calculate duration and framerate
        loop_duration = time.time() - self.start_time
        self.loop_durations.append(loop_duration)

        if len(self.loop_durations) > 0:
            avg_duration = mean(self.loop_durations)
            loops_per_second = 1 / avg_duration if avg_duration > 0 else 0
            avg_duration_ms = avg_duration * 1000
            rate_stats = f"LPS: {loops_per_second:.2f} - DUR: {avg_duration_ms:.2f} ms"
            pyxel.text(10, 20, rate_stats, 7)
