import random
from functools import partial
import character
import helpers
import copy
from collections import deque

EMPTY_CELL = "|      "


def initialize_board(width=5, height=5):
    return [[None for _ in range(width)] for _ in range(height)]


# the board holds all the game metadata including the monster and player who are playing
# it adjudicates actions and ends the game
# the board draws itself as well!
class Board:
    # set the game up by getting info from the player, giving instructions if needed, and start the turns
    # continue turns until the game is over!
    def __init__(
        self, size: int, monster: character.Monster, player: character.Player
    ) -> None:
        self.size = size
        self.characters = [monster, player]
        self.locations = initialize_board(self.size, self.size)
        self.terrain = copy.deepcopy(self.locations)
        self.add_fire_to_terrain()
        self.add_obstacles()
        self.set_character_starting_locations()
        self.game_status = "running"

        print(
            "Welcome to your quest, " + player.name + ". \n",
            "As you enter the dungeon, you see a terrifying monster ahead! \n",
            "Kill it or be killed...\n",
        )
        input("Time to start the game! Hit enter to continue\n")
        while self.game_status == "running":
            self.run_round()
            print(self.game_status)
        # once we're no longer playing, end the game
        if self.game_status != "running":
            print("what")
            print(self.game_status)
            self.end_game()

    def add_fire_to_terrain(self):
        max_loc = self.size - 1
        for i in range(10):
            self.terrain[random.randint(0, max_loc)][
                random.randint(0, max_loc)
            ] = "FIRE"
        return

    def add_obstacles(self):
        self.locations[0][0] = "X"
        for i in range(3):
            for j in range(3):
                if i + j < 3:
                    self.locations[i][j] = "X"
                    self.locations[-i - 1][-j - 1] = "X"
                    self.locations[i][-j - 1] = "X"
                    self.locations[-i - 1][j] = "X"

    def set_character_starting_locations(self):
        for x in self.characters:
            self.pick_unoccupied_location(x)

    def get_shortest_valid_path(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """
        Finds the shortest valid path between a start and end coordinate in (row, col) format.
        Valid movements are up, down, left, right.
        Will avoid non-empty cells except for end cell.

        Returns path as list of coordinates.
        """
        directions = [
            (1, 0),  # Down
            (0, 1),  # Right
            (-1, 0),  # Up
            (0, -1),  # Left
            (-1, 1), # NE
            (1, 1), # SE
            (1, -1), # SW
            (-1, -1), # NW
        ]
        max_row = max_col = self.size
        visited: set[tuple[int, int]] = set()

        previous_cell: dict[tuple[int, int], tuple[int, int]] = {}
        queue = deque([start])

        while queue:
            current = queue.popleft()

            if current == end:
                return self.generate_path(previous_cell, end)

            for direction in directions:
                new_row = current[0] + direction[0]
                new_col = current[1] + direction[1]
                new_pos = (new_row, new_col)

                if (
                    0 <= new_row < max_row
                    and 0 <= new_col < max_col
                    and new_pos not in visited
                ):
                    if self.is_legal_move(new_row, new_col) or new_pos == end:
                        queue.append(new_pos)
                        visited.add(new_pos)
                        previous_cell[new_pos] = current
        return []

    def generate_path(self, previous_cell, end):
        path = []
        current = end
        while current:
            path.append(current)
            current = previous_cell.get(current)
        path.reverse()
        path = path[1:] # drop the starting position
        return path

    def pick_unoccupied_location(self, actor):
        while True:
            rand_location = [
                random.randint(0, self.size - 1),
                random.randint(0, self.size - 1),
            ]
            if not self.locations[rand_location[0]][rand_location[1]]:
                self.locations[rand_location[0]][rand_location[1]] = actor
                break

    def print_healths(self):
        print_str = ""
        for x in self.characters:
            print_str += f"{x.name} Health: {x.health}\n"
        print(print_str)

    # draw the game board and display stats
    def draw(self):
        self.print_healths()
        to_draw = ""
        top = ""
        for i in range(self.size):
            top = " ------" * self.size + "\n"
            sides = ""
            for j in range(self.size):
                if isinstance(self.locations[i][j], character.Player):
                    sides += "|  🧙  "
                elif isinstance(self.locations[i][j], character.Monster):
                    sides += "|  🤖  "
                elif self.locations[i][j] == "X":
                    sides += "|  🪨   "
                else:
                    sides += EMPTY_CELL
            sides += EMPTY_CELL
            to_draw += top
            to_draw += sides + "\n"

            fire_sides = ""
            for j in range(self.size):
                if self.terrain[i][j] == "FIRE":
                    fire_sides += "|  🔥  "
                else:
                    fire_sides += EMPTY_CELL
            fire_sides += EMPTY_CELL
            to_draw += fire_sides + "\n"
        # add the bottom
        to_draw += top
        print(to_draw)

    # is the attack in range?
    def check_attack_in_range(self, attack_distance, attacker, target):
        attacker_location = self.find_location_of_target(attacker)
        target_location = self.find_location_of_target(target)
        dist_to_target = len(self.get_shortest_valid_path(
            attacker_location, target_location
        ))
        return attack_distance >= dist_to_target

    def find_location_of_target(self, target):
        for row_num, row in enumerate(self.locations):
            for column_num, item_in_locations in enumerate(row):
                if target == item_in_locations:
                    return row_num, column_num

    def find_opponents(self, actor):
        return [
            pot_opponent
            for pot_opponent in self.characters
            if not isinstance(pot_opponent, type(actor))
        ]

    def attack_target(self, action_card, attacker, target):
        modified_attack_strength = select_and_apply_attack_modifier(
            action_card["strength"]
        )
        print(
            f"Attempting attack with strength {action_card['strength']} and range {action_card['distance']}\n"
        )

        if target is None or (
            not self.check_attack_in_range(action_card["distance"], attacker, target)
        ):
            print("Not close enough to attack")
            return

        if modified_attack_strength <= 0:
            print("Darn, attack missed!")
            return

        print("Attack hits!\n")
        print(f"After the modifier, attack strength is: {modified_attack_strength}")

        self.modify_target_health(target, modified_attack_strength)

    def kill_target(self, target):
        self.characters.remove(target)
        row, col = self.find_location_of_target(target)
        self.locations[row][col] = None

    def check_and_update_game_status(self):
        # if all the monsters are dead, player wins
        if all(not isinstance(x, character.Monster) for x in self.characters):
            self.game_status = "player_win"
        # if all the players are dead, player loses
        elif all(not isinstance(x, character.Player) for x in self.characters):
            self.game_status = "player_loss"
        return

    def run_round(self):
        # randomize who starts the turn
        random.shuffle(self.characters)
        print("Start of Round!\n")
        for i, acting_character in enumerate(self.characters):
            # randomly pick who starts the round

            # For testing pathfinding. should create debug mode
            character1_pos = self.find_location_of_target(self.characters[0])
            character2_pos = self.find_location_of_target(self.characters[1])
            print(f"{character1_pos=} - {character2_pos=}")
            optimal_path = self.get_shortest_valid_path(character1_pos, character2_pos)
            print(f"{optimal_path=}")
            # end pathfinding test

            print(f"It's {acting_character.name}'s turn!")
            self.run_turn(acting_character)
            # !!! ideally the following lines would go in end_turn(), which is called at the end of run turn but then I don't know how to quit the for loop
            # !!! also the issue here is that if you kill all the monsters, you still move if you decide to
            # move after acting, which is not ideal
            self.check_and_update_game_status()
            if self.game_status != "running":
                return
        input("End of round. Hit Enter to continue")
        helpers.clear_terminal()

    def run_turn(self, acting_character):
        self.draw()
        action_card = acting_character.select_action_card()
        self.draw()
        move_first = acting_character.decide_if_move_first(action_card, self)

        # !!! check if there's a cleaner way to implement this
        if move_first:
            self.draw()
            acting_character.perform_movement(action_card, self)
            in_range_opponents = self.find_in_range_opponents(
                acting_character, action_card
            )
            self.draw()
            target = acting_character.select_attack_target(in_range_opponents)
            self.attack_target(action_card, acting_character, target)
        else:
            self.draw()
            in_range_opponents = self.find_in_range_opponents(
                acting_character, action_card
            )
            self.draw()
            target = acting_character.select_attack_target(in_range_opponents)
            self.attack_target(action_card, acting_character, target)
            acting_character.perform_movement(action_card, self)

        end_turn()

    def find_in_range_opponents(self, actor, action_card):
        opponents = self.find_opponents(actor)
        for opponent in opponents:
            if not self.check_attack_in_range(action_card["distance"], actor, opponent):
                opponents.remove(opponent)
        return opponents


    def move_character_toward_location(self, acting_character, target_location, movement):
        if movement == 0:
            return
        
        acting_character_loc = self.find_location_of_target(acting_character)
        # get path 
        # if len path <= movement
            # check if end is occupied
            # update movement to end of path or -1 if occupied
        # find the point on the path that's movement away and move there

        path_to_target = self.get_shortest_valid_path(start=acting_character_loc, end=target_location)
        new_loc = []
        # if we can't go all the way, get the furthest position we can go
        if len(path_to_target) > movement:
            new_loc = path_to_target[movement-1] 
        # check if the end point is unoccupied 
        elif self.is_legal_move(path_to_target[-1][0], path_to_target[-1][1]):
            new_loc = path_to_target[-1]
        # if it's occupied, go one less
        else:
            new_loc = path_to_target[-2]

        # put the character in the new location
        self.update_character_location(acting_character, acting_character_loc, new_loc)

    def update_character_location(self, actor, old_location, new_location):
        self.locations[old_location[0]][old_location[1]] = None
        self.locations[new_location[0]][new_location[1]] = actor

    def check_legality_and_move_character_in_direction(self, actor, direction):
        old_location = self.find_location_of_target(actor)
        new_location = [a + b for a, b in zip(old_location, direction)]
        if not self.is_legal_move(new_location[0], new_location[1]):
            return False
        self.locations[old_location[0]][old_location[1]] = None
        self.locations[new_location[0]][new_location[1]] = actor
        terrain_damage = self.get_terrain_damage(new_location[0], new_location[1])
        if terrain_damage:
            print(
                f"{actor.name} was damaged by the terrain for {terrain_damage} health"
            )
            self.modify_target_health(actor, terrain_damage)
        return True

    def is_legal_move(self, row, col):
        is_position_within_board = row >= 0 and col >= 0 and row < self.size and col < self.size
        return is_position_within_board and self.locations[row][col] is None

    def get_terrain_damage(self, row, col):
        if self.terrain[row][col] == "FIRE":
            return 1
        else:
            return None

    def modify_target_health(self, target, damage):
        target.health -= damage
        print(f"New health: {target.health}")
        if target.health <= 0:
            self.kill_target(target)

    def end_game(self):
        if self.game_status == "player_loss":
            lose_game()
        elif self.game_status == "player_win":
            win_game()
        else:
            raise ValueError(f"trying to end game when status is {self.game_status}")


def lose_game():
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
    return None


def win_game():
    helpers.clear_terminal()
    print("You defeated the monster!!")
    print("\n" r"    \o/   Victory!\n" "     |\n" "    / \\n" "   /   \\n" "        ")
    return None


def end_turn():
    input("End of turn. Hit enter to continue")
    helpers.clear_terminal()
    return


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
