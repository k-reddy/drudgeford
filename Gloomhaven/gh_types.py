from dataclasses import dataclass


@dataclass
class ActionCard:
    attack_name: str
    strength: int
    distance: int
    movement: int
    status_effect: str | None
    radius: int | None

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)
    
    def __str__(self):
        str = f"{self.attack_name}: Strength {self.strength}, Range {self.distance}, Movement {self.movement}"
        if self.status_effect:
            str += f"\n\tStatus Effect: {self.status_effect} with Radius {self.radius}"
        return str