import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.models.board import Board
    from backend.models.character import Character


@dataclass
class Action(abc.ABC):
    @abc.abstractmethod
    def perform(self, backend_engine: "Board"):
        pass


@dataclass
class MoveAction(Action):
    """
    Moves a player or entity on the backend game map.

    Relies on backend for pathfinding.
    """

    character_id: int
    destination_map_tile_coord: tuple[int, int]

    def perform(self, backend_engine: "Board", acting_character: "Character"):
        print(f"{self.destination_map_tile_coord=}")
        backend_engine.move_character_toward_location(
            acting_character, self.destination_map_tile_coord, 99
        )
