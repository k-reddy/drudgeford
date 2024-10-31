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

    def perform_attack(self, attacker, board, round_num: int):
        # if it's not an area of effect card, do a normal attack
        if not self.attack_shape:
            in_range_opponents = board.find_in_range_opponents(
                attacker, self
            )
            target = attacker.select_attack_target(in_range_opponents)
            self.perform_attack_card(board, attacker, target, round_num)
        else:
            board.attack_area(attacker, self.attack_shape, self.strength)

    def perform_attack_card(
        self, board, attacker, target, round_num: int
    ) -> None:
        if target is None or (
            not board.is_attack_in_range(self.distance, attacker, target)
        ):
            board.log.append("Not close enough to attack")
            return

        board.log.append(f"{attacker.name} is attempting to attack {target.name}")

        if self.status_effect and self.status_shape:
            board.log.append(f"{attacker.name} is performing {self.attack_name}!")
            row, col = board.find_location_of_target(target)
            board.log.append(f"{attacker.name} throws {self.status_effect}")
            board.add_effect_to_terrain_for_attack(
                self.status_effect.upper(), row, col, self.status_shape, round_num
            )
        # some cards have no attack, don't want to attack if we hit a good modifier
        if self.strength == 0:
            return
        board.attack_target(attacker, self.strength, target)

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