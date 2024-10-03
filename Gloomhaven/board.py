import random
from functools import partial
from character import CharacterType, Monster, Player
import copy
from collections import deque
from gh_types import ActionCard
from display import Display

EMPTY_CELL = "|      "
TERRAIN_DAMAGE = 1


# the board holds all the game metadata including the monster and player who are playing
# it adjudicates actions and ends the game
# the board draws itself as well!
class Board:
    # set the game up by getting info from the player, giving instructions if needed, and start the turns
    # continue turns until the game is over!
    def __init__(self, size: int, monsters: list[Monster], player: Player, disp: Display) -> None:
        self.size = size
        # TODO(john) - discuss with group whether to turn this into tuple
        # Possibly do not remove characters from tuple, just update statuses
        self.characters: list[CharacterType] = [player] + monsters
        self.locations = self._initialize_board(self.size, self.size)
        self.terrain = copy.deepcopy(self.locations)
        self.reshape_board()
        self.set_character_starting_locations()
        self.add_fire_to_terrain()
        # keep track of the display, and update it with the newly created locations and terrain
        self.disp = disp
        disp.locations = self.locations
        disp.terrain = self.terrain
        disp.characters = self.characters 

    def get_player(self) -> Player:
        for char in self.characters:
            if isinstance(char, Player):
                return char
        raise ValueError("Player not found on the board")

    def _initialize_board(self, width: int = 5, height=5):
        return [["X" for _ in range(width)] for _ in range(height)]

    def add_fire_to_terrain(self) -> None:
        max_loc = self.size - 1
        for i in range(10):
            row = random.randint(0, max_loc)
            col = random.randint(0, max_loc)
            # don't put fire on characters or map edge
            if self.locations[row][col] == None:
                self.terrain[row][col] = "FIRE"

    def carve_room(self, start_x: int, start_y: int, width: int, height: int) -> None:
        for x in range(start_x, min(start_x + width, self.size)):
            for y in range(start_y, min(start_y + height, self.size)):
                self.locations[x][
                    y
                ] = None  # Carving walkable room (None represents open space)

    def carve_hallway(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        # Horizontal movement first, then vertical
        x, y = start_x, start_y

        while x != end_x:
            if 0 <= x < self.size:
                self.locations[x][
                    y
                ] = None  # Carving walkable hallway (None represents open space)
            x += 1 if end_x > x else -1

        while y != end_y:
            if 0 <= y < self.size:
                self.locations[x][
                    y
                ] = None  # Carving walkable hallway (None represents open space)
            y += 1 if end_y > y else -1

    def reshape_board(self, num_rooms: int = 4) -> None:
        last_room_center = None

        for _ in range(num_rooms):
            # Random room size and position, ensuring it doesn't exceed map bounds
            room_width = random.randint(3, min(6, self.size))
            room_height = random.randint(3, min(6, self.size))
            start_x = random.randint(0, self.size - room_width)
            start_y = random.randint(0, self.size - room_height)

            self.carve_room(start_x, start_y, room_width, room_height)

            # Get the center of the current room
            current_room_center = (
                start_x + room_width // 2,
                start_y + room_height // 2,
            )

            # Connect this room to the last room with a hallway if it's not the first room
            if last_room_center:
                self.carve_hallway(
                    last_room_center[0],
                    last_room_center[1],
                    current_room_center[0],
                    current_room_center[1],
                )

            # Update last_room_center for the next iteration
            last_room_center = current_room_center

        # self.locations[0][0] = "X"
        # for i in range(3):
        #     for j in range(3):
        #         if i + j < 3:
        #             self.locations[i][j] = "X"
        #             self.locations[-i - 1][-j - 1] = "X"
        #             self.locations[i][-j - 1] = "X"
        #             self.locations[-i - 1][j] = "X"

    def set_character_starting_locations(self) -> None:
        for x in self.characters:
            self.pick_unoccupied_location(x)

    def get_shortest_valid_path(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """
        Finds the shortest valid path between a start and end coordinate in (row, col) format.
        Valid movements are up, down, left, right.
        Will avoid non-empty cells except for end cell.

        Returns path as list of coordinates which includes the end cell, but not the
        starting cell.
        Returns empty list if it is impossible to reach the end.
        """
        directions = [
            (1, 0),  # Down
            (0, 1),  # Right
            (-1, 0),  # Up
            (0, -1),  # Left
            (-1, 1),  # NE
            (1, 1),  # SE
            (1, -1),  # SW
            (-1, -1),  # NW
        ]
        end = tuple(end)
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

    def generate_path(
        self,
        previous_cell: dict[tuple[int, int], tuple[int, int]],
        end: tuple[int, int],
    ) -> list[tuple[int, int]]:
        path = []
        current: tuple[int, int] | None = end
        while current:
            path.append(current)
            current = previous_cell.get(current)
        path.reverse()
        path = path[1:]  # drop the starting position
        return path

    def pick_unoccupied_location(self, actor: CharacterType) -> None:
        while True:
            rand_location = [
                random.randint(0, self.size - 1),
                random.randint(0, self.size - 1),
            ]
            if not self.locations[rand_location[0]][rand_location[1]]:
                self.locations[rand_location[0]][rand_location[1]] = actor
                break

    def _print_healths(self) -> None:
        print_str = ""
        for x in self.characters:
            print_str += f"{x.name} Health: {x.health}\n"
        print(print_str)

    # draw the game board and display stats
    def draw(self) -> None:
        self._print_healths()
        to_draw = ""
        top = ""
        for i in range(self.size):
            top = " ------" * self.size + "\n"
            sides = ""
            for j in range(self.size):
                if isinstance(self.locations[i][j], Player):
                    sides += "|  🧙  "
                elif isinstance(self.locations[i][j], Monster):
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
    def is_attack_in_range(
        self, attack_distance: int, attacker: CharacterType, target: CharacterType
    ) -> bool:
        attacker_location = self.find_location_of_target(attacker)
        target_location = self.find_location_of_target(target)
        dist_to_target = len(
            self.get_shortest_valid_path(attacker_location, target_location)
        )
        return attack_distance >= dist_to_target

    def find_location_of_target(self, target) -> tuple[int, int]:
        for row_num, row in enumerate(self.locations):
            for column_num, item_in_locations in enumerate(row):
                if target == item_in_locations:
                    return (row_num, column_num)
        raise ValueError(f"Target {target} not found in locations")

    def find_opponents(self, actor: CharacterType) -> list[CharacterType]:
        return [
            pot_opponent
            for pot_opponent in self.characters
            if not isinstance(pot_opponent, type(actor))
        ]

    def attack_target(
        self, action_card: ActionCard, attacker: CharacterType, target: CharacterType
    ) -> None:
        print(
            f"Attempting attack with strength {action_card['strength']} and range {action_card['distance']}\n"
        )

        if target is None or (
            not self.is_attack_in_range(action_card["distance"], attacker, target)
        ):
            print("Not close enough to attack")
            return

        modified_attack_strength = select_and_apply_attack_modifier(
            action_card["strength"]
        )
        if modified_attack_strength <= 0:
            print("Darn, attack missed!")
            return

        print("Attack hits!\n")
        print(f"After the modifier, attack strength is: {modified_attack_strength}")

        self.modify_target_health(target, modified_attack_strength)

    def update_locations(self, row, col, new_item):
        self.locations[row][col] = new_item
        self.disp.update_locations(self.locations)

    def kill_target(self, target: CharacterType) -> None:
        self.characters.remove(target)
        row, col = self.find_location_of_target(target)
        self.update_locations(row, col, None)

    def find_in_range_opponents(
        self, actor: CharacterType, action_card: ActionCard
    ) -> list[CharacterType]:
        opponents = self.find_opponents(actor)
        for opponent in opponents:
            if not self.is_attack_in_range(action_card["distance"], actor, opponent):
                opponents.remove(opponent)
        return opponents

    def move_character_toward_location(
        self,
        acting_character: CharacterType,
        target_location: tuple[int, int],
        movement: int,
    ) -> None:
        if movement == 0:
            return

        acting_character_loc = self.find_location_of_target(acting_character)
        # get path
        path_to_target = self.get_shortest_valid_path(
            start=acting_character_loc, end=target_location
        )
        path_traveled = []
        # if we can't go all the way, get the furthest position we can go

        if len(path_to_target) > movement:
            path_traveled = path_to_target[:movement]
        # check if the end point is unoccupied
        elif self.is_legal_move(path_to_target[-1][0], path_to_target[-1][1]):
            path_traveled = path_to_target
        # if it's occupied and one square away, you don't need to move
        elif len(path_to_target) == 1:
            return
        # if it's occupied and you need to move, move to one away
        else:
            path_traveled = path_to_target[:-1]
        # go along the path and take any terrain damage!
        for loc in path_traveled:
            self.deal_terrain_damage(acting_character, loc[0], loc[1])

        # put the character in the new location
        self.update_character_location(
            acting_character, acting_character_loc, path_traveled[-1]
        )

    def deal_terrain_damage(
        self, acting_character: CharacterType, row: int, col: int
    ) -> None:
        damage = self.get_terrain_damage(row, col)
        if damage:
            print(f"{acting_character.name} took {damage} damage from terrain")
            self.modify_target_health(acting_character, damage)

    def update_character_location(
        self,
        actor: CharacterType,
        old_location: tuple[int, int],
        new_location: tuple[int, int],
    ) -> None:
        self.update_locations(old_location[0], old_location[1], None)
        self.update_locations(new_location[0], new_location[1], actor)

    def is_legal_move(self, row: int, col: int) -> bool:
        is_position_within_board = (
            row >= 0 and col >= 0 and row < self.size and col < self.size
        )
        return is_position_within_board and self.locations[row][col] is None

    def get_terrain_damage(self, row: int, col: int) -> int:
        if self.terrain[row][col] == "FIRE":
            return TERRAIN_DAMAGE
        else:
            return 0

    def modify_target_health(self, target: CharacterType, damage: int) -> None:
        target.health -= damage
        print(f"New health: {target.health}")
        if target.health <= 0:
            self.kill_target(target)


def select_and_apply_attack_modifier(initial_attack_strength: int) -> int:
    def multiply(x, y):
        return x * y

    def add(x, y):
        return x + y

    attack_modifier_deck = [
        (partial(multiply, 2), "2x"),
        (partial(multiply, 0), "Null"),
    ]
    for modifier in [-2, -1, 0, 1, 2]:
        attack_modifier_deck.append((partial(add, modifier), f"{modifier:+d}"))

    attack_modifier_weights = [1, 1, 2, 10, 10, 10, 2]

    attack_modifier_function, modifier_string = random.choices(
        attack_modifier_deck, attack_modifier_weights
    )[0]
    print(f"Attack modifier: {modifier_string}")
    return attack_modifier_function(initial_attack_strength)
