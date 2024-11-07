from dataclasses import dataclass
from collections import deque
from typing import Optional
import abc

from pyxel_ui.controllers.view_manager import ViewManager
from pyxel_ui.models.entity import Entity
from pyxel_ui.enums import AnimationFrame
from ..enums import Direction
from pyxel_ui.constants import FRAME_DURATION_MS


@dataclass
class Task(abc.ABC):
    @abc.abstractmethod
    def perform(self, view_manager: ViewManager):
        pass

@dataclass
class AddEntitiesTask(Task):
    """
    A task that tells pyxel to load an entity onto the game map.

    entities is a list of dicts with:
        - entity_id - unique id for the entity
        - position - where on the map to put the entity
        - sprite_name - name of the sprite to display for the entity
        - priority - kind of a "z" index, with higher numbers showing up on top
            when the map draws
    """
    entities: list

    def perform(self, view_manager: ViewManager):
        entities = {}
        for entity in self.entities:
            row_px, col_px = view_manager.convert_grid_to_pixel_pos(
                entity["position"][0],
                entity["position"][1],
            )

            entities[entity["id"]] = Entity(
                id=entity["id"],
                name=entity["name"],
                x=row_px,
                y=col_px,
                z=10,
                priority=entity["priority"],
                animation_frame=AnimationFrame.SOUTH,
                alive=True,
            )
        view_manager.update_sprites(entities)

@dataclass
class RemoveEntityTask(Task):
    """
    A task that tells pyxel to remove an entity from the game map.
    Pyxel will have no record of that entity going forward
    """
    entity_id: int

    def perform(self, view_manager: ViewManager):
        view_manager.remove_entity(self.entity_id)

@dataclass
class LoadCharactersTask(Task):
    '''
    A task that tells pyxel to update the characters/healths/ordering in the
    initiative bar
    '''
    healths: list[int]
    sprite_names: list[str]
    teams: list[bool]

    def perform(self, view_manager: ViewManager):
        view_manager.update_initiative_bar(self.sprite_names, self.healths, self.teams)

@dataclass
class LoadLogTask(Task):
    '''
    task that updates the pyxel log
    '''
    log: list[str]

    def perform(self, view_manager: ViewManager):
        view_manager.update_log(self.log)

@dataclass
class LoadActionCardsTask(Task):
    '''
    task that updates the action cards area
    '''
    action_card_log: list[str]

    def perform(self, view_manager: ViewManager):
        view_manager.update_action_card_log(self.action_card_log)

@dataclass
class LoadRoundTurnInfoTask(Task):
    '''
    task that updates the round number and who's turn it is
    '''
    round_number: int
    acting_character_name: str
    
    def perform(self, view_manager: ViewManager):
        view_manager.update_round_turn(self.round_number, self.acting_character_name)

# board init tasks are the only task that shouldn't be performed
# because they're only used to set up the board once
@dataclass
class BoardInitTask():
    """
    Initializes the board
    """
    map_height: int
    map_width: int
    valid_map_coordinates: list[tuple[int,int]]

@dataclass
class ActionTask(Task):
    """
    Represents an action performed by a entity in the game, including movement
    and animation details.

    Attributes:
        entity id (int)): The id of the entity performing the action.
        from_grid_pos (tuple): The starting position on the grid (x, y).
        to_grid_pos (tuple): The target position on the grid (x, y).
        duration_ms (int): The duration of the action in milliseconds (default is 1000 ms).
        action_steps (Optional[deque[tuple[int, int]]]): A sequence of pixel positions
            representing the path of the action (optional).
    """
    entity_id: int
    from_grid_pos: tuple
    to_grid_pos: tuple
    duration_ms: int = 1000
    action_steps: Optional[deque[tuple[int, int]]] = None

    def perform(self, view_manager):
        # if you don't have action steps, create them
        if not self.action_steps:
            self.action_steps = self.get_px_move_steps_between_tiles(view_manager)

        px_pos_x, px_pos_y = self.action_steps.popleft()
        # !!! yuck! fix this later 
        view_manager.map_view.entities[self.entity_id].update_position(px_pos_x, px_pos_y)
        view_manager.map_view.draw()

    def get_px_move_steps_between_tiles(
        self, view_manager: ViewManager
    ) -> deque[tuple[int, int]]:
        """
        Calculates the pixel-based steps for movement between two tiles.

        Movement is broken into discrete steps, where the number of steps determines
        the speed of the animation. The steps are stored as tuples of (x, y) pixel coordinates.
        """
        assert self.duration_ms > FRAME_DURATION_MS, "ActionTask smaller than frame rate"

        start_px_x, start_px_y = view_manager.convert_grid_to_pixel_pos(*self.from_grid_pos)
        end_px_x, end_px_y = view_manager.convert_grid_to_pixel_pos(*self.to_grid_pos)

        step_count = self.duration_ms // FRAME_DURATION_MS
        diff_px_x = end_px_x - start_px_x
        diff_px_y = end_px_y - start_px_y

        return deque(
            (
                int(start_px_x + i / step_count * (diff_px_x)),
                int(start_px_y + i / step_count * (diff_px_y)),
            )
            for i in range(step_count + 1)
        )