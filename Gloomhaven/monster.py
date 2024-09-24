import random
from IPython.display import display, clear_output
import sys
import time
import numpy as np

# monsters are our actors
# they have core attributes (health, name, etc.) and a set of attacks they can do
# they will belong to a board, and they will send attacks out to the board to be carried out
class Monster:
    # basic monster setup
    def __init__(self, name, health, is_character, starting_location):
        self.name = name
        self.health = health
        # randomly generate a stack of possible attacks
        self.create_attack_cards()
        # is this the player character or the monster?
        self.is_character = is_character
        self.location = starting_location

    # think of this as a deck of attack cards that we will randomly pull from
    # here we generate that deck of attack cards
    def create_attack_cards(self):
        # each attack card will be generated with a strength, distance, and number of targets, so set
        # some values to pull from
        strenghts = [1, 2, 3, 4, 5]
        strength_weights = [3, 5, 4, 2, 1]
        movements = [0, 1, 2, 3, 4]
        movement_weights = [1, 3, 4, 3, 1]
        max_distance = 3
        num_attacks = 5
        attacks = []

        # some things for attack names
        adjectives = ['Shadowed', 'Infernal', 'Venomous', 'Blazing', 'Cursed']
        elements = ['Fang', 'Storm', 'Flame', 'Void', 'Thorn']
        actions = ['Strike', 'Surge', 'Rend', 'Burst', 'Reaver']

        for item in [adjectives, elements, actions]:
            random.shuffle(item)

        # generate each attack card
        for i in range(num_attacks):
            strength = random.choices(strenghts, strength_weights)[0]
            movement = random.choices(movements, movement_weights)[0]
            distance = random.randint(1, max_distance)
            attack = {
                "attack_name": f"{adjectives.pop()} {elements.pop()} {actions.pop()}",
                "strength": strength,
                "distance": distance,
                "movement": movement
            }
            attacks.append(attack)
        self.attacks = attacks

    # grabs an attack card and send it to the board to be played
    def select_and_submit_attack(self, board):
        # if it's the monster grab a random attack card
        if self.is_character is False:
            attack_to_perform = random.choice(self.attacks)
            board.perform_monster_card(attack_to_perform)
        # if it's the character, let them pick their own actions
        else:
            attack_to_perform = self.get_character_attack_selection()
            board.perform_character_card(attack_to_perform)

    # asks character what card they want to play
    def get_character_attack_selection(self):
        # if you run out of actions without killing the monster, you get exhausted
        if len(self.attacks) == 0:
            print("Oh no! You have no more attacks left!")
            self.lose_game()
        # if they have attacks, show them what they have
        print("Your attacks are: ")
        for i, attack in enumerate(self.attacks):
            print(
                f"{i}: {attack['attack_name']}: Strength {attack['strength']}, Distance: {attack['distance']}, Movement: {attack['movement']}")
        verifying = True
        # let them pick a valid attack
        while (verifying):
            attack_num = int(input("Which attack card would you like to pick? Type the number exactly."))
            if 0 <= attack_num < len(self.attacks):
                verifying = False
                clear_output()
                attack_to_perform = self.attacks.pop(attack_num)
            else:
                print("Oops, typo! Try typing the number again.")
        return attack_to_perform