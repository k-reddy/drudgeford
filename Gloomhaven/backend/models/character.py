import random
import abc
import backend.models.character_classes as character_classes
import backend.models.action_model as action_model
from ..utils import utilities
from backend.models import obstacle
from backend.utils import attack_shapes as shapes

MAX_ROUNDS = 1000


# characters are our actors
# they have core attributes (health, name, etc.) and a set of attacks they can do
# they will belong to a board, and they will send attacks out to the board to be carried out
class Character(abc.ABC):
    # basic monster setup
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        self.id = char_id
        self.health = self.set_health()
        # we do not edit this value, so we can reset health and only heal to a max health
        self.max_health = self.health
        self.name = name
        self.action_cards = self.create_action_cards()
        self.killed_action_cards: list = []
        self.available_action_cards = self.action_cards.copy()
        self.pyxel_manager = pyxel_manager
        self.emoji = emoji
        # a default sprite
        self.pyxel_sprite_name = "knight"
        self.agent = agent
        self.backstory = "I'm a generic character, how boring"
        self.attack_modifier_deck = self.make_attack_modifier_deck()
        self.team_monster = is_monster
        self.shield: tuple[int, int] = (0, MAX_ROUNDS)
        self.log = log
        self.elemental_affinity = None
        self.client_id = player_id
        self.lose_turn = False

    def select_action_card(self):
        action_card_to_perform = self.agent.select_action_card(
            self.pyxel_manager, self.available_action_cards, self.client_id
        )
        return action_card_to_perform

    def select_board_square_target(self, board, att_range, shape):
        return self.agent.select_board_square_target(
            board, self.client_id, att_range, self, shape
        )

    def decide_if_move_first(self, action_card):
        return self.agent.decide_if_move_first(self.pyxel_manager, self.client_id)

    def perform_movement(self, movement, is_jump, board):
        if movement == 0:
            self.log.append("No movement!")
            return
        self.log.append(f"{self.name} is moving")
        self.agent.perform_movement(self, movement, is_jump, board, self.client_id)
        # add some space between the movement and attack
        self.log.append("")

    def select_attack_target(self, in_range_opponents, board):
        if not in_range_opponents:
            return None
        return self.agent.select_attack_target(
            self.pyxel_manager, in_range_opponents, board, self, self.client_id
        )

    def short_rest(self) -> None:
        # kill a random used card that's not already been killed
        killed_card = random.choice(
            set(self.action_cards)
            - set(self.available_action_cards)
            - set(self.killed_action_cards)
        )
        # reset our available cards
        self.available_action_cards = [
            card for card in self.action_cards if card not in self.killed_action_cards
        ]
        # update the user, remove it from play, and keep track for next round
        # only update people with a frontend
        if self.client_id:
            self.pyxel_manager.get_user_input(
                prompt=f"You short rested and lost {killed_card}\nHit enter to continue",
                client_id=self.client_id,
            )
        self.available_action_cards.remove(killed_card)
        self.killed_action_cards.append(killed_card)
        # load new available cards
        self.pyxel_manager.load_action_cards(
            self.available_action_cards, self.client_id
        )

    def make_attack_modifier_deck(self) -> list:
        attack_modifier_deck = [
            utilities.make_multiply_modifier(2, "2x"),
            utilities.make_multiply_modifier(0, "Null"),
        ]
        for modifier in [-2, -1, 0, 1, 2]:
            attack_modifier_deck.append(utilities.make_additive_modifier(modifier))

        attack_modifier_weights = [1, 1, 1, 3, 3, 3, 1]
        for i, weight in enumerate(attack_modifier_weights):
            for _ in range(weight + 1):
                attack_modifier_deck.append(attack_modifier_deck[i])
        random.shuffle(attack_modifier_deck)
        return attack_modifier_deck

    def pick_rotated_attack_coordinates(
        self, board, shape: set, starting_coord: tuple[int, int], from_self: bool = True
    ) -> list[tuple[int, int]]:
        """
        gets an attack shape rotation and attack coordinates (not offsets)
        from agent
        if from_self=false, we're using this for an area attack with target,
        so we only show cardinal directions
        """
        # we do not rotate cirlces or rings
        if shapes.is_circle_or_ring(shape):
            return [
                (starting_coord[0] + coordinate[0], starting_coord[1] + coordinate[1])
                for coordinate in shape
            ]
        else:
            shape.discard((0, 0))
        return self.agent.pick_rotated_attack_coordinates(
            board, shape, starting_coord, self.client_id, self.team_monster, from_self
        )

    def decide_if_short_rest(self):
        return self.agent.decide_if_short_rest(self.pyxel_manager, self.client_id)

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
            "Shadowed",
            "Infernal",
            "Venomous",
            "Blazing",
            "Cursed",
            "Frozen",
            "Eternal",
            "Bloodthirsty",
            "Savage",
            "Dreadful",
            "Ancient",
            "Malevolent",
            "Spectral",
            "Dire",
            "Enraged",
        ]

        elements = [
            "Fang",
            "Storm",
            "Flame",
            "Void",
            "Thorn",
            "Frost",
            "Stone",
            "Ember",
            "Blade",
            "Hollow",
            "Spirit",
            "Tide",
            "Wind",
            "Ash",
            "Grave",
        ]

        actions = [
            "Strike",
            "Surge",
            "Rend",
            "Burst",
            "Reaver",
            "Crush",
            "Slash",
            "Howl",
            "Smite",
            "Rampage",
            "Sunder",
            "Devour",
            "Shatter",
            "Lash",
            "Tremor",
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
                actions=[
                    action_model.SingleTargetAttack(
                        strength=strength, att_range=distance
                    )
                ],
                movement=movement,
                jump=random.choice([False, False, False, False, True]),
            )
            action_cards.append(action_card)
        return action_cards

    def set_health(self):
        return 8


class Wizard(Character):

    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.backstory = character_classes.wizard.backstory
        self.pyxel_sprite_name = "wizard"

    def create_action_cards(self):
        return character_classes.wizard.cards

    def set_health(self):
        return character_classes.wizard.health


class Miner(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.backstory = character_classes.miner.backstory
        self.pyxel_sprite_name = "miner"

    def create_action_cards(self):
        return character_classes.miner.cards

    def set_health(self):
        return character_classes.miner.health


class Necromancer(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.backstory = character_classes.necromancer.backstory
        self.pyxel_sprite_name = "necromancer"

    def create_action_cards(self):
        return character_classes.necromancer.cards

    def set_health(self):
        return character_classes.necromancer.health


class Monk(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.backstory = character_classes.monk.backstory
        self.pyxel_sprite_name = "monk"

    def create_action_cards(self):
        return character_classes.monk.cards

    def set_health(self):
        return character_classes.monk.health


class Treeman(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "treeman"

    def create_action_cards(self):
        return character_classes.tank_melee.cards

    def set_health(self):
        return character_classes.tank_melee.health


class Fairy(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "fairy"

    def create_action_cards(self):
        return character_classes.fairy.cards

    def set_health(self):
        return character_classes.fairy.health


class MushroomMan(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "mushroomman"
        self.elemental_affinity = obstacle.Spores

    def create_action_cards(self):
        return character_classes.support_fungal.cards

    def set_health(self):
        return character_classes.support_fungal.health


# class EvilBlob(Character):
#     def __init__(self, name, pyxel_manager, emoji, agent, char_id: int, is_monster, log):
#         super().__init__(name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id)
#         self.pyxel_sprite_name = "evilblob"


class Fiend(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "fiend"

    def create_action_cards(self):
        return character_classes.fiend.cards

    def set_health(self):
        return character_classes.fiend.health


class Demon(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "demon"

    def create_action_cards(self):
        return character_classes.demon.cards

    def set_health(self):
        return character_classes.demon.health


class FireSprite(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "firesprite"
        self.elemental_affinity = obstacle.Fire

    def create_action_cards(self):
        return character_classes.firesprite.cards

    def set_health(self):
        return character_classes.firesprite.health


class IceMonster(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "icemonster"

    def create_action_cards(self):
        return character_classes.ice_monster.cards

    def set_health(self):
        return character_classes.ice_monster.health


class SnowStalker(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "snowstalker"

    def create_action_cards(self):
        return character_classes.snow_stalker.cards

    def set_health(self):
        return character_classes.snow_stalker.health


class IceDragon(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "icedragon"

    def create_action_cards(self):
        return character_classes.ice_dragon.cards

    def set_health(self):
        return character_classes.ice_dragon.health


class Skeleton(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "skeleton"

    def create_action_cards(self):
        return character_classes.skeleton.cards

    def set_health(self):
        return character_classes.skeleton.health


class Corpse(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "corpse"

    def create_action_cards(self):
        return character_classes.corpse.cards

    def set_health(self):
        return character_classes.corpse.health


class Ghost(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "ghost"

    def create_action_cards(self):
        return character_classes.ghost.cards

    def set_health(self):
        return character_classes.ghost.health


class WailingSpirit(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "wailingspirit"

    def create_action_cards(self):
        return character_classes.wailing_spirit.cards

    def set_health(self):
        return character_classes.wailing_spirit.health


class FleshGolem(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "fleshgolem"

    def create_action_cards(self):
        return character_classes.fleshgolem.cards

    def set_health(self):
        return character_classes.fleshgolem.health


class BloodOoze(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "bloodooze"

    def create_action_cards(self):
        return character_classes.bloodooze.cards

    def set_health(self):
        return character_classes.bloodooze.health


class MalformedFlesh(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "evilblob"

    def create_action_cards(self):
        return character_classes.malformed.cards

    def set_health(self):
        return character_classes.malformed.health


class Orchestrator(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "orchestrator"

    def create_action_cards(self):
        return character_classes.orchestrator.cards

    def set_health(self):
        return character_classes.orchestrator.health


class Puppet(Character):
    def __init__(
        self,
        name,
        pyxel_manager,
        emoji,
        agent,
        char_id: int,
        is_monster,
        log,
        player_id=None,
    ):
        super().__init__(
            name, pyxel_manager, emoji, agent, char_id, is_monster, log, player_id
        )
        self.pyxel_sprite_name = "orchestratorgolem"

    def create_action_cards(self):
        return character_classes.puppet.cards

    def set_health(self):
        return character_classes.puppet.health
