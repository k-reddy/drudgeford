import random
from backend.utils import attack_shapes as shapes
import backend.models.obstacle as obstacle
from typing import Type


class BoardInitializer:
    def __init__(self, starting_elements, size, id_generator, characters):
        self.starting_elements = starting_elements
        self.size = size
        self.id_generator = id_generator
        self.characters = characters
        self.locations = self._initialize_locations(size, size)
        self.terrain = self._initialize_terrain(size, size)

    def set_up_board(self):

        self.reshape_board()
        self.set_character_starting_locations()
        self.potential_shapes = [
            shapes.line(random.randint(2, 3)),
            shapes.arc(random.randint(2, 3)),
            shapes.cone(random.randint(1, 2)),
            shapes.ring(random.randint(2, 3)),
        ]
        for element in self.starting_elements:
            self.add_starting_effect_to_terrain(element, 1000)
        return self.locations, self.terrain

    # initializes a game map which is a list of ListWithUpdate
    def _initialize_locations(self, width: int = 5, height=5) -> list:
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
            terrain_obj = effect_type(0, next(self.id_generator))
            self.terrain[row][col] = terrain_obj
            return True
        return False

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
            row, col = self.pick_unoccupied_starting_location(is_monster=x.team_monster)
            self.locations[row][col] = x

    def pick_unoccupied_starting_location(
        self, is_monster: bool = True
    ) -> tuple[int, int]:
        # find first non_wall location
        min_x = min(
            x
            for x in range(len(self.locations))
            for y in range(len(self.locations[0]))
            if not self.locations[x][y]
        )
        player_max_x = min_x + 1
        board_edge = self.size - 1
        # space the player and monster starts
        monster_min_x = board_edge - 3

        while True:
            if is_monster:
                rand_location = (
                    random.randint(monster_min_x, board_edge),
                    random.randint(0, board_edge),
                )

            else:
                rand_location = (
                    random.randint(min_x, player_max_x),
                    random.randint(0, board_edge),
                )
            if not self.locations[rand_location[0]][rand_location[1]]:
                return rand_location
