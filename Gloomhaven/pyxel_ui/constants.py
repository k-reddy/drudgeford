import os

DEFAULT_PYXEL_WIDTH = 720
DEFAULT_PYXEL_HEIGHT= 600
MAP_TILE_HEIGHT_PX = 32
MAP_TILE_WIDTH_PX = 32
BITS = 32
FRAME_DURATION_MS = 34
FONT_PATH = os.path.join(
    "pyxel_ui", "assets", "Press_Start_2P", "PressStart2P-Regular.ttf"
)
GRID_COLOR = 0
MAX_LOG_LINES = 10
WALL_THICKNESS = 32
# approx 2 sec of durations with no movement
WINDOW_LENGTH = 60

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

WALL_DIRECTIONS = [
    {
        "coord": (1, 0),
        "wall_tile_name": "new_wall_ns",
        "height": 32,
        "width": 4,
    },
    {
        "coord": (-1, 0),
        "wall_tile_name": "new_wall_ns",
        "height": 32,
        "width": 4,
    },
    {
        "coord": (0, 1),
        "wall_tile_name": "new_wall_ew",
        "height": 4,
        "width": 32,
    },
    {
        "coord": (0, -1),
        "wall_tile_name": "new_wall_ew",
        "height": 4,
        "width": 32,
    },
]