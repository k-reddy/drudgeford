import pyxel

from pyxel_ui.constants import MAP_TILE_HEIGHT_PX, MAP_TILE_WIDTH_PX
from pyxel_ui.utils import round_down_to_nearest_multiple


class UserInputManager:
    def __init__(self, view_manager, server_client):
        self.view_manager = view_manager
        self.accept_keyboard_input = False
        self.accept_mouse_input = False
        self.input = ""
        self.prompt = ""
        self.server_client = server_client
        self.mouse_tile_pos = None
        self.last_mouse_pos = (-1, -1)

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
            # draw the grid only if it's on mapview
            # store valid current map tile pos
            if tile_pos := self.view_manager.get_valid_map_coords_for_cursor_pos(
                grid_left_px, grid_top_px
            ):
                self.view_manager.draw_grid(
                    grid_left_px, grid_top_px, MAP_TILE_WIDTH_PX, MAP_TILE_HEIGHT_PX
                )
                self.mouse_tile_pos = tile_pos
            else:
                self.mouse_tile_pos = None

            self.last_mouse_pos = (curr_mouse_x, curr_mouse_y)

        # Add controls for scrolling action cards
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.view_manager.scroll_carousel_right()
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.view_manager.scroll_carousel_left()

        if self.accept_mouse_input:
            self.print_personal_log(self.input)
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.mouse_tile_pos:
                tile_pos_x, tile_pos_y = self.mouse_tile_pos
                # BUG: location seems to be relative to character starting position so
                # the target location will always be off by some amount, e.g. always 2 over.
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
