import random
import abc
import backend.models.character_classes as character_classes
import backend.models.action_model as action_model 
from ..utils import utilities
from backend.models import obstacle
import textwrap
from backend.utils.config import TEXT_WIDTH

MAX_ROUNDS = 1000

# characters are our actors
# they have core attributes (health, name, etc.) and a set of attacks they can do
# they will belong to a board, and they will send attacks out to the board to be carried out
class Character(abc.ABC):
    # basic monster setup
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        self.id = char_id
        self.health = 8
        self.name = name
        self.action_cards = self.create_action_cards()
        self.killed_action_cards: list = []
        self.available_action_cards = self.action_cards.copy()
        self.disp = disp
        self.emoji = emoji
        # a default sprite 
        self.pyxel_sprite_name = "knight"
        self.agent = agent
        self.backstory = "I'm a generic character, how boring"
        self.attack_modifier_deck = self.make_attack_modifier_deck()
        self.team_monster = is_monster
        self.shield: tuple[int,int] = (0, MAX_ROUNDS)
        self.log = log
        self.elemental_affinity = None

    def select_action_card(self):
        action_card_to_perform = self.agent.select_action_card(
                self.disp, self.available_action_cards
            )
        return action_card_to_perform

    def decide_if_move_first(self, action_card):
        return self.agent.decide_if_move_first(self.disp)

    def perform_movement(self, movement, is_jump, board):
        if movement == 0:
            self.log.append("No movement!")
            return
        self.log.append(f"\n{self.name} is moving\n")
        self.agent.perform_movement(self, movement, is_jump, board)
        # add some space between the movement and attack
        self.log.append("")

    def select_attack_target(self, in_range_opponents, board):
        if not in_range_opponents:
            return None
        return self.agent.select_attack_target(self.disp, in_range_opponents, board, self)

    def short_rest(self) -> None:
        # reset our available cards
        self.available_action_cards = [card for card in self.action_cards if card not in self.killed_action_cards]
        # kill a random card, update the user, remove it from play, and keep track for next round
        killed_card = random.choice(self.available_action_cards)
        self.log.append(f"You lost {killed_card}")
        self.available_action_cards.remove(killed_card)
        self.killed_action_cards.append(killed_card)

    def make_attack_modifier_deck(self) -> list:
        attack_modifier_deck = [
            utilities.make_multiply_modifier(2, "2x"),
            utilities.make_multiply_modifier(0, "Null"),
        ]
        for modifier in [-2, -1, 0, 1, 2]:
            attack_modifier_deck.append(utilities.make_additive_modifier(modifier))

        attack_modifier_weights = [1, 1, 1, 3, 3, 3, 1]
        for i, weight in enumerate(attack_modifier_weights):
            for _ in range(weight+1):
                attack_modifier_deck.append(attack_modifier_deck[i])
        random.shuffle(attack_modifier_deck)
        return attack_modifier_deck
    
    def create_action_cards(self):
        strengths = [1, 2, 3, 4, 5]
        strength_weights = [3, 5, 4, 2, 1]
        movements = [0, 1, 2, 3, 4]
        movement_weights = [1, 3, 4, 3, 1]
        max_distance = 3
        num_action_cards = 5
        action_cards = []

        # some things for attack names
        adjectives = [
            "Shadowed", "Infernal", "Venomous", "Blazing", "Cursed", 
            "Frozen", "Eternal", "Bloodthirsty", "Savage", "Dreadful",
            "Ancient", "Malevolent", "Spectral", "Dire", "Enraged"
        ]

        elements = [
            "Fang", "Storm", "Flame", "Void", "Thorn", 
            "Frost", "Stone", "Ember", "Blade", "Hollow",
            "Spirit", "Tide", "Wind", "Ash", "Grave"
        ]

        actions = [
            "Strike", "Surge", "Rend", "Burst", "Reaver", 
            "Crush", "Slash", "Howl", "Smite", "Rampage", 
            "Sunder", "Devour", "Shatter", "Lash", "Tremor"
        ]

        for item in [adjectives, elements, actions]:
            random.shuffle(item)

        # generate each attack card
        for i in range(num_action_cards):
            strength = random.choices(strengths, strength_weights)[0]
            movement = random.choices(movements, movement_weights)[0]
            distance = random.randint(1, max_distance)
            action_card = action_model.ActionCard(
                attack_name=f"{adjectives[i]} {elements[i]} {actions[i]}",
                actions=[action_model.SingleTargetAttack(
                    strength=strength,
                    att_range=distance
                )],
                movement=movement,
                jump=random.choice([False, False, False, False, True])
            )
            action_cards.append(action_card)
        return action_cards

class Wizard(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.health = character_classes.wizard.health
        self.backstory = textwrap.fill(character_classes.wizard.backstory, TEXT_WIDTH)
        self.pyxel_sprite_name = "wizard"
    
    def create_action_cards(self):
        return character_classes.wizard.cards
    
class Miner(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.health = character_classes.miner.health
        self.backstory = textwrap.fill(character_classes.miner.backstory, TEXT_WIDTH)
        self.pyxel_sprite_name = "miner"

    def create_action_cards(self):
        return character_classes.miner.cards

class Necromancer(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.health = character_classes.necromancer.health
        self.backstory = textwrap.fill(character_classes.necromancer.backstory, TEXT_WIDTH)
        self.pyxel_sprite_name = "necromancer"
    
    def create_action_cards(self):
        return character_classes.necromancer.cards
    
class Monk(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.health = character_classes.monk.health
        self.backstory = textwrap.fill(character_classes.monk.backstory, TEXT_WIDTH)
        self.pyxel_sprite_name = "monk"
    
    def create_action_cards(self):
        return character_classes.monk.cards

class Treeman(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.health = character_classes.tank_melee.health
        self.pyxel_sprite_name = "treeman"
    
    def create_action_cards(self):
        return character_classes.tank_melee.cards
    
class Fairy(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.health = character_classes.fairy.health
        self.pyxel_sprite_name = "fairy"
    
    def create_action_cards(self):
        return character_classes.fairy.cards
    
class MushroomMan(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.health = character_classes.support_fungal.health
        self.pyxel_sprite_name = "mushroomman"
        self.elemental_affinity = obstacle.Spores
    
    def create_action_cards(self):
        return character_classes.support_fungal.cards
    
# class EvilBlob(Character):
#     def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
#         super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
#         self.pyxel_sprite_name = "evilblob"

class Fiend(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "fiend"
        self.health = character_classes.fiend.health

        
    def create_action_cards(self):
        return character_classes.fiend.cards

class Demon(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "demon"
        self.health = character_classes.demon.health


    def create_action_cards(self):
        return character_classes.demon.cards

class FireSprite(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "firesprite"
        self.elemental_affinity = obstacle.Fire
        self.health = character_classes.firesprite.health


    def create_action_cards(self):
        return character_classes.firesprite.cards
    
class IceMonster(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "icemonster"
        self.health = character_classes.ice_monster.health


    def create_action_cards(self):
        return character_classes.ice_monster.cards
    
class SnowStalker(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "snowstalker"
        self.health = character_classes.snow_stalker.health


    def create_action_cards(self):
        return character_classes.snow_stalker.cards

class IceDragon(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "icedragon"
        self.health = character_classes.ice_dragon.health

    def create_action_cards(self):
        return character_classes.ice_dragon.cards
    

class Skeleton(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "skeleton"
        self.health = character_classes.skeleton.health

    def create_action_cards(self):
        return character_classes.skeleton.cards

class Corpse(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "corpse"
        self.health = character_classes.corpse.health

    def create_action_cards(self):
        return character_classes.corpse.cards

class Ghost(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "ghost"
        self.health = character_classes.ghost.health

    def create_action_cards(self):
        return character_classes.ghost.cards

class WailingSpirit(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "wailingspirit"
        self.health = character_classes.wailing_spirit.health

    def create_action_cards(self):
        return character_classes.wailing_spirit.cards

class FleshGolem(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "fleshgolem"
        self.health = character_classes.fleshgolem.health

    def create_action_cards(self):
        return character_classes.fleshgolem.cards
    
class BloodOoze(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "bloodooze"
        self.health = character_classes.bloodooze.health

    def create_action_cards(self):
        return character_classes.bloodooze.cards
    
class MalformedFlesh(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "evilblob"
        self.health = character_classes.malformed.health

    def create_action_cards(self):
        return character_classes.malformed.cards
    
class Orchestrator(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "orchestrator"
        self.health = character_classes.orchestrator.health

    def create_action_cards(self):
        return character_classes.malformed.cards
    
class Puppet(Character):
    def __init__(self, name, disp, emoji, agent, char_id: int, is_monster, log):
        super().__init__(name, disp, emoji, agent, char_id, is_monster, log)
        self.pyxel_sprite_name = "orchestratorgolem"
        self.health = character_classes.puppet.health

    def create_action_cards(self):
        return character_classes.puppet.cards

