from dataclasses import dataclass
import attack_shapes as shapes
import abc 
import utils
import random
from functools import partial
import obstacle


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
        target = select_in_range_target(board, attacker, self.att_range)
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
        target = select_in_range_target(board, attacker, self.att_range)

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
        target = select_in_range_target(board, attacker, self.att_range)

        if target is not None:
            board.teleport_character(target)

    def __str__(self):
        return f"Teleport Another Character in range {self.att_range}"

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
        return f"Cause one enemy in range {self.att_range} to draw {self.strength} as next attack modifier"
    
@dataclass
class ShieldSelf(ActionStep):
    strength: int
    duration: int

    def perform(self, board, attacker, round_num):
        attacker.shield = (self.strength, round_num+self.duration)
    
    def __str__(self):
        return f"Shield {self.strength} self for {self.duration} turns"

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
        return f"Shield {self.strength} for all allies in range {self.att_range} for {self.duration} turns"
   
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
class BlessSelf(ActionStep):
    def perform(self, board, attacker, round_num):
        rand_index = random.randint(0, len(attacker.attack_modifier_deck))
        modifier = utils.make_multiply_modifier(2, "2x Bless")
        attacker.modifier_deck.insert(rand_index, modifier)
    
    def __str__(self):
        return "Bless self with one 2x modifier card"

@dataclass  
class Pull(ActionStep):
    squares: int
    att_range: int

    def perform(self, board, attacker, round_num):
        target = select_in_range_target(board, attacker, self.att_range)

        if not target:
            board.disp.add_to_log("No one in range to pull")
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
        return f"Pull {self.squares} any enemy in range {self.att_range}"

@dataclass  
class Push(ActionStep):
    squares: int
    att_range: int

    def perform(self, board, attacker, round_num):
        from agent import Human, Ai

        target = select_in_range_target(board, attacker, self.att_range)

        if not target:
            board.disp.add_to_log("No one in range to pull")
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
        return f"Push {self.squares} any enemy in range {self.att_range}"

@dataclass
class MakeObstableArea(ActionStep):
    '''Unlike elements, obstacles go on the locations board
    and cannot be moved through and do not expire'''
    obstacle_type: obstacle.TerrainObject
    shape: set

    def perform(self, board, attacker, round_num):
        starting_coordinate = board.find_location_of_target(attacker)
        board.set_obstacles_in_area(
                starting_coordinate,
                self.shape,
                self.obstacle_type
            )
    
    def __str__(self):
        return f"Set {self.obstacle_type.__name__} with shape:\n{shapes.print_shape(self.shape)}"

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
        return f"Move one ally in range {self.att_range} up to {self.squares} squares"


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

def select_in_range_target(board, attacker, att_range, opponent=True):
    in_range_chars = board.find_in_range_opponents_or_allies(
        attacker, att_range, opponents=opponent
    )
    target = attacker.select_attack_target(in_range_chars)
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
