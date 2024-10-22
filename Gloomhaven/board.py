import random
from functools import partial
import copy
from collections import deque
from character import CharacterType, Monster, Player
from gh_types import ActionCard
from display import Display
from listwithupdate import ListWithUpdate

EMPTY_CELL = "|      "
TERRAIN_DAMAGE = 1


# the board holds all the game metadata including the monster and player who are playing
# it adjudicates actions and ends the game
# the board draws itself as well!
class Board:
    # set the game up by getting info from the player, giving instructions if needed, and start the turns
    # continue turns until the game is over!
    def __init__(
        self, size: int, monsters: list[Monster], players: list[Player], disp: Display
    ) -> None:
        self.size = size
        self.disp = disp
        # TODO(john) - discuss with group whether to turn this into tuple
        # Possibly do not remove characters from tuple, just update statuses
        self.characters: list[CharacterType] = ListWithUpdate(
            players + monsters, self.disp.reload_display
        )
        self.locations = self._initialize_map(self.size, self.size)
        self.terrain = self._initialize_map(self.size, self.size)
        self.reshape_board()
        self.set_character_starting_locations()
        self.add_fire_to_terrain()
        self.log = ListWithUpdate([], self.disp.add_to_log)

    @property
    def locations(self):
        return self.__locations

    @locations.setter
    def locations(self, locations):
        self.__locations = locations
        self.disp.locations = locations
        self.disp.reload_display()

    @property
    def terrain(self):
        return self.__terrain

    @terrain.setter
    def terrain(self, terrain):
        self.__terrain = terrain
        self.disp.terrain = terrain
        self.disp.reload_display()

    @property
    def characters(self):
        return self.__characters

    @characters.setter
    def characters(self, characters):
        self.__characters = characters
        self.disp.characters = characters
        self.disp.reload_display()

    # initializes a game map which is a list of ListWithUpdate
    # game maps are used to represent locations and terrain
    def _initialize_map(self, width: int = 5, height=5) -> list[ListWithUpdate]:
        return [
            ListWithUpdate(["X" for _ in range(width)], self.disp.reload_display)
            for _ in range(height)
        ]

    def add_fire_to_terrain(self) -> None:
        max_loc = self.size - 1
        for _ in range(10):
            row = random.randint(0, max_loc)
            col = random.randint(0, max_loc)
            # don't put fire on characters or map edge
            if self.locations[row][col] is None:
                self.terrain[row][col] = "FIRE"
    
    def add_fire_to_terrain_for_attack(self, row, col) -> None:
        self.terrain[row][col] = "FIRE"


    def carve_room(self, start_x: int, start_y: int, width: int, height: int) -> None:
        for x in range(start_x, min(start_x + width, self.size)):
            for y in range(start_y, min(start_y + height, self.size)):
                # Carving walkable room (None represents open space)
                self.locations[x][y] = None

    def carve_hallway(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        # Horizontal movement first, then vertical
        x, y = start_x, start_y

        while x != end_x:
            if 0 <= x < self.size:
                # Carving walkable hallway (None represents open space)
                self.locations[x][y] = None
            x += 1 if end_x > x else -1

        while y != end_y:
            if 0 <= y < self.size:
                # Carving walkable hallway (None represents open space)
                self.locations[x][y] = None
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

    # is the attack in range?
    def is_attack_in_range(
        self, attack_distance: int, attacker: CharacterType, target: CharacterType
    ) -> bool:
        attacker_location = self.find_location_of_target(attacker)
        target_location = self.find_location_of_target(target)
        # BUG path_to_target might be [], which would make dist_to_target 0 and return True
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
        if target is None or (
            not self.is_attack_in_range(action_card["distance"], attacker, target)
        ):
            self.log.append("Not close enough to attack")
            return

        self.log.append(f"{attacker.name} is attempting to attack {target.name}")

        modified_attack_strength = self.select_and_apply_attack_modifier(
            action_card["strength"]
        )
        if modified_attack_strength <= 0:
            self.log.append("Darn, attack missed!")
            return

        self.log.append("Attack hits!\n")
        self.log.append(
            f"After the modifier, attack strength is: {modified_attack_strength}"
        )

        self.modify_target_health(target, modified_attack_strength)

    def update_locations(self, row, col, new_item):
        self.locations[row][col] = new_item

    def remove_character(self, target):
        self.characters.remove(target)
        # this method is not necessary as well, keeping it till we discuss

    def kill_target(self, target: CharacterType) -> None:
        # !!! to fix
        # weird bug where you can kill someone who's already killed
        # by walking through fire after you're dead since
        # movement doesn't auto-end
        # we need to fix this upstream by ending turn immediately when die,
        # not by ending turn after each action
        if target not in self.characters:
            return
        self.remove_character(target)
        row, col = self.find_location_of_target(target)
        self.update_locations(row, col, None)
        self.log.append(f"{target.name} has been killed.")
        # !!! for pair coding
        # !!! if the target is the player, end game
        # !!! if the target is the acting_character, end turn
        # - to do this, end turn and end game need to actually work, not just be place holders

    def find_in_range_opponents(
        self, actor: CharacterType, action_card: ActionCard
    ) -> list[CharacterType]:
        opponents = self.find_opponents(actor)
        in_range_opponents = []
        for opponent in opponents:
            if self.is_attack_in_range(action_card["distance"], actor, opponent):
                in_range_opponents.append(opponent)
        return in_range_opponents

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
        # BUG path_to_target might be [] leading to an error in is_legal_move's arguments below
        # discuss how we want to proceed if there is no path to chosen target
        # found this error when running simulations (uncommon even then)
        # human players will probably not pick an inaccessible target?

        path_to_target = self.get_shortest_valid_path(
            start=acting_character_loc, end=target_location
        )
        path_traveled = []

        # if there's not a way to get to target, don't move
        if not path_to_target:
            return
        # if we can't go all the way, get the furthest position we can go
        elif len(path_to_target) > movement:
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
            self.log.append(
                f"{acting_character.name} took {damage} damage from terrain"
            )
            self.modify_target_health(acting_character, damage)

    def deal_terrain_damage_current_location(self, acting_character: CharacterType):
        row, col = self.find_location_of_target(acting_character)
        self.deal_terrain_damage(acting_character, row, col)

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
        if target.health <= 0:
            self.kill_target(target)
        else:
            self.log.append(f"{target.name}'s new health: {target.health}")

    def select_and_apply_attack_modifier(self, initial_attack_strength: int) -> int:
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
        self.log.append(f"Attack modifier: {modifier_string}")
        return attack_modifier_function(initial_attack_strength)
