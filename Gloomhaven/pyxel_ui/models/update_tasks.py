from dataclasses import dataclass
from pyxel_ui.controllers.view_manager import ViewManager

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

    def perform(self, view_manager: ViewManager):
        view_manager.remove_entity(self.entity_id)

@dataclass
class LoadCharactersTask:
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
class LoadLogTask:
    '''
    task that updates the pyxel log
    '''
    log: list[str]

    def perform(self, view_manager: ViewManager):
        view_manager.update_log(self.log)

@dataclass
class LoadActionCardsTask:
    '''
    task that updates the action cards area
    '''
    action_card_log: list[str]

    def perform(self, view_manager: ViewManager):
        view_manager.update_action_card_log(self.action_card_log)

@dataclass
class LoadRoundTurnInfoTask:
    '''
    task that updates the round number and who's turn it is
    '''
    round_number: int
    acting_character_name: str
    
    def perform(self, view_manager: ViewManager):
        view_manager.update_round_turn(self.round_number, self.acting_character_name)
