from dataclasses import dataclass


@dataclass
class ActionCard:
    attack_name: str
    strength: int
    distance: int
    movement: int

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)
