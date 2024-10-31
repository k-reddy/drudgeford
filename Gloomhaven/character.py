import random
import abc
import character_classes
from gh_types import ActionCard
from functools import partial

# characters are our actors
# they have core attributes (health, name, etc.) and a set of attacks they can do
# they will belong to a board, and they will send attacks out to the board to be carried out
class Character(abc.ABC):
    # basic monster setup
    def __init__(self, name, health, disp, emoji, agent, is_monster):
        self.health = self.set_health()
        self.name = name
        self.action_cards = self.create_action_cards()
        self.killed_action_cards = []
        self.available_action_cards = self.action_cards.copy()
        self.disp = disp
        self.emoji = emoji
        self.agent = agent
        self.backstory = self.set_backstory()
        self.attack_modifier_deck = self.make_attack_modifier_deck()
        self.team_monster = is_monster

    @abc.abstractmethod
    def set_health(self):
        pass

    @abc.abstractmethod
    def create_action_cards(self):
        pass

    @abc.abstractmethod
    def set_backstory(self):
        pass

    def select_action_card(self):
        action_card_to_perform = self.agent.select_action_card(
                self.disp, self.available_action_cards
            )
        return action_card_to_perform

    def decide_if_move_first(self, action_card):
        self.disp.add_to_log(f"{self.name} is performing {action_card}\n")
        return self.agent.decide_if_move_first(self.disp)

    def perform_movement(self, action_card, board):
        if action_card["movement"] == 0:
            self.disp.add_to_log("No movement!")
            return
        self.disp.add_to_log(f"{self.name} is moving")
        self.agent.perform_movement(self, action_card, board)
        # add some space between the movement and attack
        self.disp.add_to_log("")

    def select_attack_target(self, in_range_opponents):
        if not in_range_opponents:
            self.disp.add_to_log("No opponents in range\n")
            return None
        return self.agent.select_attack_target(self.disp, in_range_opponents)

    def short_rest(self) -> None:
        # reset our available cards
        self.available_action_cards = [card for card in self.action_cards if card not in self.killed_action_cards]
        # kill a random card, update the user, remove it from play, and keep track for next round
        killed_card = random.choice(self.available_action_cards)
        self.disp.add_to_log(f"You lost {killed_card}")
        self.available_action_cards.remove(killed_card)
        self.killed_action_cards.append(killed_card)

    def make_attack_modifier_deck(self) -> list:
        attack_modifier_deck = [
            make_multiply_modifier(2, "2x"),
            make_multiply_modifier(0, "Null"),
        ]
        for modifier in [-2, -1, 0, 1, 2]:
            attack_modifier_deck.append(make_additive_modifier(modifier))

        attack_modifier_weights = [1, 1, 1, 3, 3, 3, 1]
        for i, weight in enumerate(attack_modifier_weights):
            for _ in range(weight+1):
                attack_modifier_deck.append(attack_modifier_deck[i])
        random.shuffle(attack_modifier_deck)
        return attack_modifier_deck

    def set_health(self):
        return 8
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
            action_card = ActionCard(
                attack_name=f"{adjectives[i]} {elements[i]} {actions[i]}",
                attack_shape=None,
                strength=strength,
                distance=distance,
                movement=movement,
                status_effect=None,
                status_shape=None,
                jump=True
            )
            action_cards.append(action_card)
        return action_cards
    def set_backstory(self):
        return ""

class Wizard(Character):
    def set_health(self):
        return character_classes.wizard.health
    def create_action_cards(self):
        return character_classes.wizard.cards
    def set_backstory(self):
        return character_classes.wizard.backstory

def make_multiply_modifier(multiplier: int, multiplier_text: str) -> tuple:
    def multiply(x, y):
        return x * y
    return (partial(multiply, multiplier), multiplier_text)

def make_additive_modifier(modifier_num) -> tuple:
    def add(x, y):
        return x + y
    return (partial(add, modifier_num), f"{modifier_num:+d}")