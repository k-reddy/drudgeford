import itertools


class Canvas:
    """
    Canvas class to manage the board's dimensions and position.
    Assumes that East/West wall tiles are half the width of North/South

    Attributes:
        board_tile_width (int): Number of tiles along the board's width.
        board_tile_height (int): Number of tiles along the board's height.
        tile_width_px (int): Width of a single tile in pixels.
        tile_height_px (int): Height of a single tile in pixels.
        wall_sprite_thickness_px (int): Thickness of the wall sprite in pixels.
        board_start_pos (tuple): Starting position of the board in pixels.
        board_width_px (int): Total width of the board in pixels.
        board_height_px (int): Total height of the board in pixels.
        canvas_width_px (int): Total width of the canvas in pixels.
        canvas_height_px (int): Total height of the canvas in pixels.
    """

    def __init__(
        self,
        board_tile_width,
        board_tile_height,
        tile_width_px,
        tile_height_px,
        wall_sprite_thickness_px,
    ):
        self.board_tile_width = board_tile_width
        self.board_tile_height = board_tile_height
        self.tile_width_px = tile_width_px
        self.tile_height_px = tile_height_px
        self.wall_sprite_thickness_px = wall_sprite_thickness_px

        # Calculate the board start position and sizes
        self.board_start_pos = (wall_sprite_thickness_px // 2, wall_sprite_thickness_px)
        self.board_width_px = board_tile_width * tile_width_px
        self.board_height_px = board_tile_height * tile_height_px
        self.canvas_width_px = self.board_width_px + wall_sprite_thickness_px
        self.canvas_height_px = self.board_height_px + (2 * wall_sprite_thickness_px)
        self.board_end_pos = (
            self.canvas_width_px - wall_sprite_thickness_px // 2,
            self.canvas_height_px - wall_sprite_thickness_px,
        )

    def grid_pixels(self):
        x_values = range(
            self.board_start_pos[0], self.board_end_pos[0], self.tile_width_px
        )
        y_values = range(
            self.board_start_pos[1], self.board_end_pos[1], self.tile_height_px
        )

        return itertools.product(x_values, y_values)
