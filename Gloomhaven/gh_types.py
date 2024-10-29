from dataclasses import dataclass
import attack_shapes as shapes

@dataclass
class ActionCard:
    attack_name: str
    attack_shape: set | None
    strength: int
    distance: int
    movement: int
    status_effect: str | None
    status_shape: set | None
    jump: bool

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)
    
    def __str__(self):
        print_str = f"{self.attack_name}: Strength {self.strength}, "
        if self.attack_shape:
            print_str += f"Shape:\n{shapes.print_shape(self.attack_shape)}"
        print_str += f"Range {self.distance}, Movement {self.movement}"
        if self.jump:
            print_str+= ", Jump"
        if self.status_effect:
            print_str += f"\n\tStatus Effect: {self.status_effect} with Shape:\n{shapes.print_shape(self.status_shape)}"
        return print_str