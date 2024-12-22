import pyxel


def draw_tile(x, y, img_bank, u, v, w, h, colkey=0):
    pyxel.blt(x, y, img_bank, u, v, w, h, colkey)


def round_down_to_nearest_multiple(value: int, multiple: int, offset: int) -> int:
    """
    Rounds down the given value to the nearest multiple of `multiple`.
    Can offset grid location to account for border.

    Example:
        round_down_to_nearest_multiple(37, 10) -> 30
        round_down_to_nearest_multiple(25, 7) -> 21
    """
    return max(0, value - offset) // multiple * multiple + offset
