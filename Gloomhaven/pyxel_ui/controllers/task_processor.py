from collections import deque

from pyxel_ui.models.entity import Entity
from pyxel_ui.models.canvas import Canvas
from pyxel_ui.models.action_task import ActionTask
from pyxel_ui.models.update_tasks import (
    AddEntityTask,
    RemoveEntityTask,
)
from pyxel_ui.constants import FRAME_DURATION_MS
from pyxel_ui.enums import AnimationFrame
from pyxel_ui.utils import generate_wall_bank


class TaskProcessor:
    def __init__(self, entities, canvas: Canvas):
        self.entities = entities
        self.canvas = canvas

    # Task processors
    def process_action(self, action_task: ActionTask) -> None:
        assert action_task, "Attempting to process empty action"
        if not action_task.action_steps:
            return

        px_pos_x, px_pos_y = action_task.action_steps.popleft()
        self.entities[action_task.entity_id].update_position(px_pos_x, px_pos_y)

    def process_entity_loading_task(self, entity_loading_task: AddEntityTask) -> None:
        assert entity_loading_task, "Attempting to process empty system task"
        for entity in entity_loading_task.payload["entities"]:
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

    def process_remove_entity_task(self, remove_entity_task: RemoveEntityTask) -> None:
        assert remove_entity_task, "Attempting to process empty system task"
        try:
            del self.entities[remove_entity_task.entity_id]
        except Exception as e:
            print(f"attempting to delete non-existent entity: {str(e)}")
            raise
        self.current_task = None

    # End task processors

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

    def convert_grid_to_pixel_pos(self, tile_x: int, tile_y: int) -> tuple[int, int]:
        """Converts grid-based tile coordinates to pixel coordinates on the canvas."""
        pixel_x = self.canvas.board_start_pos[0] + (tile_x * self.canvas.tile_width_px)
        pixel_y = self.canvas.board_start_pos[1] + (tile_y * self.canvas.tile_height_px)
        return (pixel_x, pixel_y)

    def convert_and_append_move_steps_to_action(self, action: ActionTask) -> ActionTask:
        action.action_steps = self.get_px_move_steps_between_tiles(
            action.from_grid_pos, action.to_grid_pos, action.duration_ms
        )
        return action

    def init_pyxel_map(
        self,
        width: int,
        height: int,
        valid_floor_coordinates: list[tuple[int, int]],
    ) -> None:
        """
        Initializes the Pyxel map with the given dimensions and valid floor coordinates.
        """
        self.canvas.board_tile_width = width
        self.canvas.board_tile_height = height
        self.valid_floor_coordinates = set(valid_floor_coordinates)
        # Additional initialization if needed
        self.dungeon_walls = generate_wall_bank(self.canvas)
