import pyxel

from pyxel_ui.constants import MAP_TILE_HEIGHT_PX, MAP_TILE_WIDTH_PX
from pyxel_ui.utils import round_down_to_nearest_multiple


class UserInputManager:
    def __init__(self, view_manager, server_client):
        self.view_manager = view_manager

        self.accept_keyboard_input = False
        self.accept_mouse_input = False
        self.cursor_shape_offsets = []
        self.default_grid_color = 3
        self.draw_shape_with_cursor = False
        self.grid_color = self.default_grid_color
        self.input = ""
        self.last_mouse_pos = (-1, -1)
        self.mouse_tile_pos = None
        self.mouse_px_pos = None
        self.prompt = ""
        self.server_client = server_client
        self.valid_starting_squares = []

        self.reachable_positions: list[tuple[int, int]] = []
        # The coordinates represented in these attributes have been converted from
        # map tile to pixel with view border offsets applied.
        self.reachable_positions_px: list[tuple[int, int]] = []
        self.reachable_paths_px: dict[tuple[int, int], list[tuple[int, int]]] = {}

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        # Handle cursor redraws and grid
        curr_mouse_x, curr_mouse_y = pyxel.mouse_x, pyxel.mouse_y
        if self.last_mouse_pos != (curr_mouse_x, curr_mouse_y):
            last_mouse_x, last_mouse_y = self.last_mouse_pos
            if view := self.view_manager.get_view_for_coordinate_px(
                last_mouse_x, last_mouse_y
            ):
                view.redraw()

            # Grid concerns
            grid_left_px = round_down_to_nearest_multiple(
                curr_mouse_x, MAP_TILE_WIDTH_PX, self.view_manager.view_border
            )
            grid_top_px = round_down_to_nearest_multiple(
                curr_mouse_y, MAP_TILE_HEIGHT_PX, self.view_manager.view_border
            )
            self.mouse_px_pos = (grid_left_px, grid_top_px)

            # draw the grid only if it's on mapview
            # store valid current map tile pos
            if tile_pos := self.view_manager.get_valid_map_coords_for_cursor_pos(
                grid_left_px, grid_top_px
            ):
                self.view_manager.draw_grid(
                    grid_left_px, grid_top_px, MAP_TILE_WIDTH_PX, MAP_TILE_HEIGHT_PX
                )
                self.mouse_tile_pos = tile_pos
                # and add the rest of the shape if needed
                if (
                    self.draw_shape_with_cursor
                    and tile_pos in self.valid_starting_squares
                ):
                    shape_tiles = [
                        (tile_pos[0] + offset[0], tile_pos[1] + offset[1])
                        for offset in self.cursor_shape_offsets
                    ]
                    self.draw_grid_shape(shape_tiles, color=self.grid_color)
            else:
                self.mouse_tile_pos = None

            self.last_mouse_pos = (curr_mouse_x, curr_mouse_y)

        # Add controls for scrolling action cards
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.view_manager.scroll_carousel_right()
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.view_manager.scroll_carousel_left()

        if self.accept_mouse_input:
            for pos_x, pos_y in self.reachable_positions_px:
                self.view_manager.draw_grid(
                    pos_x, pos_y, MAP_TILE_WIDTH_PX, MAP_TILE_HEIGHT_PX, color=5
                )
            if self.mouse_tile_pos and self.mouse_tile_pos in self.reachable_positions:
                for path_x, path_y in self.reachable_paths_px.get(
                    self.mouse_tile_pos, [self.mouse_px_pos]
                ):
                    self.view_manager.draw_grid(
                        path_x, path_y, MAP_TILE_WIDTH_PX, MAP_TILE_HEIGHT_PX, color=7
                    )
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.mouse_tile_pos:
                tile_pos_x, tile_pos_y = self.mouse_tile_pos
                self.view_manager.reset_personal_log()
                self.accept_mouse_input = False
                self.input = f"{tile_pos_y}, {tile_pos_x}"
                self.return_input_to_server()
                return

        if self.accept_keyboard_input:
            # Handle enter
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.view_manager.reset_personal_log()
                self.accept_keyboard_input = False
                self.return_input_to_server()
                return

            # Handle backspace
            elif pyxel.btnp(pyxel.KEY_BACKSPACE):
                if len(self.input) > 0:
                    self.input = self.input[:-1]

            # Handle space
            elif pyxel.btnp(pyxel.KEY_SPACE):
                self.input += " "

            # Check for A-Z (ASCII 65-90)
            for key in range(pyxel.KEY_A, pyxel.KEY_Z + 1):
                if pyxel.btnp(key):
                    self.input += chr(key).lower()

            # Check for 0-9 (ASCII 48-57)
            for key in range(pyxel.KEY_0, pyxel.KEY_9 + 1):
                if pyxel.btnp(key):
                    self.input += chr(key)

            self.print_personal_log(self.input)

    def print_personal_log(self, user_input):
        self.view_manager.update_personal_log(self.prompt + "\n" + user_input)

    def get_keyboard_input(self, prompt):
        # clear out input
        self.input = ""
        self.accept_keyboard_input = True
        self.prompt = prompt

    def return_input_to_server(self):
        self.server_client.post_user_input(self.input)

    # nit: this method doesn't actually get mouse input, maybe
    # rename to something like enable_mouse_input?
    def get_mouse_input(self, prompt):
        self.input = ""
        self.accept_mouse_input = True
        self.prompt = prompt

    def draw_grid_shape(self, tiles, color):
        for tile in tiles:
            if tile not in self.view_manager.map_view.valid_map_coordinates:
                continue
            x, y = self.view_manager.map_view.convert_grid_to_pixel_pos(
                tile[0], tile[1]
            )
            self.view_manager.draw_grid(
                x, y, MAP_TILE_WIDTH_PX, MAP_TILE_HEIGHT_PX, color
            )

    def set_reachable_values(
        self,
        reachable_positions: list[tuple[int, int]],
        reachable_paths: dict[tuple[int, int], list[tuple[int, int]]],
    ) -> None:
        self.reachable_positions = reachable_positions

        # Convert map tile coords to pixel coords
        self.reachable_positions_px = [
            self.view_manager.get_pixel_pos_for_map_tile(pos_x, pos_y)
            for pos_x, pos_y in reachable_positions
        ]
        self.reachable_paths_px = {
            end_pos: [
                self.view_manager.get_pixel_pos_for_map_tile(pos_x, pos_y)
                for pos_x, pos_y in paths
            ]
            for end_pos, paths in reachable_paths.items()
        }
