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
        want_help = input("Hit enter to start or type help for instructions")
        helpers.clear_terminal()
        if want_help == 'help':
            give_help()
        print("Time to start the game!\n")
        while not self.game_over:
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
    def perform_player_card(self, attack):
        print(f"{self.player.name} performs " + attack["attack_name"] + ": Attack " + str(
            attack["strength"]) + ", Range " + str(attack["distance"]) + ", Movement " + str(attack["movement"]) + "\n")
        good_action = False
        self.draw()
        while not good_action:
            action = input("Type 1 to move first or 2 to attack first. ")
            if action == "1":
                good_action = True
                self.perform_player_movement(attack)
                time.sleep(3)
                self.attack_opponent(attack, True)
            elif action == "2":
                good_action = True
                self.attack_opponent(attack, True)
                time.sleep(3)
                self.perform_player_movement(attack)
        time.sleep(3)

    def perform_player_movement(self, attack):
        remaining_movement = attack["movement"]
        if remaining_movement == 0:
            print("No movement!")
            return
        print("\nNow it's time to move!")
        while remaining_movement > 0:
            print(
                f"You are performing {attack['attack_name']} with Attack " + str(attack["strength"]) + ", Range " + str(
                    attack["distance"]))
            print(f"\nmovement remaining: {remaining_movement}")
            direction = input(
                "Type w for up, a for left, d for right, s for down, or f to finish. "
                "If you move off the map, you'll disappear!")
            direction_map = {
                "w": [-1, 0],
                "s": [1, 0],
                "a": [0, -1],
                "d": [0, 1]
            }
            if direction == "f":
                break
            elif direction in direction_map:
                self.player.location = list(np.add(self.player.location, direction_map[direction]))
                helpers.clear_terminal()
                self.draw()
            else:
                print("Incorrect input. Try again!")
                continue
            remaining_movement -= 1
        print("movement done!")

    def perform_monster_card(self, attack):
        print("Monster performs " + attack["attack_name"] + ": Attack " + str(attack["strength"]) + ", Range " + str(
            attack["distance"]) + ", Movement " + str(attack["movement"]) + "\n")
        if not self.check_attack_in_range(attack["distance"]):
            self.perform_monster_movement(False, attack["movement"])

        # after movement, try to attack
        self.attack_opponent(attack, False)
        time.sleep(3)

    def attack_opponent(self, attack, is_player):
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

    def perform_monster_movement(self, is_player, distance):
        # WORK ON THIS TOMORROW
        # can probably simplify the distance calculations
        # I think there's also an issue here if one distance is negative and the other is positive
        y_dist = self.monster.location[0] - self.player.location[0]
        x_dist = self.monster.location[1] - self.player.location[1]

        if distance > 0:
            print("Monster moved!\n")
            # first move vertically if you can
            if y_dist > 1:
                dist_to_travel = distance if (x_dist + y_dist) > distance else y_dist - 1
                if is_player:
                    self.player.location[0] += dist_to_travel
                else:
                    self.monster.location[0] -= dist_to_travel

                distance -= y_dist

            # if there's distance left, move horizontally
            if x_dist > 1:
                dist_to_travel = distance if x_dist > distance else x_dist - 1
                if is_player:
                    self.player.location[1] += dist_to_travel
                else:
                    self.monster.location[1] -= dist_to_travel
            self.draw()

    def take_turn(self):
        # randomize who starts the turn
        print("Start of Round!\n")
        if random.choice([1, 2]) == 1:
            # monster goes first
            print("Ah! The Monster got a jump on you this round. Watch out...")
            self.monster.select_and_submit_attack(self)
            continue_turn()
            print("Now it's your turn! Make this one count.\n")
            self.player.select_and_submit_attack(self)
            input("Hit enter to start the next round")
        else:
            # player goes first
            print("You acted quick - it's your turn first this time.")
            self.player.select_and_submit_attack(self)
            continue_turn()
            print("Now it's the Monster's turn...Watch out!")
            self.monster.select_and_submit_attack(self)
            input("Hit enter to start the next round")

        helpers.clear_terminal()

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
        sys.exit(0)

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
        sys.exit(0)


def continue_turn():
    input('Hit enter to continue')
    helpers.clear_terminal()


# display the game instructions
def give_help():
    print('''
Welcome to the game! Here's how it works:
- You and the monster will attack each other once per turn in a random order
- You can only attack if you are within range of your enemy
- You pick your attacks, and the monster's are randomly generated
- Each attack has a movement associated with it. If you're not in range, you'll move that amount toward your enemy
- If you end in range, you will attack. If not, you won't attack this turn.
- Whoever runs out of health first loses

Good luck!
        ''')
    input("Hit enter to continue")
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
