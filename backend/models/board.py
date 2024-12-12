from backend.models.character import Character
from collections import deque
import heapq
from itertools import count
import random
from typing import Type, Optional, Callable

import backend.models.agent as agent
import backend.models.character as character
from ..utils.listwithupdate import ListWithUpdate
import backend.models.pyxel_backend as pyxel_backend
import backend.models.obstacle as obstacle
from backend.utils import attack_shapes as shapes
from backend.utils.utilities import DieAndEndTurn, directions


MAX_ROUNDS = 1000
EMPTY_CELL = "|      "


PositionPathResult = tuple[
    list[tuple[int, int]], dict[tuple[int, int], list[tuple[int, int]]]
]


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
            shapes.line(random.randint(2, 3)),
            shapes.arc(random.randint(2, 3)),
            shapes.cone(random.randint(1, 2)),
            shapes.ring(random.randint(2, 3)),
        ]
        for element in starting_elements:
            self.add_starting_effect_to_terrain(element, 1000)
        pyxel_manager.load_board(self.locations, self.terrain)
        # pyxel_manager.load_characters(self.characters)
        self.acting_character = None

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
        attack_coords: list[tuple[int, int]],
    ) -> None:
        """
        if you want this to also do damage, you must pass damage and an attacker
        """
        for effect_row, effect_col in attack_coords:
            # check if row and col are in bounds
            if 0 <= effect_row < len(self.terrain):
                if 0 <= effect_col < len(self.terrain[effect_row]):
                    potential_char = self.locations[effect_row][effect_col]
                    # do not add terrain effects where walls are
                    if isinstance(potential_char, obstacle.Wall):
                        continue
                    terrain_obj = effect_type(self.round_num, next(self.id_generator))
                    # if there's something there already, and it's the same element
                    # adopt its frontend id and update its backend info
                    # this prevents weird frontend effects from clearing and reapplying
                    # the same element
                    if type(self.terrain[effect_row][effect_col]) is type(terrain_obj):
                        terrain_obj.id = self.terrain[effect_row][effect_col].id
                        self.terrain[effect_row][effect_col] = terrain_obj
                    # otherwise, clear it and push new element to front end
                    else:
                        self.clear_terrain_square(effect_row, effect_col)
                        self.terrain[effect_row][effect_col] = terrain_obj
                        self.pyxel_manager.add_entity(
                            terrain_obj, effect_row, effect_col
                        )
                    # if there's a character there, deal damage to them unless it's ice
                    if (
                        isinstance(potential_char, Character)
                        and not effect_type == obstacle.Ice
                    ):
                        self.deal_terrain_damage(
                            potential_char, effect_row, effect_col, movement=False
                        )

    def attack_area(
        self, attacker: Character, attack_coords: list[tuple[int, int]], strength: int
    ) -> None:
        self.pyxel_manager.highlight_map_tiles(
            attack_coords, "ALL_FRONTEND", persist=False
        )
        for attack_row, attack_col in attack_coords:
            # check if row and col are in bounds
            if 0 <= attack_row < len(self.locations):
                if 0 <= attack_col < len(self.locations[attack_row]):
                    potential_char = self.locations[attack_row][attack_col]
                    # if there's a character there, deal damage to them
                    # removing friendly fire, which hasn't been so fun
                    if (
                        isinstance(potential_char, Character)
                        and potential_char.team_monster != attacker.team_monster
                    ):
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

    def find_all_jumpable_positions(
        self,
        start: tuple[int, int],
        num_moves: int,
    ) -> PositionPathResult:
        """
        Finds all valid jumpable positions within `num_moves` where diagonal movements
        cost as much as cardinal movements. We never push/pull with jump, so there's no
        additional movement check here

        Args:
            start: Starting position as (row, col)
            num_moves: Maximum jump distance

        Returns:
            List of valid jumpable positions as normalized and flipped (col, row)
            for Pyxel compatibility and a blank dict to maintain consistency in function
            sugnatures with find_all_reachable_paths()
        """
        # Since we cannot jump over walls, we will get all jumpable positions by calling
        # find_all_reachable_paths with exclude_walls_only set to True, then we will
        # remove all character locations to prevent jumping onto them.
        jumpable_positions, _ = self.find_all_reachable_paths(
            start, num_moves, exclude_walls_only=True
        )

        # remove character locations. can be more efficient if self.locations is a set
        jumpable_positions = [
            (pos_x, pos_y)
            for pos_x, pos_y in jumpable_positions
            if self.locations[pos_x][pos_y] is None
        ]

        return jumpable_positions, {}

    def find_all_reachable_paths(
        self,
        start: tuple[int, int],
        num_moves: int,
        exclude_walls_only: bool = False,
        additional_movement_check: Optional[
            Callable[[tuple[int, int], tuple[int, int]], bool]
        ] = None,
    ) -> PositionPathResult:
        """
        Finds all positions reachable within the movement range and the shortest path to each position.

        NOTE: All positions are flipped and then normalized!

        Args:
            start: Starting position as (row, col)
            num_moves: Maximum number of moves allowed
            exclude_walls_only: Only considers walls as an invalid position - useful when using this
                to find potential attack square targets for area attacks

        Returns:
            A tuple containing:
            - list[tuple[int, int]]: All reachable positions, excluding the start position.
              Use this for highlighting possible destinations.
            - dict[tuple[int, int], list[tuple[int, int]]]: Maps each reachable position
              to its shortest valid path from the start position. Each path is a list of
              coordinates excluding the start position. Use this for showing movement
              preview when hovering over a destination.

        """
        reachable_positions = set()
        queue = deque([(start, 0)])
        visited = {start}

        # BFS to find all reachable positions
        while queue:
            current_pos, distance = queue.popleft()

            # prevents us from considering starting point
            if distance > 0:
                reachable_positions.add(current_pos)

            if distance < num_moves:
                valid_surrounding_positions = [
                    (new_row, new_col)
                    for d_row, d_col in directions
                    if (
                        new_row := current_pos[0] + d_row,
                        new_col := current_pos[1] + d_col,
                    )
                    not in visited
                    and (
                        # only excluding walls and it's in bounds and not a wall
                        (
                            exclude_walls_only
                            and new_row < self.size
                            and new_col < self.size
                            and not isinstance(
                                self.locations[new_row][new_col], obstacle.Wall
                            )
                        )
                        # there's no movement check and it's a legal move
                        or (
                            self.is_legal_move(new_row, new_col)
                            and additional_movement_check is None
                        )
                        # movement check exists, you pass the movement check, and it's a legal move
                        or (
                            self.is_legal_move(new_row, new_col)
                            and additional_movement_check(
                                current_pos, (new_row, new_col)
                            )
                        )
                    )
                ]
                visited.update(valid_surrounding_positions)
                queue.extend((pos, distance + 1) for pos in valid_surrounding_positions)

        # Iterate over reachable positions and find shortest valid routes
        reachable_paths = {}
        for end_pos in reachable_positions:
            if path := self.get_shortest_valid_path(
                start=start, end=end_pos, num_moves=num_moves
            ):
                reachable_paths[end_pos] = path

        return reachable_positions, reachable_paths

    def get_shortest_valid_path(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
        is_jump: bool = False,
        num_moves: int = 100,
    ) -> list[tuple[int, int]]:
        """
        Finds the shortest valid path between a start and end coordinate in (row, col) format.
        Can move in all 8 directions.

        When is_jump is True and we're at exactly num_moves distance, checks is_legal_move
        with is_jump=False to ensure the final position is valid.

        Args:
            start: Starting position as (row, col)
            end: Target position as (row, col)
            is_jump: Whether jumping over obstacles is allowed
            num_moves: If positive, specifies the exact movement distance where we need to check
                      is_legal_move with is_jump=False

        Returns path as list of coordinates which includes the end cell, but not the
        starting cell.
        Returns empty list if it is impossible to reach the end.
        """

        closed: set[tuple[int, int]] = set()

        previous_cell: dict[tuple[int, int], tuple[int, int]] = {}
        priority_queue: list = []
        heapq.heappush(priority_queue, (0, start))

        g_scores = {start: 0}

        def calculate_chebyshev_distance(
            pos_a: tuple[int, int], pos_b: tuple[int, int]
        ) -> int:
            return max(abs(pos_a[0] - pos_b[0]), abs(pos_a[1] - pos_b[1]))

        def is_valid_jump_path(path: list, end: tuple) -> bool:
            """
            returns true if the landing position (smaller of num_moves or path length)
            is legal or second to last move is legal if the landing position is target
            """
            if not path:
                return True
            position_index = min(num_moves - 1, len(path) - 1)
            position = path[position_index]

            # First check if landing position is legal
            if self.is_legal_move(
                position[0], position[1], jump_intermediate_move=False
            ):
                return True

            # If not, check if previous position exists and is legal
            if position_index > 0 and position == end:
                prev_pos = path[position_index - 1]
                if self.is_legal_move(
                    prev_pos[0], prev_pos[1], jump_intermediate_move=False
                ):
                    return True

            return False

        while priority_queue:
            _, current = heapq.heappop(priority_queue)

            if current == end:
                path = self.generate_path(previous_cell, end)
                # only return the path if it's a valid path
                if not is_jump or is_valid_jump_path(path, end):
                    return path

            if current in closed:
                continue

            valid_neighbors = [
                (new_pos, new_g)
                for d_row, d_col in directions
                if (new_pos := (current[0] + d_row, current[1] + d_col)) not in closed
                and (self.is_legal_move(*new_pos, is_jump) or new_pos == end)
                and (new_g := g_scores[current] + 1)
                < g_scores.get(new_pos, float("inf"))
            ]

            for new_pos, new_g_score in valid_neighbors:
                g_scores[new_pos] = new_g_score
                h_score = calculate_chebyshev_distance(new_pos, end)
                # punish moves that go diagonally but don't have to by adding a small penalty
                is_diagonal = (
                    abs(new_pos[0] - current[0]) + abs(new_pos[1] - current[1]) == 2
                )  # True for diagonal moves
                tiebreaker = 0.001 if is_diagonal else 0
                heapq.heappush(
                    priority_queue, (new_g_score + h_score + tiebreaker, new_pos)
                )
                # heapq.heappush(priority_queue, (new_g_score + h_score, new_pos))
                previous_cell[new_pos] = current

            closed.add(current)

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
            modified_attack_strength = 0
            to_log += f", does no damage!\n"
        elif self.is_shadow_interference(attacker, target):
            modified_attack_strength = 0
            to_log += f", missed due to shadow\n"
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

    def kill_target(self, target: Character, damage_str: str = "") -> None:
        if target not in self.characters:
            return
        self.remove_character(target)
        row, col = self.find_location_of_target(target)
        self.update_locations(row, col, None)
        self.pyxel_manager.remove_entity(target.id, show_death_animation=True)
        died_by = f" by{damage_str}" if damage_str else ""
        self.pyxel_manager.log.append(f"{target.name} has been killed{died_by}.")
        # if it's your turn, end it immediately
        if target == self.acting_character:
            raise DieAndEndTurn()

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
    ) -> int:
        if movement == 0:
            return 0

        acting_character_loc = self.find_location_of_target(acting_character)
        # get path
        path_to_target = self.get_shortest_valid_path(
            start=acting_character_loc,
            end=target_location,
            is_jump=is_jump,
            num_moves=movement,
        )
        path_traveled = []
        path_length_jump = 0

        # if there's not a way to get to target, don't move
        if not path_to_target:
            return 0
        # if we can't go all the way, get the furthest position we can go
        elif len(path_to_target) > movement:
            path_traveled = path_to_target[:movement]
        # check if the end point is unoccupied
        elif self.is_legal_move(path_to_target[-1][0], path_to_target[-1][1]):
            path_traveled = path_to_target
        # if it's occupied and one square away, you don't need to move
        elif len(path_to_target) == 1:
            return 0
        # if it's occupied and you need to move, move to one away
        else:
            path_traveled = path_to_target[:-1]
        # go along the path and take any terrain damage! if you jump, go straight to end
        if is_jump:
            path_length_jump = len(path_traveled)
            path_traveled = path_traveled[-1:]
        for loc in path_traveled:
            # if they die during the movement, move on
            if acting_character not in self.characters:
                return
            # move character one step
            self.update_character_location(
                acting_character, acting_character_loc, loc, is_jump
            )
            acting_character_loc = loc
            # humans move step by step, so they should not take damage on a jump - we'll have them take damage
            # at the end of their movement later
            if not (is_jump and isinstance(acting_character.agent, agent.Human)):
                self.deal_terrain_damage(acting_character, loc[0], loc[1])
        return max(len(path_traveled), path_length_jump)

    def deal_terrain_damage(
        self, affected_character: Character, row: int, col: int, movement: bool = True
    ) -> None:
        """
        deals terrain damage to a character
        if movement = True, this is because the character steps onto a square
        if movement = False this is because the element was thrown onto a character or
        they started their turn in that element
        ice slipping should only apply when movement = True
        """
        element = self.terrain[row][col]
        if not element:
            return
        damage = element.damage
        # if it's not ice or it's ice and they're moving, you can have the element perform
        # this is to avoid slipping when ice is thrown at you or when you start
        # your turn on ice
        if not isinstance(element, obstacle.Ice) or movement:
            element.perform(row, col, self, affected_character)
        # if they have an elemental affinity for this element, they heal instead of take damage
        if affected_character.elemental_affinity == element.__class__:
            self.pyxel_manager.log.append(
                f"{affected_character.name} has an affinity for {element.__class__.__name__}"
            )
            damage = damage * -1
        if damage:
            self.modify_target_health(
                affected_character, damage, element.__class__.__name__
            )
        # if it's rotting flesh and doesn't do damage:
        elif isinstance(element, obstacle.RottingFlesh):
            self.pyxel_manager.log.append(
                f"{affected_character.name} avoided infection from RottingFlesh"
            )

    def deal_terrain_damage_current_location(self, affected_character: Character):
        """
        deals terrain damage for the start of the turn - set movement to false
        so you don't slip when you start on ice
        """
        row, col = self.find_location_of_target(affected_character)
        self.deal_terrain_damage(affected_character, row, col, movement=False)

    def update_character_location(
        self,
        actor: Character,
        old_location: tuple[int, int],
        new_location: tuple[int, int],
        is_jump: bool = False,
    ) -> None:
        # Add action queue logic here.
        self.update_locations(old_location[0], old_location[1], None)
        self.update_locations(new_location[0], new_location[1], actor)
        self.pyxel_manager.move_character(actor, old_location, new_location, is_jump)

    def is_legal_move(self, row: int, col: int, jump_intermediate_move=False) -> bool:
        is_position_within_board = (
            row >= 0 and col >= 0 and row < self.size and col < self.size
        )
        # for jumping, we can jump through any obstacles and players
        # but we have to stay on board and can't go through walls
        if jump_intermediate_move:
            return is_position_within_board and not isinstance(
                self.locations[row][col], obstacle.Wall
            )
        else:
            return is_position_within_board and self.locations[row][col] is None

    def modify_target_health(
        self, target: Character, damage: int, damage_str: str = ""
    ) -> None:
        """
        Modifies the target health by subtracting damage. For a heal,
        pass negative damage.
        """
        if damage == 0:
            return
        # if it's a heal (negative damage) and you have max health, do nothing
        if target.health == target.max_health and damage < 0:
            return
        # add needed spacing if we have a string
        damage_str = " " + damage_str if damage_str else damage_str
        # if this is a heal (damage is -), don't allow them to heal beyond max health
        target.health = min(target.health - damage, target.max_health)
        if target.health <= 0:
            self.pyxel_manager.log.append(
                f"{target.name} takes {damage}{damage_str} damage"
            )
            self.kill_target(target, damage_str)
        elif damage > 0:
            self.pyxel_manager.log.append(
                f"{target.name} takes {damage}{damage_str} damage and has {target.health} health"
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

    def update_character_statuses(self, char: Character):
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
            # if the character died during the movement, move on
            if target not in self.characters:
                return
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
