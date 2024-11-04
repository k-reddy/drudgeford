from dataclasses import dataclass

@dataclass
class AddEntityTask:
    """
    A task that tells pyxel to load an entity onto the game map.

    Payload Dict has one entry, "entities", which is a list of dicts with:
        - entity_id - unique id for the entity
        - position - where on the map to put the entity
        - sprite_name - name of the sprite to display for the entity
        - priority - kind of a "z" index, with higher numbers showing up on top
            when the map draws
    """
    payload: dict

@dataclass
class RemoveEntityTask:
    """
    A task that tells pyxel to remove an entity from the game map.
    Pyxel will have no record of that entity going forward
    """
    entity_id: int

@dataclass
class LoadCharactersTask:
    '''
    A task that tells pyxel to update the characters/healths/ordering in the
    initiative bar
    '''
    healths: list[int]
    sprite_names: list[str]
    teams: list[bool]

