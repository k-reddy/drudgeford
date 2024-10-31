from dataclasses import dataclass
import attack_shapes as shapes
import abc 
import utils


@dataclass
class ActionStep(abc.ABC):
    @abc.abstractmethod
    def perform(self, board, attacker, round_num):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

@dataclass
class AreaAttack(ActionStep):
    shape: set
    strength: int

    def perform(self, board, attacker, round_num):
        board.attack_area(attacker, self.shape, self.strength)

    def __str__(self):
        return f"Area Attack Strength {self.strength} with Shape:\n{shapes.print_shape(self.shape)}"

@dataclass
class SingleTargetAttack(ActionStep):
    strength: int
    att_range: int

    def perform(self, board, attacker, round_num):
        in_range_opponents = board.find_in_range_opponents(
            attacker, self.att_range
        )
        target = attacker.select_attack_target(in_range_opponents)
        if target is not None:
            board.attack_target(attacker, self.strength, target)
        else:
            board.log.append("No targets in range")

    def __str__(self):
        return f"Single Target Attack with Strength {self.strength}, Range {self.att_range}"

@dataclass
class ElementAreaEffect(ActionStep):
    shape: set
    element: str
    att_range: int

    def perform(self, board, attacker, round_num):
        in_range_opponents = board.find_in_range_opponents(
            attacker, self.att_range
        )
        target = attacker.select_attack_target(in_range_opponents)
        if target is not None:
            row, col = board.find_location_of_target(target)
            board.log.append(f"{attacker.name} throws {self.element}")
            board.add_effect_to_terrain_for_attack(
                self.element.upper(), row, col, self.shape, round_num
            )
        else:
            board.log.append("No target in range")

    def __str__(self):
        return f"{self.element} Attack with Range {self.att_range} and Shape:\n{shapes.print_shape(self.shape)}"

@dataclass
class Teleport(ActionStep):
    att_range: int

    def perform(self, board, attacker, round_num):
        in_range_opponents = board.find_in_range_opponents(
            attacker, self.att_range
        )
        target = attacker.select_attack_target(in_range_opponents)
        if target is not None:
            board.teleport_character(target)

    def __str__(self):
        return f"Teleport Another Character in range {self.att_range}"

@dataclass
class ChargeNextAttack(ActionStep):
    strength: int

    def perform(self, board, attacker, round_num):
        modifier = utils.make_additive_modifier(2)
        attacker.attack_modifier_deck.insert(0,modifier)

    def __str__(self):
        return f"Charge next attack {self.strength}"

@dataclass
class ActionCard:
    attack_name: str
    actions: list[ActionStep]
    movement: int
    jump: bool

    # actions = [single_target_attack, area_of_attack, status_effect]
    def perform_attack(self, attacker, board, round_num: int):
        for action in self.actions:
            board.log.append(f"{attacker.name} is performing {action}!")
            action.perform(board, attacker, round_num)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)
    
    def __str__(self):
        print_str = f"{self.attack_name}, Movement {self.movement}"
        if self.jump:
            print_str+= ", Jump"
        for action in self.actions:
            print_str+=f"\n\t{action}"
        return print_str
    