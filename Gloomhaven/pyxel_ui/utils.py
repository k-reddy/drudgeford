from .enums import Direction
from .models.canvas import Canvas
from .models.walls import Wall
import pyxel


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
