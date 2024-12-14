from dataclasses import dataclass
import abc
import random
from functools import partial
from typing import Type, Optional

from . import obstacle
from ..utils import utilities as utils
from ..utils import attack_shapes as shapes


@dataclass
class ActionStep(abc.ABC):
    @abc.abstractmethod
    def perform(self, board, attacker, round_num):
        pass

    @abc.abstractmethod
    def __str__(self):
        pass

    def perform_string(self, attacker):
        return f"{attacker.name} is performing {self}"


@dataclass
class AreaAttackFromSelf(ActionStep):
    shape: set
    strength: Optional[int] = None
    element_type: Optional[Type[obstacle.TerrainObject]] = None

    def perform(self, board, attacker, round_num):
        # first create the attack coordinates from the shape (offsets)
        starting_coord = board.find_location_of_target(attacker)
        attack_coords = attacker.pick_rotated_attack_coordinates(
            board, self.shape, starting_coord
        )
        if self.strength:
            board.attack_area(attacker, attack_coords, self.strength)
        if self.element_type:
            board.add_effect_to_terrain_for_attack(self.element_type, attack_coords)

    def __str__(self):
        attack_type = f"{self.element_type.__name__} " if self.element_type else ""
        damage_str = f" {self.strength}" if self.strength else ""
        return f"{attack_type}Attack{damage_str}:\n{shapes.print_shape(self.shape)}"

    def perform_string(self, attacker):
        if self.element_type:
            return f"{attacker.name} throws {self.element_type.__name__}"
        else:
            return ""


@dataclass
class SingleTargetAttack(ActionStep):
    strength: int
    att_range: int
    knock_down: bool = False
    pierce: bool = False

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range)
        if target is not None:
            if self.knock_down and random.random() < 0.5:
                target.lose_turn = True
                board.pyxel_manager.log.append(f"{target.name} was knocked down")
            elif self.knock_down:
                board.pyxel_manager.log.append("Knock down failed")
            board.attack_target(attacker, self.strength, target, pierce=self.pierce)
        else:
            board.pyxel_manager.log.append("No targets in range for attack")

    def __str__(self):
        range_str = f" <{self.att_range}>" if self.att_range > 1 else ""
        print_str = f"Attack {self.strength}{range_str}"
        print_str += "\nKnock down (50%)" if self.knock_down else ""
        return print_str

    def perform_string(self, attacker):
        return ""


@dataclass
class AreaAttackWithTarget(ActionStep):
    shape: set
    att_range: int
    damage: Optional[int] = None
    element_type: Optional[Type[obstacle.TerrainObject]] = None

    def perform(self, board, attacker, round_num):
        attacker_loc = board.find_location_of_target(attacker)
        if shapes.is_circle(self.shape):
            self.shape.add((0, 0))
        else:
            self.shape.discard((0, 0))
        rotated_offset_shape = attacker.pick_rotated_attack_coordinates(
            board, self.shape, attacker_loc, from_self=False
        )
        # remove attacker_loc
        rotated_shape = [
            (row - attacker_loc[0], col - attacker_loc[1])
            for (row, col) in rotated_offset_shape
        ]
        target_row, target_col = attacker.select_board_square_target(
            board, self.att_range, rotated_shape
        )
        # if we don't get a target, return
        if target_row is None:
            board.pyxel_manager.log.append("No target in range")
            return

        attack_coords = [
            (row + target_row, col + target_col) for (row, col) in rotated_shape
        ]
        # if we're given damage, perform a damage attack
        if self.damage:
            board.attack_area(attacker, attack_coords, self.damage)

        # if we're given an element, add elements to board
        if self.element_type:
            board.add_effect_to_terrain_for_attack(self.element_type, attack_coords)

    def __str__(self):
        attack_type = f"{self.element_type.__name__} " if self.element_type else ""
        damage_str = f" {self.damage}" if self.damage else ""
        return f"{attack_type}Attack{damage_str} <{self.att_range}>:\n{shapes.print_shape(self.shape)}"

    def perform_string(self, attacker):
        if self.element_type:
            return f"{attacker.name} throws {self.element_type.__name__}"
        else:
            return ""


@dataclass
class Teleport(ActionStep):
    att_range: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range)

        if target is not None:
            board.teleport_character(target)

    def __str__(self):
        return f"Teleport Enemy <{self.att_range}>"

    def perform_string(self, attacker):
        return ""


@dataclass
class Fortify(ActionStep):
    strength: int

    def perform(self, board, attacker, round_num):
        modifier = utils.make_additive_modifier(self.strength)
        attacker.attack_modifier_deck.append(modifier)

    def __str__(self):
        return f"Fortify self by {self.strength}"

    def perform_string(self, attacker):
        return f"+{self.strength} -> {attacker.name}'s [{len(attacker.attack_modifier_deck)}]"


@dataclass
class WeakenEnemy(ActionStep):
    strength: int
    att_range: int

    def perform(self, board, attacker, round_num):
        modifier = utils.make_additive_modifier(-self.strength)
        target = select_in_range_target(board, attacker, self.att_range, opponent=True)
        # if no one is in range, return
        if not target:
            return
        target.attack_modifier_deck.append(modifier)
        board.pyxel_manager.log.append(f"Weakened {target.name} by {self.strength}")

    def __str__(self):
        return f"Weaken enemy by {self.strength} <{self.att_range}>"

    def perform_string(self, attacker):
        return ""


@dataclass
class WeakenAllEnemies(ActionStep):
    strength: int
    att_range: int

    def perform(self, board, attacker, round_num):
        enemies = board.find_in_range_opponents_or_allies(
            attacker, self.att_range, opponents=True
        )
        for enemy in enemies:
            modifier = utils.make_additive_modifier(-self.strength)
            enemy.attack_modifier_deck.append(modifier)
            board.pyxel_manager.log.append(f"{enemy.name}")

    def __str__(self):
        return f"Weaken all enemies by -{self.strength} <{self.att_range}>"

    def perform_string(self, attacker):
        return f"{attacker.name} weakens all enemies by -{self.strength}:"


@dataclass
class ShieldSelf(ActionStep):
    strength: int
    duration: int

    def perform(self, board, attacker, round_num):
        attacker.shield = (self.strength, round_num + self.duration)

    def __str__(self):
        return f"Shield {self.strength}, {self.duration} turn{'s' if self.duration>1 else ''}"

    def perform_string(self, attacker):
        return f"{attacker.name} shields {self.strength} self, {self.duration} turn{'s' if self.duration>1 else ''}"


@dataclass
class ShieldAllAllies(ActionStep):
    strength: int
    duration: int
    att_range: int

    def perform(self, board, attacker, round_num):
        in_range_allies = board.find_in_range_opponents_or_allies(
            attacker, self.att_range, opponents=False
        )
        for ally in in_range_allies:
            ally.shield = (self.strength, round_num + self.duration)
            board.pyxel_manager.log.append(f"{ally.name}")

    def __str__(self):
        return f"Shield {self.strength} all allies <{self.att_range}>, {self.duration} turns"

    def perform_string(self, attacker):
        return f"Shield {self.strength}, {self.duration} turn{'s' if self.duration >1 else ''} these allies:"


@dataclass
class ModifySelfHealth(ActionStep):
    strength: int

    def perform(self, board, attacker, round_num):
        board.modify_target_health(attacker, -self.strength)

    def __str__(self):
        if self.strength > 0:
            return f"Heal {self.strength}"
        else:
            return f"Take {-self.strength} damage"

    def perform_string(self, attacker):
        return ""


@dataclass
class HealAlly(ActionStep):
    strength: int
    att_range: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range, False)
        board.modify_target_health(target, -self.strength)

    def __str__(self):
        return f"Heal ally {self.strength} <{self.att_range}>"

    def perform_string(self, attacker):
        return ""


@dataclass
class HealAllAllies(ActionStep):
    strength: int
    att_range: int

    def perform(self, board, attacker, round_num):
        in_range_allies = board.find_in_range_opponents_or_allies(
            attacker, self.att_range, opponents=False
        )
        for ally in in_range_allies:
            board.modify_target_health(ally, -self.strength)

    def __str__(self):
        return f"Heal all allies {self.strength} <{self.att_range}>"

    def perform_string(self, attacker):
        return ""


@dataclass
class BlessSelf(ActionStep):
    def perform(self, board, attacker, round_num):
        rand_index = random.randint(0, len(attacker.attack_modifier_deck))
        modifier = utils.make_multiply_modifier(2, "2x Bless")
        attacker.attack_modifier_deck.insert(rand_index, modifier)

    def __str__(self):
        return "Bless self"

    def perform_string(self, attacker):
        return f"2x -> {attacker.name}'s [{len(attacker.attack_modifier_deck)}]"


@dataclass
class BlessAndFortifyAlly(ActionStep):
    att_range: int
    strength: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range, opponent=False)
        rand_index = random.randint(0, len(target.attack_modifier_deck))
        bless = utils.make_multiply_modifier(2, "2x Bless")
        modifier = utils.make_additive_modifier(self.strength)
        target.attack_modifier_deck.insert(rand_index, bless)
        target.attack_modifier_deck.append(modifier)
        board.pyxel_manager.log.append(
            f"+{self.strength} and 2x -> {target.name}'s [{len(target.attack_modifier_deck)}]"
        )

    def __str__(self):
        return f"Bless and fortify +{self.strength} ally <{self.att_range}>"

    def perform_string(self, attacker):
        return ""


@dataclass
class BlessAllAllies(ActionStep):
    att_range: int

    def perform(self, board, attacker, round_num):
        in_range_allies = board.find_in_range_opponents_or_allies(
            attacker, self.att_range, opponents=False
        )
        for ally in in_range_allies:
            rand_index = random.randint(0, len(ally.attack_modifier_deck))
            modifier = utils.make_multiply_modifier(2, "2x Bless")
            ally.attack_modifier_deck.insert(rand_index, modifier)
            board.pyxel_manager.log.append(f"Blessed {ally.name}")

    def __str__(self):
        return f"Bless all allies <{self.att_range}>"

    def perform_string(self, attacker):
        return ""


@dataclass
class Curse(ActionStep):
    att_range: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range, opponent=True)
        if not target:
            return
        rand_index = random.randint(0, len(target.attack_modifier_deck))
        modifier = utils.make_multiply_modifier(0, "Null Curse")
        target.attack_modifier_deck.insert(rand_index, modifier)
        board.pyxel_manager.log.append(
            f"Null -> {target.name}'s [{len(target.attack_modifier_deck)}]"
        )

    def __str__(self):
        return f"Curse enemy <{self.att_range}>"

    def perform_string(self, attacker):
        return ""


@dataclass
class CurseSelf(ActionStep):
    def perform(self, board, attacker, round_num):
        rand_index = random.randint(0, len(attacker.attack_modifier_deck))
        modifier = utils.make_multiply_modifier(0, "Null Curse")
        attacker.attack_modifier_deck.insert(rand_index, modifier)

    def __str__(self):
        return "Curse self"

    def perform_string(self, attacker):
        return f"Null -> {attacker.name}'s [{len(attacker.attack_modifier_deck)}]"


@dataclass
class CurseAllEnemies(ActionStep):
    att_range: int

    def perform(self, board, attacker, round_num):
        enemies = board.find_in_range_opponents_or_allies(
            attacker, self.att_range, opponents=True
        )
        for enemy in enemies:
            rand_index = random.randint(0, len(enemy.attack_modifier_deck))
            modifier = utils.make_multiply_modifier(0, "Null Curse")
            enemy.attack_modifier_deck.insert(rand_index, modifier)
            board.pyxel_manager.log.append(
                f"Null -> {enemy.name}'s[{len(enemy.attack_modifier_deck)}]"
            )

    def __str__(self):
        return f"Curse all enemies <{self.att_range}>"

    def perform_string(self, attacker):
        return ""


@dataclass
class Pull(ActionStep):
    squares: int
    att_range: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range)

        if not target:
            board.pyxel_manager.log.append("No one in range to pull")
            return

        board.pyxel_manager.log.append(f"Pulling {target.name}")

        is_legal_pull_check = partial(
            check_if_legal_pull, board.find_location_of_target(attacker), board
        )

        attacker.agent.move_other_character(
            target,
            board.find_location_of_target(attacker),
            self.squares,
            False,
            board,
            is_legal_pull_check,
            attacker.client_id,
        )
        board.pyxel_manager.log.append("Pull completed")

    def __str__(self):
        return f"Pull {self.squares} <{self.att_range}>"

    def perform_string(self, attacker):
        return ""


@dataclass
class Push(ActionStep):
    squares: int
    att_range: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range)

        if not target:
            board.pyxel_manager.log.append("No one in range to push")
            return

        board.pyxel_manager.log.append(f"Pushing {target.name}")

        is_legal_push_check = partial(
            check_if_legal_push, board.find_location_of_target(attacker), board
        )

        attacker.agent.move_other_character(
            target,
            board.find_location_of_target(attacker),
            self.squares,
            False,
            board,
            is_legal_push_check,
            attacker.client_id,
            is_push=True,
        )
        board.pyxel_manager.log.append("Push completed")

    def __str__(self):
        return f"Push {self.squares} <{self.att_range}>"

    def perform_string(self, attacker):
        return ""


@dataclass
class PushAllEnemies(ActionStep):
    squares: int
    att_range: int

    def perform(self, board, attacker, round_num):
        enemies = board.find_in_range_opponents_or_allies(
            attacker, self.att_range, opponents=True
        )
        if not enemies:
            board.pyxel_manager.log.append("No one in range to push")
            return

        attacker_loc = board.find_location_of_target(attacker)
        is_legal_push_check = partial(check_if_legal_push, attacker_loc, board)

        for enemy in enemies:
            board.pyxel_manager.log.append(f"Pushing {enemy.name}")

            attacker.agent.move_other_character(
                enemy,
                attacker_loc,
                self.squares,
                False,
                board,
                is_legal_push_check,
                attacker.client_id,
                is_push=True,
            )

    def __str__(self):
        return f"Push {self.squares} all enemies <{self.att_range}>"

    def perform_string(self, attacker):
        return ""


@dataclass
class SummonSkeleton(ActionStep):

    def perform(self, board, attacker, round_num):
        from backend.models.character import Skeleton

        board.add_new_ai_char(attacker.team_monster, Skeleton)

    def __str__(self):
        return "Summon a skeleton"

    def perform_string(self, attacker):
        return f"{attacker.name} summons a skeleton"


@dataclass
class SummonPuppet(ActionStep):
    def perform(self, board, attacker, round_num):
        from backend.models.character import Puppet

        board.add_new_ai_char(attacker.team_monster, Puppet)

    def __str__(self):
        return "Summon a puppet"

    def perform_string(self, attacker):
        return f"{attacker.name} summons a puppet"


@dataclass
class MakeObstableArea(ActionStep):
    """Unlike elements, obstacles go on the locations board
    and cannot be moved through and do not expire"""

    obstacle_type: Type[obstacle.TerrainObject]
    shape: set

    def perform(self, board, attacker, round_num):
        starting_coordinate = board.find_location_of_target(attacker)
        board.set_obstacles_in_area(starting_coordinate, self.shape, self.obstacle_type)

    def __str__(self):
        return f"Set {self.obstacle_type.__name__}:\n{shapes.print_shape(self.shape)}"

    def perform_string(self, attacker):
        return f"{attacker.name} creates {self.obstacle_type.__name__}"


@dataclass
class MoveAlly(ActionStep):
    """Unlike elements, obstacles go on the locations board
    and cannot be moved through and do not expire"""

    squares: int
    att_range: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range, opponent=False)

        attacker.agent.move_other_character(
            target,
            board.find_location_of_target(attacker),
            self.squares,
            is_jump=False,
            board=board,
            movement_check=None,
            client_id=attacker.client_id,
        )
        board.pyxel_manager.log.append(f"Moved {target.name}")

    def __str__(self):
        return f"Move {self.squares} one ally <{self.att_range}>"

    def perform_string(self, attacker):
        return ""


@dataclass
class ActionCard:
    attack_name: str
    actions: list[ActionStep]
    movement: int
    jump: bool

    def perform_attack(self, attacker, board, round_num: int):
        for action in self.actions:
            action_log_line = action.perform_string(attacker)
            if action_log_line:
                board.pyxel_manager.log.append(action_log_line)
            action.perform(board, attacker, round_num)
            board.pyxel_manager.log.append("")

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __str__(self):
        print_str = f"{self.attack_name}\n"
        if self.movement != 0:
            print_str += "\nJump" if self.jump else "\nMove"
            print_str += f" {self.movement}\n"
        for action in self.actions:
            print_str += f"\n{action}"
        return print_str


def select_in_range_target(board, attacker, att_range, opponent=True):
    in_range_chars = board.find_in_range_opponents_or_allies(
        attacker, att_range, opponents=opponent
    )
    target = attacker.select_attack_target(in_range_chars, board, opponent=opponent)
    return target


def check_if_legal_pull(
    puller_location, board, pull_target_old_location, new_pull_target_location
):
    orig_dist = len(
        board.get_shortest_valid_path(pull_target_old_location, puller_location)
    )
    new_dist = len(
        board.get_shortest_valid_path(new_pull_target_location, puller_location)
    )

    if orig_dist > new_dist:
        return True
    else:
        return False


def check_if_legal_push(
    puller_location, board, pull_target_old_location, new_pull_target_location
):
    orig_dist = len(
        board.get_shortest_valid_path(pull_target_old_location, puller_location)
    )
    new_dist = len(
        board.get_shortest_valid_path(new_pull_target_location, puller_location)
    )

    if orig_dist < new_dist:
        return True
    else:
        return False
