from dataclasses import dataclass

@dataclass
class AddEntityTask:
    """
    A task that tells pyxel to load an entity onto the game map.

    Attributes:
        - entity_id - unique id for the entity
        - position - where on the map to put the entity
        - sprite_name - name of the sprite to display for the entity
        - priority - kind of a "z" index, with higher numbers showing up on top
            when the map draws
    """
    entity_id: int
    position: tuple[int, int]
    sprite_name: str
    priority: int

@dataclass
class RemoveEntityTask:
    """
    A task that tells pyxel to remove an entity from the game map.
    Pyxel will have no record of that entity going forward
    """
    entity_id: int