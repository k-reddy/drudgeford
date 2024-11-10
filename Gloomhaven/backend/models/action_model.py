from dataclasses import dataclass
import abc 
import random
from functools import partial
from typing import Type

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

@dataclass
class AreaAttack(ActionStep):
    shape: set
    strength: int

    def perform(self, board, attacker, round_num):
        board.attack_area(attacker, self.shape, self.strength)

    def __str__(self):
        return f"Area Attack\nStrength {self.strength}, Shape:\n{shapes.print_shape(self.shape)}"

@dataclass
class SingleTargetAttack(ActionStep):
    strength: int
    att_range: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range)
        if target is not None:
            board.attack_target(attacker, self.strength, target)
        else:
            board.pyxel_manager.log.append("No targets in range")

    def __str__(self):
        return f"Single Target Attack\nStrength {self.strength}\nRange {self.att_range}"

@dataclass
class ElementAreaEffectWithTarget(ActionStep):
    shape: set
    element_type: Type[obstacle.TerrainObject]
    att_range: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range)

        if target is not None:
            row, col = board.find_location_of_target(target)
            board.pyxel_manager.log.append(f"{attacker.name} throws {self.element_type.__name__}")
            board.add_effect_to_terrain_for_attack(
                self.element_type, row, col, self.shape
            )
        else:
            board.pyxel_manager.log.append("No target in range")

    def __str__(self):
        return f"{self.element_type.__name__} Attack\nRange {self.att_range} and Shape:\n{shapes.print_shape(self.shape)}"

@dataclass
class ElementAreaEffectFromSelf(ActionStep):
    shape: set
    element_type: Type[obstacle.TerrainObject]

    def perform(self, board, attacker, round_num):
        target = attacker

        row, col = board.find_location_of_target(target)
        board.pyxel_manager.log.append(f"{attacker.name} throws {self.element_type.__name__}")
        board.add_effect_to_terrain_for_attack(
            self.element_type, row, col, self.shape
        )

    def __str__(self):
        return f"{self.element_type.__name__} Attack\nShape:\n{shapes.print_shape(self.shape)}"

@dataclass
class Teleport(ActionStep):
    att_range: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range)

        if target is not None:
            board.teleport_character(target)

    def __str__(self):
        return f"Teleport Another Characte\nRange {self.att_range}"

@dataclass
class ChargeNextAttack(ActionStep):
    strength: int

    def perform(self, board, attacker, round_num):
        modifier = utils.make_additive_modifier(self.strength)
        attacker.attack_modifier_deck.append(modifier)

    def __str__(self):
        return f"Charge next attack {self.strength}"
    
@dataclass
class WeakenEnemy(ActionStep):
    strength: int
    att_range: int

    def perform(self, board, attacker, round_num):
        modifier = utils.make_additive_modifier(self.strength)
        target = select_in_range_target(board, attacker, self.att_range, opponent=True)
        # if no one is in range, return
        if not target:
            return
        target.attack_modifier_deck.append(modifier)

    def __str__(self):
        return f"Cause one enemy to\ndraw {self.strength} as next attack modifier\nRange {self.att_range}"

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
    
    def __str__(self):
        return f"Weaken all enemies by {self.strength}\nRange {self.att_range}"

@dataclass
class ShieldSelf(ActionStep):
    strength: int
    duration: int

    def perform(self, board, attacker, round_num):
        attacker.shield = (self.strength, round_num+self.duration)
    
    def __str__(self):
        return f"Shield {self.strength} self\n{self.duration} turns"

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
            ally.shield = (self.strength, round_num+self.duration)
    
    def __str__(self):
        return f"Shield {self.strength}\n all allies\nRange {self.att_range}, {self.duration} turns"
   
@dataclass
class ModifySelfHealth(ActionStep):
    strength: int

    def perform(self, board, attacker, round_num):
        board.modify_target_health(attacker, -self.strength)
    
    def __str__(self):
        if self.strength > 0:
            return f"Heal self for {self.strength}"
        else:
            return f"Take {self.strength} damage"

@dataclass
class HealAlly(ActionStep):
    strength: int
    att_range: int

    def perform(self, board, attacker, round_num):
        target=select_in_range_target(board, attacker, self.att_range, False)
        board.modify_target_health(target, -self.strength)
    
    def __str__(self):
        return f"Heal ally {self.strength}\nRange {self.att_range}"

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
        return f"Heal all allies for {self.strength}\nRange {self.att_range}"
@dataclass
class BlessSelf(ActionStep):
    def perform(self, board, attacker, round_num):
        rand_index = random.randint(0, len(attacker.attack_modifier_deck))
        modifier = utils.make_multiply_modifier(2, "2x Bless")
        attacker.attack_modifier_deck.insert(rand_index, modifier)
    
    def __str__(self):
        return "Bless self\nOne 2x modifier card"


@dataclass
class BlessAndChargeAlly(ActionStep):
    att_range: int
    strength: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range, opponent=False)
        rand_index = random.randint(0, len(target.attack_modifier_deck))
        bless = utils.make_multiply_modifier(2, "2x Bless")
        charge = utils.make_additive_modifier(self.strength)
        target.attack_modifier_deck.insert(rand_index, bless)
        target.attack_modifier_deck.append(charge)  
    
    def __str__(self):
        return f"Bless one ally\nRange {self.att_range}\nCharge their next attack +{self.strength}"
     
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
    
    def __str__(self):
        return f"Bless all allies\nRange {self.att_range}\nOne 2x modifier card each"

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
    
    def __str__(self):
        return f"Curse an enemy\nRange {self.att_range}\nOne null modifier card"

@dataclass
class CurseSelf(ActionStep):
    def perform(self, board, attacker, round_num):
        rand_index = random.randint(0, len(attacker.attack_modifier_deck))
        modifier = utils.make_multiply_modifier(0, "Null Curse")
        attacker.attack_modifier_deck.insert(rand_index, modifier)
    
    def __str__(self):
        return "Curse self\nOne null modifier card"

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
    
    def __str__(self):
        return f"Curse all enemies\nRange {self.att_range}"

@dataclass  
class Pull(ActionStep):
    squares: int
    att_range: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range)

        if not target:
            board.pyxel_manager.log.append("No one in range to pull")
            return
        
        is_legal_pull_check = partial(check_if_legal_pull, board.find_location_of_target(attacker), board)

        attacker.agent.move_other_character(
            target,
            board.find_location_of_target(attacker),
            self.squares,
            False,
            board,
            is_legal_pull_check
        )

    def __str__(self):
        return f"Pull {self.squares}\nAny enemy\nRange {self.att_range}"

@dataclass  
class Push(ActionStep):
    squares: int
    att_range: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range)

        if not target:
            board.pyxel_manager.log.append("No one in range to pull")
            return
        
        is_legal_push_check = partial(check_if_legal_push, board.find_location_of_target(attacker), board)
        
        attacker.agent.move_other_character(
            target,
            board.find_location_of_target(attacker),
            self.squares,
            False,
            board,
            is_legal_push_check
        )

    def __str__(self): 
        return f"Push {self.squares}\nAny enemy\nRange {self.att_range}"

@dataclass
class PushAllEnemies(ActionStep):
    squares: int
    att_range: int

    def perform(self, board, attacker, round_num):
        from .agent import Human
        enemies = board.find_in_range_opponents_or_allies(
            attacker, self.att_range, opponents=True
        )
        if not enemies:
            board.pyxel_manager.log.append("No one in range to push")
            return
        
        is_legal_push_check = partial(check_if_legal_push, board.find_location_of_target(attacker), board)
        
        for enemy in enemies:
            board.pyxel_manager.log.append(f"Pushing {enemy.name}")

            Human.move_other_character(
                enemy,
                board.find_location_of_target(attacker),
                self.squares,
                False,
                board,
                is_legal_push_check
            )

    def __str__(self): 
        return f"Push {self.squares} all enemies\nRange {self.att_range}"

@dataclass
class SummonSkeleton(ActionStep):

    def perform(self, board, attacker, round_num):
        board.add_new_skeleton(attacker.team_monster)

    def __str__(self):
        return "Summon a skeleton\nTo fight alongside you."


@dataclass
class MakeObstableArea(ActionStep):
    '''Unlike elements, obstacles go on the locations board
    and cannot be moved through and do not expire'''
    obstacle_type: Type[obstacle.TerrainObject]
    shape: set

    def perform(self, board, attacker, round_num):
        starting_coordinate = board.find_location_of_target(attacker)
        board.set_obstacles_in_area(
                starting_coordinate,
                self.shape,
                self.obstacle_type
            )
    
    def __str__(self):
        return f"Set {self.obstacle_type.__name__}\nShape:\n{shapes.print_shape(self.shape)}"

@dataclass
class MoveAlly(ActionStep):
    '''Unlike elements, obstacles go on the locations board
    and cannot be moved through and do not expire'''
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
            movement_check=None
        )
    
    def __str__(self):
        return f"Move {self.squares}, one ally\nRange {self.att_range}"


@dataclass
class ActionCard:
    attack_name: str
    actions: list[ActionStep]
    movement: int
    jump: bool

    # actions = [single_target_attack, area_of_attack, status_effect]
    def perform_attack(self, attacker, board, round_num: int):
        for action in self.actions:
            board.pyxel_manager.log.append(f"{attacker.name} is performing {action}!")
            action.perform(board, attacker, round_num)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)
    
    def __str__(self):
        print_str = f"{self.attack_name}\nMovement {self.movement}"
        if self.jump:
            print_str+= ", Jump"
        for action in self.actions:
            print_str+=f"\n{action}"
        return print_str

def select_in_range_target(board, attacker, att_range, opponent=True):
    in_range_chars = board.find_in_range_opponents_or_allies(
        attacker, att_range, opponents=opponent
    )
    target = attacker.select_attack_target(in_range_chars, board)
    return target

def check_if_legal_pull(puller_location, board, pull_target_old_location, new_pull_target_location):
    orig_dist = len(board.get_shortest_valid_path(pull_target_old_location, puller_location))
    new_dist = len(board.get_shortest_valid_path(new_pull_target_location, puller_location))

    if orig_dist > new_dist:
        return True
    else:
        return False

def check_if_legal_push(puller_location, board, pull_target_old_location, new_pull_target_location):
    orig_dist = len(board.get_shortest_valid_path(pull_target_old_location, puller_location))
    new_dist = len(board.get_shortest_valid_path(new_pull_target_location, puller_location))

    if orig_dist < new_dist:
        return True
    else:
        return False
