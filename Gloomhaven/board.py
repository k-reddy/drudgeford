import random
from IPython.display import display, clear_output
import sys
import time
import numpy as np

# the board holds all the game metadata including the monster and character who are playing
# it adjudicates actions and ends the game, too
# the board draws itself as well!
class Board:
    # set the game up by getting info from the player, giving instructions if needed, and start the turns
    # continue turns until the game is over!
    def __init__(self, size):
        self.size = size
        self.monster = Monster("Tree Man", 10, False, [2, 3])
        player_name = input("What's your character's name? ")
        clear_output()
        self.character = Monster(player_name, 10, True, [0, 0])
        self.game_over = False
        print(
            "Welcome to your quest, " + player_name + ". \nAs you enter the dungeon, you see a terrifying monster ahead! \nKill it or be killed...\n")
        want_help = input("Type anything to start or type help for instructions")
        if want_help == 'help':
            self.give_help()
        clear_output()
        self.draw()
        while self.game_over == False:
            self.take_turn()

    # dispaly the game instructions
    def give_help(self):
        clear_output()
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
        input("Type anything to continue")

    # draw the game board and display stats
    def draw(self):
        print(f"Monster Health: {self.monster.health}, Character Health: {self.character.health}")
        to_draw = ''
        monster_square = False
        character_square = False
        for i in range(self.size):
            top = ' ---' * self.size + "\n"
            sides = ''
            for j in range(self.size + 1):
                if self.character.location == [i, j]:
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
        return attack_distance >= sum(abs(a - b) for a, b in zip(self.monster.location, self.character.location))

    # !!! Help here - is there a more graceful way to handle the repeated code / ordering in the if / elif statement?
    def perform_character_card(self, attack):
        print("Character performs " + attack["attack_name"] + ": Attack " + str(attack["strength"]) + ", Range " + str(
            attack["distance"]) + ", Movement " + str(attack["movement"]) + "\n")
        good_action = False
        self.draw()
        while not good_action:
            action = input("Type 1 to move first or 2 to attack first.")
            if action == "1":
                clear_output()
                good_action = True
                self.perform_character_movement(attack)
                clear_output()
                self.attack_opponent(attack, True)
            elif action == "2":
                clear_output()
                good_action = True
                self.attack_opponent(attack, True)
                clear_output()
                self.perform_character_movement(attack)
        self.end_turn()

    # FOR TOMORROW: think about whether there's a better way to handle the direction mapping
    def perform_character_movement(self, attack):
        print("Now it's time to move!")
        self.draw()
        remaining_movement = attack["movement"]
        while remaining_movement > 0:
            print(f"movement remaining: {remaining_movement}")
            direction = input(
                "Type w for up, a for left, d for right, s for down, or f to finish. If you move off the map, you'll disappear!")
            direction_map = {
                "w": [-1, 0],
                "s": [1, 0],
                "a": [0, -1],
                "d": [0, 1]
            }
            if direction == "f":
                break
            elif direction in direction_map:
                self.character.location = list(np.add(self.character.location, direction_map[direction]))
                clear_output()
                self.draw()
            else:
                print("Incorrect input. Try again!")
                continue
            remaining_movement -= 1
        print("movement done!")

    def perform_monster_card(self, attack):
        print("Monsetr performs " + attack["attack_name"] + ": Attack " + str(attack["strength"]) + ", Range " + str(
            attack["distance"]) + ", Movement " + str(attack["movement"]) + "\n")
        if not self.check_attack_in_range(attack["distance"]):
            self.perform_monster_movement(False, attack["movement"])

        # after movement, try to attack
        self.attack_opponent(attack, False)
        self.end_turn()

    def end_turn(self):
        self.draw()
        time.sleep(3)

    def attack_opponent(self, attack, is_character):
        # if you're close enough, attack
        if self.check_attack_in_range(attack["distance"]):
            print("Attack hits!\n")
            # if it's the character and the attack kills, end the game. Otherwise, increment monster health
            if is_character:
                if self.monster.health <= attack["strength"]:
                    self.win_game()
                else:
                    self.monster.health -= attack["strength"]
            # similar for monster
            else:
                if self.character.health <= attack["strength"]:
                    self.lose_game()
                else:
                    self.character.health -= attack["strength"]

        # if you're not close enough and already did your movement, that's it for your turn
        else:
            print("Not close enough to attack")

    def perform_monster_movement(self, is_character, distance):
        # WORK ON THIS TOMORROW
        # can probably simplify the distance calculations
        # I think there's also an issue here if one distance is negative and the other is positive
        y_dist = self.monster.location[0] - self.character.location[0]
        x_dist = self.monster.location[1] - self.character.location[1]

        # first move vertically if you can
        if distance > 0 and y_dist > 1:
            dist_to_travel = distance if (x_dist + y_dist) > distance else y_dist - 1
            if is_character:
                self.character.location[0] += dist_to_travel
            else:
                self.monster.location[0] -= dist_to_travel

            distance -= y_dist

        # if there's distance left, move horizontally
        if distance > 0 and x_dist > 1:
            dist_to_travel = distance if x_dist > distance else x_dist - 1
            if is_character:
                self.character.location[1] += dist_to_travel
            else:
                self.monster.location[1] -= dist_to_travel

    def take_turn(self):
        # randomize who starts the turn
        if random.choice([1, 2]) == 1:
            # monster goes first
            clear_output()
            print("Ah! The Monster got a jump on you this round. Watch out...")
            self.monster.select_and_submit_attack(self)
            print("Now it's your turn! Make this one count.")
            self.character.select_and_submit_attack(self)
            input("Type anything to start the next round")
        else:
            # character goes first
            clear_output()
            print("You acted quick - it's your turn first this time.")
            self.draw()
            self.character.select_and_submit_attack(self)
            print("Now it's the Monster's turn...Watch out!")
            self.monster.select_and_submit_attack(self)
            input("Type anything to start the next round")

    def lose_game(self):
        print('''You died...GAME OVER
  .-.
 (o o)  
  |-|  
 /   \\
|     |
 \\___/''')
        self.game_over = True
        self.character.location = (self.size + 1, self.size + 1)
        sys.exit(0)

    def win_game(self):
        clear_output()
        print("You defeated the monster!!")
        self.game_over = True
        print('''
    \o/   Victory!
     |
    / \
   /   \
        ''')
        self.monster.location = (self.size + 1, self.size + 1)
        sys.exit(0)