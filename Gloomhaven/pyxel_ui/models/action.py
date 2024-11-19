from dataclasses import dataclass
import abc


@dataclass
class Action(abc.ABC):
    @abc.abstractmethod
    def perform(self):
        pass


@dataclass
class MoveAction(Action):
    """
    Moves a player or entity on the backend game map.

    Relies on backend for pathfinding.
    """

    character_id: int
    destination_map_tile_coord: tuple[int, int]

    def perform(self):
        print(f"moving to {self.destination_map_tile_coord}")
