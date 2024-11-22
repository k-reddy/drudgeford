from backend.models.character import Character
import heapq
import random
from itertools import count
from typing import Type

import backend.models.agent as agent
import backend.models.character as character
from backend.models.display import Display
from ..utils.listwithupdate import ListWithUpdate
import backend.models.pyxel_backend as pyxel_backend
import backend.models.obstacle as obstacle
from backend.utils import attack_shapes as shapes


MAX_ROUNDS = 1000
EMPTY_CELL = "|      "


# the board holds all the game metadata including the monster and player who are playing
# it adjudicates actions and ends the game
# the board draws itself as well!
class Board:
    # set the game up by getting info from the player, giving instructions if needed, and start the turns
    # continue turns until the game is over!
    def __init__(
        self,
        size: int,
        monsters: list[character.Character],
        players: list[character.Character],
        pyxel_manager: pyxel_backend.PyxelManager,
        id_generator: count,
        starting_elements: list[obstacle.TerrainObject],
    ) -> None:
        self.round_num = 0
        self.size = size
        self.id_generator = id_generator
        self.pyxel_manager = pyxel_manager

        self.characters: list[character.Character] = ListWithUpdate(
            players + monsters, self.pyxel_manager.load_characters
        )
        # self.characters: list[character.Character] = players + monsters
        # self.characters=players+monsters

        self.locations = self._initialize_map(self.size, self.size)
        self.terrain = self._initialize_terrain(self.size, self.size)
        self.reshape_board()
        self.set_character_starting_locations()

        self.potential_shapes = [
            shapes.line((1, 0), random.randint(2, 3)),
            shapes.line((0, 1), random.randint(2, 3)),
            shapes.arc(random.randint(2, 3)),
            shapes.cone(random.randint(1, 2)),
            shapes.ring(random.randint(2, 3)),
        ]
        for element in starting_elements:
            self.add_starting_effect_to_terrain(element, 1000)
        pyxel_manager.load_board(self.locations, self.terrain)
        pyxel_manager.load_characters(self.characters)

    # @property
    # def locations(self):
    #     return self.__locations

    # @locations.setter
    # def locations(self, locations):
    #     self.__locations = locations
    #     self.disp.locations = locations
    #     self.disp.reload_display()

    # @property
    # def terrain(self):
    #     return self.__terrain

    # @terrain.setter
    # def terrain(self, terrain):
    #     self.__terrain = terrain
    #     self.disp.terrain = terrain
    #     self.disp.reload_display()

    # @property
    # def characters(self):
    #     return self.__characters

    # @characters.setter
    # def characters(self, characters):
    #     self.__characters = characters
    #     self.disp.characters = characters
    #     # self.pyxel_manager.load_characters(characters)
    #     self.disp.reload_display()

    # initializes a game map which is a list of ListWithUpdate
    # game maps are used to represent locations and terrain
    def _initialize_map(self, width: int = 5, height=5) -> list:
        return [
            [
                obstacle.Wall(round_num=0, obj_id=next(self.id_generator))
                for _ in range(width)
            ]
            for _ in range(height)
        ]

    def _initialize_terrain(self, width: int = 5, height=5) -> list:
        return [[None for _ in range(width)] for _ in range(height)]

    def add_starting_effect_to_terrain(
        self, effect_type: Type[obstacle.TerrainObject], num_tries: int
    ) -> None:
        # pick a random shape for our element, and use each one only once
        shape_offsets = random.choice(self.potential_shapes)
        self.potential_shapes.remove(shape_offsets)
        max_loc = self.size - 1
        # try to start the shape on a random square
        for _ in range(num_tries):
            row = random.randint(0, max_loc)
            col = random.randint(0, max_loc)
            # if we can't draw our whole shape, try again
            if not self.whole_shape_unoccupied(row, col, shape_offsets):
                continue
            # otherwise, draw!
            for offset in shape_offsets:
                self.add_starting_effect_if_valid_square(
                    row + offset[0], col + offset[1], effect_type
                )
            return

    def whole_shape_unoccupied(self, row, col, shape_offsets):
        shape_coords = [(row + offset[0], col + offset[1]) for offset in shape_offsets]
        for coord in shape_coords:
            if coord[0] >= self.size or coord[1] >= self.size:
                return False
            if self.locations[coord[0]][coord[1]] is not None:
                return False
        return True

    def add_starting_effect_if_valid_square(
        self, row, col, effect_type: Type[obstacle.TerrainObject]
    ) -> bool:
        if row >= self.size or col >= self.size:
            return False
        if self.locations[row][col] is None:
            terrain_obj = effect_type(self.round_num, next(self.id_generator))
            self.terrain[row][col] = terrain_obj
            return True
        return False

    def add_effect_to_terrain_for_attack(
        self,
        effect_type: Type[obstacle.TerrainObject],
        row: int,
        col: int,
        shape: set,
    ) -> None:
        for coordinate in shape:
            effect_row = row + coordinate[0]
            effect_col = col + coordinate[1]
            # check if row and col are in bounds
            if 0 <= effect_row < len(self.terrain):
                if 0 <= effect_col < len(self.terrain[effect_row]):
                    potential_char = self.locations[effect_row][effect_col]
                    # do not add terrain effects where walls are
                    if isinstance(potential_char, obstacle.Wall):
                        continue
                    terrain_obj = effect_type(self.round_num, next(self.id_generator))
                    # if there's something there already, clear it
                    self.clear_terrain_square(effect_row, effect_col)
                    self.terrain[effect_row][effect_col] = terrain_obj
                    self.pyxel_manager.add_entity(terrain_obj, effect_row, effect_col)
                    # if there's a character there, deal damage to them unless it's ice
                    if (
                        isinstance(potential_char, Character)
                        and not effect_type == obstacle.Ice
                    ):
                        self.deal_terrain_damage(potential_char, effect_row, effect_col)

    def attack_area(self, attacker: Character, shape: set, strength: int) -> None:
        starting_coord = self.find_location_of_target(attacker)
        # don't attack yourself
        shape.discard((0, 0))
        for coordinate in shape:
            attack_row = starting_coord[0] + coordinate[0]
            attack_col = starting_coord[1] + coordinate[1]
            # check if row and col are in bounds
            if 0 <= attack_row < len(self.locations):
                if 0 <= attack_col < len(self.locations[attack_row]):
                    potential_char = self.locations[attack_row][attack_col]
                    # if there's a character there, deal damage to them
                    # note: this allows friendly fire, which I think is fun
                    if isinstance(potential_char, Character):
                        self.attack_target(attacker, strength, potential_char)

    def set_obstacles_in_area(
        self, starting_coord, shape: set, obstacle_type: Type[obstacle.TerrainObject]
    ):
        for coordinate in shape:
            obstacle_row = starting_coord[0] + coordinate[0]
            obstacle_col = starting_coord[1] + coordinate[1]
            # check if row and col are in bounds
            if 0 <= obstacle_row < len(self.locations):
                if 0 <= obstacle_col < len(self.locations[obstacle_row]):
                    # if it's unoccupied, place obstacle there
                    if not self.locations[obstacle_row][obstacle_col]:
                        obs = obstacle_type(
                            self.round_num, obj_id=next(self.id_generator)
                        )
                        self.locations[obstacle_row][obstacle_col] = obs
                        self.pyxel_manager.add_entity(
                            obs,
                            obstacle_row,
                            obstacle_col,
                        )

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
        last_room_center: tuple = ()

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

    def set_character_starting_locations(self) -> None:
        for x in self.characters:
            row, col = self.pick_unoccupied_location()
            self.locations[row][col] = x

    def get_shortest_valid_path(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """
        Finds the shortest valid path between a start and end coordinate in (row, col) format.
        Can move in all 8 directions.

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
        closed: set[tuple[int, int]] = set()

        previous_cell: dict[tuple[int, int], tuple[int, int]] = {}
        priority_queue: list = []
        heapq.heappush(priority_queue, (0, start))

        g_scores = {start: 0}

        def calculate_chebyshev_distance(
            pos_a: tuple[int, int], pos_b: tuple[int, int]
        ) -> int:
            return max(abs(pos_a[0] - pos_b[0]), abs(pos_a[1] - pos_b[1]))

        while priority_queue:
            _, current = heapq.heappop(priority_queue)

            if current == end:
                return self.generate_path(previous_cell, end)

            if current in closed:
                continue

            closed.add(current)

            for direction in directions:
                new_row = current[0] + direction[0]
                new_col = current[1] + direction[1]
                new_pos = (new_row, new_col)
                if new_pos not in closed and (
                    self.is_legal_move(new_row, new_col) or new_pos == end
                ):
                    new_g_score = g_scores[current] + 1
                    if new_pos not in g_scores or new_g_score < g_scores[new_pos]:
                        h_score = calculate_chebyshev_distance(new_pos, end)
                        g_scores[new_pos] = new_g_score
                        f_score = new_g_score + h_score
                        heapq.heappush(priority_queue, (f_score, new_pos))
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

    def pick_unoccupied_location(self) -> tuple[int, int]:
        while True:
            rand_location = (
                random.randint(0, self.size - 1),
                random.randint(0, self.size - 1),
            )
            if not self.locations[rand_location[0]][rand_location[1]]:
                return rand_location

    # is the attack in range?
    def is_attack_in_range(
        self, attack_distance: int, attacker: Character, target: Character
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

    def find_opponents(self, actor: Character) -> list[Character]:
        return [
            pot_opponent
            for pot_opponent in self.characters
            if pot_opponent.team_monster != actor.team_monster
        ]

    def find_allies(self, actor: Character) -> list[Character]:
        return [
            pot_opponent
            for pot_opponent in self.characters
            if pot_opponent.team_monster == actor.team_monster
        ]

    def attack_target(self, attacker, strength, target):
        modified_attack_strength, attack_modifier_string = (
            self.select_and_apply_attack_modifier(attacker, strength)
        )
        to_log = (
            f"\nAttack targets {target.name} with {attack_modifier_string} modifier"
        )
        if target.shield[0] > 0:
            to_log += f"\n{target.name} has shield {target.shield[0]}"
            modified_attack_strength -= target.shield[0]
        if modified_attack_strength <= 0:
            to_log += f", does no damage!\n"
            return
        if self.is_shadow_interference(attacker, target):
            to_log += f", missed due to shadow\n"
            return
        self.pyxel_manager.log.append(to_log)
        self.modify_target_health(target, modified_attack_strength)

    def is_shadow_interference(self, attacker, target):
        """returns true if the attack misses due to shadow"""
        attacker_loc = self.find_location_of_target(attacker)
        target_path = self.get_shortest_valid_path(
            attacker_loc, self.find_location_of_target(target)
        )
        chance_of_miss = 0
        target_path += [attacker_loc]
        for coord in target_path:
            if isinstance(self.terrain[coord[0]][coord[1]], obstacle.Shadow):
                chance_of_miss += 0.1
        return random.random() < chance_of_miss

    def update_locations(self, row, col, new_item):
        self.locations[row][col] = new_item

    def remove_character(self, target):
        self.characters.remove(target)
        self.pyxel_manager.load_characters(self.characters)
        # this method is not necessary as well, keeping it till we discuss

    def kill_target(self, target: Character) -> None:
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
        self.pyxel_manager.remove_entity(target.id)
        self.pyxel_manager.log.append(f"{target.name} has been killed.")
        # !!! for pair coding
        # !!! if the target is the player, end game
        # !!! if the target is the acting_character, end turn
        # - to do this, end turn and end game need to actually work, not just be place holders

    def find_in_range_opponents_or_allies(
        self, actor: Character, distance: int, opponents=True
    ) -> list[Character]:
        if opponents:
            chars = self.find_opponents(actor)
        else:
            chars = self.find_allies(actor)
        in_range_chars = []
        for char in chars:
            if self.is_attack_in_range(distance, actor, char):
                in_range_chars.append(char)
        return in_range_chars

    def move_character_toward_location(
        self,
        acting_character: Character,
        target_location: tuple[int, int],
        movement: int,
        is_jump=False,
    ) -> None:
        if movement == 0:
            return

        acting_character_loc = self.find_location_of_target(acting_character)
        # get path
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
        # go along the path and take any terrain damage! if you jump, go straight to end
        if is_jump and isinstance(acting_character.agent, agent.Ai):
            path_traveled = path_traveled[-1:]
        for loc in path_traveled:
            # move character one step
            self.update_character_location(acting_character, acting_character_loc, loc)
            acting_character_loc = loc
            # humans move step by step, so they should not take damage on a jump
            if not (is_jump and isinstance(acting_character.agent, agent.Human)):
                self.deal_terrain_damage(acting_character, loc[0], loc[1])

    def deal_terrain_damage(
        self,
        acting_character: Character,
        row: int,
        col: int,
    ) -> None:
        damage = self.get_terrain_damage(row, col)
        element = self.terrain[row][col]
        # if they have an elemental affinity for this element, they heal instead of take damage
        if acting_character.elemental_affinity == element.__class__:
            self.pyxel_manager.log.append(
                f"{acting_character.name} has an affinity for {element.__class__.__name__}"
            )
            damage = damage * -1
        if damage:
            self.pyxel_manager.log.append(
                f"{acting_character.name} stepped on {element.__class__.__name__}"
            )
            self.modify_target_health(acting_character, damage)

    def deal_terrain_damage_current_location(self, acting_character: Character):
        row, col = self.find_location_of_target(acting_character)
        self.deal_terrain_damage(acting_character, row, col)

    def update_character_location(
        self,
        actor: Character,
        old_location: tuple[int, int],
        new_location: tuple[int, int],
    ) -> None:
        # Add action queue logic here.
        self.update_locations(old_location[0], old_location[1], None)
        self.update_locations(new_location[0], new_location[1], actor)
        self.pyxel_manager.move_character(actor, old_location, new_location)

    def is_legal_move(self, row: int, col: int) -> bool:
        is_position_within_board = (
            row >= 0 and col >= 0 and row < self.size and col < self.size
        )
        return is_position_within_board and self.locations[row][col] is None

    def get_terrain_damage(self, row: int, col: int) -> int | None:
        el = self.terrain[row][col]
        if el:
            el.perform(row, col, self)
            return el.damage
        else:
            return None

    def modify_target_health(self, target: Character, damage: int) -> None:
        target.health -= damage
        if target.health <= 0:
            self.kill_target(target)
        elif damage > 0:
            self.pyxel_manager.log.append(
                f"{target.name} takes {damage} damage and has {target.health} health"
            )
        else:
            self.pyxel_manager.log.append(
                f"{target.name} heals for {-1*damage} and has {target.health} health"
            )
        # updating healths also affects the initiative bar
        self.pyxel_manager.load_characters(self.characters)

    def select_and_apply_attack_modifier(
        self, attacker, initial_attack_strength: int
    ) -> int:
        attack_modifier_function, modifier_string = attacker.attack_modifier_deck.pop()
        if len(attacker.attack_modifier_deck) == 0:
            attacker.make_attack_modifier_deck()
        return attack_modifier_function(initial_attack_strength), modifier_string

    def clear_terrain_square(self, row, col):
        el = self.terrain[row][col]
        if el:
            self.terrain[row][col] = None
            self.pyxel_manager.remove_entity(el.id)

    def update_terrain(self):
        for i, _ in enumerate(self.terrain):
            for j, el in enumerate(self.terrain[i]):
                # None is the default initialization
                if not el:
                    continue
                # if the terrain item was placed 2 or more rounds ago, clear it
                if self.round_num - el.round_placed > el.duration:
                    self.clear_terrain_square(i, j)

    def update_character_statuses(self):
        for char in self.characters:
            if char.shield[1] <= self.round_num:
                # reset to shield 0 indefinitely
                character.shield = (0, MAX_ROUNDS)

    def append_to_attack_modifier_deck(self, target: Character, modifier_card: tuple):
        target.attack_modifier_deck.append(modifier_card)

    def push(self, target: Character, direction, squares):
        """pushes characters in a straight line"""
        starting_location = self.find_location_of_target(target)
        destinations = []
        for i in range(squares):
            # scale the movement then add it to starting location
            destination = tuple(
                [a * (i + 1) + b for a, b in zip(direction, starting_location)]
            )
            destinations.append(destination)
        for destination in destinations:
            # force the algo to move the way we want, square by square
            self.move_character_toward_location(target, destination, 1, is_jump=False)

    def add_new_ai_char(self, is_monster, char_class: Type[Character]):
        from backend.models.agent import Ai

        new_char = char_class(
            f"Spooky {char_class.__name__}",
            self.pyxel_manager,
            "💀",
            Ai(),
            next(self.id_generator),
            is_monster=is_monster,
            log=self.pyxel_manager.log,
        )
        self.characters.append(new_char)
        row, col = self.pick_unoccupied_location()
        self.locations[row][col] = new_char
        self.pyxel_manager.add_entity(new_char, row, col)
        self.pyxel_manager.load_characters(self.characters)

    def teleport_character(self, target: Character):
        self.pyxel_manager.log.append(f"Teleporting {target.name}")
        new_loc = self.pick_unoccupied_location()
        self.update_character_location(
            target, self.find_location_of_target(target), new_loc
        )
