import random
import sys
import time
from functools import partial
import numpy as np
import helpers


# the board holds all the game metadata including the monster and player who are playing
# it adjudicates actions and ends the game
# the board draws itself as well!
class Board:
    # set the game up by getting info from the player, giving instructions if needed, and start the turns
    # continue turns until the game is over!
    def __init__(self, size: int, monster: object, player: object) -> object:
        self.size = size
        self.monster = monster
        self.player = player
        self.game_over = False
        print(
            "Welcome to your quest, " + player.name + ". \n",
            "As you enter the dungeon, you see a terrifying monster ahead! \n",
            "Kill it or be killed...\n")
        input("Time to start the game! Hit enter to continue\n")
        while not self.game_over:
            # !!! need some way of checking in here if it's time to end the game, b/c that can happen within a round
            # also should change turn vs round
            self.take_turn()

    # draw the game board and display stats
    def draw(self):
        print(f"Monster Health: {self.monster.health}, {self.player.name}'s Health: {self.player.health}")
        to_draw = ''
        top = ''
        for i in range(self.size):
            top = ' ---' * self.size + "\n"
            sides = ''
            for j in range(self.size + 1):
                if self.player.location == [i, j]:
                    sides += '| C '
                elif self.monster.location == [i, j]:
                    sides += '| M '
                else:
                    sides += '|   '
            to_draw += top
            to_draw += sides + '\n'
        # add the bottom
        to_draw += top
        print(to_draw)

    # is the attack in range?
    def check_attack_in_range(self, attack_distance):
        return attack_distance >= sum(abs(a - b) for a, b in zip(self.monster.location, self.player.location))

    # !!! Help here - is there a more graceful way to handle the repeated code / ordering in the if / elif statement?



    # !!! I should probably ask the character who they want to attack out of whoever is possible
    # then board should adjudicate the attack and update people's healths


    def find_possible_attack_targets(self):
        pass
    def attack_opponent(self, attack, is_player):
        # targets = find_possible_attack_targets()
        # character.pick_target(targets)
        modified_attack_strength = select_and_apply_attack_modifier(attack["strength"])
        print(f"Attempting attack with strength {attack['strength']} and range {attack['distance']}\n")

        # if you're close enough, attack
        if self.check_attack_in_range(attack["distance"]):
            if modified_attack_strength <= 0:
                print("Darn, attack missed!")
            else:
                print("Attack hits!\n")
                print(f"After the modifier, attack strength is: {modified_attack_strength}")

                # if it's the player and the attack kills, end the game. Otherwise, increment monster health
                if is_player:
                    if self.monster.health <= modified_attack_strength:
                        self.win_game()
                    else:
                        self.monster.health -= modified_attack_strength
                # similar for monster
                else:
                    if self.player.health <= modified_attack_strength:
                        self.lose_game()
                    else:
                        self.player.health -= modified_attack_strength

        # if you're not close enough and already did your movement, that's it for your turn
        else:
            print("Not close enough to attack")


    # here the board should keep track of whose turn it is and the locations
    # it should ask players what they want to do
    # it should adjudicate if that's possible
    def run_round(self):
        # randomize who starts the turn
        print("Start of Round!\n")
        characters = [self.player, self.monster]
        for i, _ in enumerate(characters):
            # randomly pick who starts the round
            acting_character = random.choice(characters)
            characters.remove(acting_character)
            print(f"It's {acting_character.name}'s turn!")
            self.run_turn(acting_character)
            end_turn()
        input("End of round. Hit Enter to continue")
        helpers.clear_terminal()

    def run_turn(self, acting_character):
        action_card = acting_character.select_action_card()
        actions_to_perform = acting_character.set_action_order(action_card)
        # I think best to move the action map here, and ask for a bool, move_first = true
        # because the functions should have different parameters
        for action in actions_to_perform:
            action(action_card, self)


    def lose_game(self):
        helpers.clear_terminal()
        print('''You died...GAME OVER
  .-.
 (o o)  
  |-|  
 /   \\
|     |
 \\___/''')
        self.game_over = True
        self.player.location = (self.size + 1, self.size + 1)

    def win_game(self):
        helpers.clear_terminal()
        print("You defeated the monster!!")
        self.game_over = True
        print('\n'
              r'    \o/   Victory!\n'
              '     |\n'
              '    / \\n'
              '   /   \\n'
              '        ')
        self.monster.location = (self.size + 1, self.size + 1)

def end_turn():
    input('End of turn. Hit enter to continue')
    helpers.clear_terminal()


def select_and_apply_attack_modifier(initial_attack_strength):
    def multiply(x, y):
        return x * y

    def add(x, y):
        return x + y

    attack_modifier_deck = [partial(multiply, 2), partial(multiply, 0)]
    for modifier in [-2, -1, 0, 1, 2]:
        attack_modifier_deck.append(partial(add, modifier))

    attack_modifier_weights = [1, 1, 2, 10, 10, 10, 2]

    attack_modifier_function = random.choices(attack_modifier_deck, attack_modifier_weights)[0]
    return attack_modifier_function(initial_attack_strength)
