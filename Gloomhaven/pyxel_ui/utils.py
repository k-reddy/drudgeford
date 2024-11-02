from .enums import Direction
from .models.canvas import Canvas
from .models.walls import Wall

BACKGROUND_TILES = {
    "dungeon_floor": {
        "img_bank": 1,
        "u": 113,
        "v": 108,
        "w": 32,
        "h": 32,
    },
    "dungeon_wall_north": {
        "img_bank": 1,
        "u": 98,
        "v": 75,
        "w": 32,
        "h": 32,
    },
    "dungeon_wall_south": {
        "img_bank": 1,
        "u": 96,
        "v": 156,
        "w": 32,
        "h": 32,
    },
    "dungeon_wall_west": {
        "img_bank": 1,
        "u": 81,
        "v": 108,
        "w": 32,
        "h": 32,
    },
    "dungeon_wall_east": {
        "img_bank": 1,
        "u": 144,
        "v": 108,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_blue": {
        "img_bank": 1,
        "u": 0,
        "v": 128,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_gray": {
        "img_bank": 1,
        "u": 32,
        "v": 128,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_tan": {
        "img_bank": 1,
        "u":0,
        "v": 160,
        "w": 32,
        "h": 32,
    },
}


class AutoIncrementDict:
    def __init__(self):
        self.data = {}
        self.counter = 0

    def add(self, value):
        self.data[self.counter] = value
        self.counter += 1

    def get_data(self):
        return self.data


def generate_wall_bank(canvas: Canvas) -> dict[str, Wall]:
    return {
        "north": Wall(
            0,
            0,
            canvas.wall_sprite_thickness_px,
            Direction.NORTH,
            canvas.canvas_width_px,
            canvas.canvas_height_px,
        ),
        "south": Wall(
            0,
            canvas.canvas_height_px - canvas.wall_sprite_thickness_px,
            canvas.wall_sprite_thickness_px,
            Direction.SOUTH,
            canvas.canvas_width_px,
            canvas.canvas_height_px,
        ),
        "west": Wall(
            0,
            0,
            32,
            Direction.WEST,
            canvas.canvas_width_px,
            canvas.canvas_height_px,
        ),
        "east": Wall(
            canvas.canvas_width_px - 32,
            0,
            32,
            Direction.EAST,
            canvas.canvas_width_px,
            canvas.canvas_height_px,
        ),
    }
