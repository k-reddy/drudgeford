from .enums import Direction
import pyxel


def draw_tile(x, y, img_bank, u, v, w, h, colkey=0):
    pyxel.blt(x, y, img_bank, u, v, w, h, colkey)


def round_to_multiple(value, multiple):
    return value // multiple * multiple
