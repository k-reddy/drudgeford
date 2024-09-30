import random
import sys
import time
from functools import partial
from dataclasses import dataclass
import helpers


"""
[
    i: [
        j: Object ref
    ]
]
[0][0] = Monster
[4][4] = Player

"""


def initialize_board(width=5, height=5):
    return [[None for _ in range(width)] for _ in range(height)]


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
        self.characters = [monster, player]
        self.all_character_data = self.generate_character_data([monster, player])
        # !!! may want to add this to all_character_data rather than keeping it separate
        # but may want to keep it separate b/c then this can also hold obstacles?
        self.locations = initialize_board(self.size, self.size)
        self.set_starting_locations()
        self.game_over = False
        print(
            "Welcome to your quest, " + player.name + ". \n",
            "As you enter the dungeon, you see a terrifying monster ahead! \n",
            "Kill it or be killed...\n",
        )
        input("Time to start the game! Hit enter to continue\n")
        while not self.game_over:
            self.run_round()
        # !!! Implement something here to end the game depending on the game state

    def generate_character_data(self, characters):
        all_character_data = []
        for i, char in enumerate(characters):
            char_data = characterData(
                id=str(i),
                action_cards=create_action_cards(),
                health=10,
                character=char,
            )
            all_character_data.append(char_data)
        return all_character_data

    def set_starting_locations(self):
        for character in self.characters:
            self.pick_unoccupied_location(character)

    def pick_unoccupied_location(self, character):
        while True:
            rand_location = [
                random.randint(0, self.size - 1),
                random.randint(0, self.size - 1),
            ]
            if not self.locations[rand_location[0]][rand_location[1]]:
                self.locations[rand_location[0]][rand_location[1]] = character

    # draw the game board and display stats
    def draw(self):
        # print(f"Monster Health: {self.monster.health}, {self.player.name}'s Health: {self.player.health}")
        to_draw = ""
        top = ""
        for i in range(self.size):
            top = " ---" * self.size + "\n"
            sides = ""
            for j in range(self.size + 1):
                if isinstance(self.locations[i][j], Player):
                    sides += "| P "
                elif isinstance(self.locations[i][j], Monster):
                    sides += "| M "
                else:
                    sides += "|   "
            to_draw += top
            to_draw += sides + "\n"
        # add the bottom
        to_draw += top
        print(to_draw)

    # is the attack in range?
    def check_attack_in_range(self, attack_distance, attack_target):
        dist_to_target = get_distance_between_locations(
            self.locations[self.id], self.locations[attack_target.id]
        )
        return attack_distance >= dist_to_target

    def find_opponents(self, actor):
        if actor == self.monster:
            return [self.player]
        else:
            return [self.monster]

    def attack_target(self, target_id, action_card):
        modified_attack_strength = select_and_apply_attack_modifier(
            action_card["strength"]
        )
        print(
            f"Attempting attack with strength {action_card['strength']} and range {action_card['distance']}\n"
        )

        # if you're close enough, attack
        if not self.check_attack_in_range(action_card["distance"]):
            print("Not close enough to attack")
            return

        if modified_attack_strength <= 0:
            print("Darn, attack missed!")
            return

        print("Attack hits!\n")
        print(f"After the modifier, attack strength is: {modified_attack_strength}")

        # if
        # !!! To implement
        # if it's the player and the attack kills, end the game. Otherwise, increment monster health
        # update the health of the character we attacked
        # if it goes below their remaining health, win or lose the game depending on who it is
        # ^ this is a place to work on the game state thing


"""
id ->
character
health
action_cards
"""


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

        # !!! ideally this would go in end_turn() but then I don't know how to quit the for loop
        if self.game_over:
            return
        end_turn()
    input("End of round. Hit Enter to continue")
    helpers.clear_terminal()


def run_turn(self, acting_character):
    action_card = acting_character.select_action_card()
    move_first = acting_character.decide_if_move_first(action_card)

    if move_first:
        acting_character.perform_movement(action_card, self)
        target_id = acting_character.select_attack_target_id()
        self.attack_target(target_id, action_card)
    else:
        target_id = acting_character.select_attack_target_id()
        self.attack_target(target_id, action_card)
        acting_character.perform_movement()

    end_turn()


def find_closest_opponent_location(self, acting_character):
    closest_opponent_id = self.find_closest_opponent_id(self, acting_character)
    return self.locations[closest_opponent_id]


def find_closest_opponent_id(self, acting_character):
    # right now there's only one opponent
    return self.find_opponents(acting_character)[0].id


def move_character_to_location(self, acting_character, target_location, movement):
    remaining_movement = movement
    while remaining_movement > 0:
        y_movement, x_movement = [
            b - a for a, b, in zip(self.locations[acting_character.id], target_location)
        ]
        if y_movement != 0:
            axis = 0
            direction = 1 if y_movement > 0 else -1
            # move one in the direction of y_movement
        elif x_movement > 1:
            axis = 1
            direction = 1 if x_movement > 0 else -1
        else:
            break

        remaining_movement -= 1
        self.locations[acting_character.id][axis] += direction


def lose_game(self):
    helpers.clear_terminal()
    print(
        """You died...GAME OVER
.-.
(o o)  
|-|  
/   \\
|     |
\\___/"""
    )
    self.game_over = True
    self.player.location = (self.size + 1, self.size + 1)


def win_game(self):
    helpers.clear_terminal()
    print("You defeated the monster!!")
    self.game_over = True
    print("\n" r"    \o/   Victory!\n" "     |\n" "    / \\n" "   /   \\n" "        ")
    self.monster.location = (self.size + 1, self.size + 1)


def end_turn():
    input("End of turn. Hit enter to continue")
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

    attack_modifier_function = random.choices(
        attack_modifier_deck, attack_modifier_weights
    )[0]
    return attack_modifier_function(initial_attack_strength)


def get_distance_between_locations(location1, location2):
    return sum(abs(a - b) for a, b in zip(location1, location2))


@dataclass
class characterData:
    id: str
    action_cards: list
    health: int
    character: object

    # think of this as a deck of attack cards that we will randomly pull from
    # here we generate that deck of attack cards


def create_action_cards():
    # each attack card will be generated with a strength, distance, and number of targets, so set
    # some values to pull from
    strengths = [1, 2, 3, 4, 5]
    strength_weights = [3, 5, 4, 2, 1]
    movements = [0, 1, 2, 3, 4]
    movement_weights = [1, 3, 4, 3, 1]
    max_distance = 3
    num_action_cards = 5
    action_cards = []

    # some things for attack names
    adjectives = ["Shadowed", "Infernal", "Venomous", "Blazing", "Cursed"]
    elements = ["Fang", "Storm", "Flame", "Void", "Thorn"]
    actions = ["Strike", "Surge", "Rend", "Burst", "Reaver"]

    for item in [adjectives, elements, actions]:
        random.shuffle(item)

    # generate each attack card
    for i in range(num_action_cards):
        strength = random.choices(strengths, strength_weights)[0]
        movement = random.choices(movements, movement_weights)[0]
        distance = random.randint(1, max_distance)
        action_card = {
            "attack_name": f"{adjectives.pop()} {elements.pop()} {actions.pop()}",
            "strength": strength,
            "distance": distance,
            "movement": movement,
        }
        action_cards.append(action_card)
    return action_cards
