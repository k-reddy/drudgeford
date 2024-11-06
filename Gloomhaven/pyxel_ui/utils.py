from .enums import Direction
from .models.canvas import Canvas
from .models.walls import Wall
import pyxel

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
        "u": 0,
        "v": 160,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_cracked_1": {
        "img_bank": 2,
        "u": 0,
        "v": 128,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_cracked_2": {
        "img_bank": 2,
        "u": 32,
        "v": 128,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_cracked_3": {
        "img_bank": 2,
        "u": 0,
        "v": 160,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_cracked_4": {
        "img_bank": 2,
        "u": 32,
        "v": 160,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_cracked_5": {
        "img_bank": 2,
        "u": 0,
        "v": 192,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_cracked_6": {
        "img_bank": 2,
        "u": 32,
        "v": 192,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_cracked_7": {
        "img_bank": 2,
        "u": 64,
        "v": 192,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_cracked_8": {
        "img_bank": 2,
        "u": 64,
        "v": 160,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_cracked_9": {
        "img_bank": 2,
        "u": 64,
        "v": 128,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_cracked_10": {
        "img_bank": 2,
        "u": 64,
        "v": 224,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_cracked_11": {
        "img_bank": 2,
        "u": 32,
        "v": 224,
        "w": 32,
        "h": 32,
    },
    "dungeon_floor_cracked_12": {
        "img_bank": 2,
        "u": 0,
        "v": 224,
        "w": 32,
        "h": 32,
    },
    "new_wall_ew": {
        "img_bank": 2,
        "u": 64,
        "v": 92,
        "w": 32,
        "h": 4,
    },
    "new_wall_ns": {
        "img_bank": 2,
        "u": 64,
        "v": 96,
        "w": 4,
        "h": 32,
    },
}


def draw_tile(x, y, img_bank, u, v, w, h, colkey=0):
    pyxel.blt(x, y, img_bank, u, v, w, h, colkey)


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
