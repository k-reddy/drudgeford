import pyxel

from typing import Optional

from pyxel_ui.controllers.view_factory import ViewFactory
from pyxel_ui.constants import (
    BITS,
    FONT_PATH,
)
from pyxel_ui.models.font import PixelFont
from pyxel_ui.views.sprite import SpriteManager
from pyxel_ui.models.view_params import MapViewParams, ViewParams
from pyxel_ui.models import view_section as view


class ViewManager:
    def __init__(
        self, pyxel_width, pyxel_height, floor_color_map=[], wall_color_map=[]
    ):
        self.view_border = 10
        self.sprite_manager = SpriteManager()
        self.font = PixelFont(pyxel, f"../{FONT_PATH}")
        self.canvas_width = pyxel_width
        self.canvas_height = pyxel_height
        self.view_factory = ViewFactory()
        self.views = []
        self.map_view = None
        self.load_carousel_log_screen(view.CharacterPickerView)

    def clear_current_views(self):
        for v in self.views:
            self.turn_off_view_section(v)
        self.views = []
        self.clear_screen()

    def load_game_screen(self, floor_color_map=[], wall_color_map=[]):
        self.clear_current_views()
        initiative_bar_width = 11
        initiative_bar_view_params = ViewParams(
            font=self.font,
            start_pos=[0, 0],
            bounding_coordinate=[BITS * initiative_bar_width, BITS],
        )
        self.initiative_bar_view, bar_borders = (
            self.view_factory.create_view_with_border(
                view.InitiativeBarView, initiative_bar_view_params, [4, 0, 0, 10]
            )
        )
        self.views.extend([self.initiative_bar_view, *bar_borders])

        map_view_params = MapViewParams(
            font=self.font,
            start_pos=[
                0,
                BITS,
            ],
            bounding_coordinate=[
                self.initiative_bar_view.bounding_coordinate[0],
                BITS * 12,
            ],
            floor_color_map=floor_color_map,
            wall_color_map=wall_color_map,
        )
        self.map_view, map_borders = self.view_factory.create_view_with_border(
            view.MapView, map_view_params, [10, 10, 0, 10]
        )
        self.views.extend([self.map_view, *map_borders])

        log_view_params = ViewParams(
            font=self.font,
            start_pos=[
                initiative_bar_width * BITS,
                0,
            ],
            bounding_coordinate=[
                self.canvas_width,
                self.map_view.bounding_coordinate[1],
            ],
        )
        self.log_view, log_borders = self.view_factory.create_view_with_border(
            view.LogView, log_view_params, [4, 0, 0, 0]
        )
        self.views.extend([self.log_view, *log_borders])

        action_card_view_params = ViewParams(
            font=self.font,
            start_pos=[
                0,
                self.map_view.bounding_coordinate[1],
            ],
            bounding_coordinate=[self.canvas_width, BITS * 18],
        )
        self.action_card_view, action_card_borders = (
            self.view_factory.create_view_with_border(
                view.ActionCardView, action_card_view_params, [0, 10, 10, 10]
            )
        )
        self.views.extend([self.action_card_view, *action_card_borders])

        personal_log_params = ViewParams(
            font=self.font,
            start_pos=[
                0,
                self.action_card_view.bounding_coordinate[1],
            ],
            bounding_coordinate=[self.canvas_width, self.canvas_height],
        )
        self.personal_log, personal_log_borders = (
            self.view_factory.create_view_with_border(
                view.LogView, personal_log_params, [60, 10, 0, 10]
            )
        )
        self.views.extend([self.personal_log, *personal_log_borders])
        self.personal_log.font_color = 2
        self.personal_log.display_round_turn = False

    def load_carousel_log_screen(self, carousel_type: view.CarouselView):
        self.clear_current_views()
        carousel_params = ViewParams(
            font=self.font,
            start_pos=(0, 0),
            bounding_coordinate=(
                self.canvas_width,
                BITS * 16,
            ),
        )
        self.carousel_view, carousel_borders = (
            self.view_factory.create_view_with_border(
                carousel_type, carousel_params, [10, 10, 0, 10]
            )
        )
        self.views.extend([self.carousel_view, *carousel_borders])

        personal_log_params = ViewParams(
            font=self.font,
            start_pos=[
                0,
                self.carousel_view.bounding_coordinate[1],
            ],
            bounding_coordinate=[self.canvas_width, self.canvas_height],
        )
        self.personal_log, personal_log_borders = (
            self.view_factory.create_view_with_border(
                view.LogView, personal_log_params, [60, 10, 0, 10]
            )
        )
        self.views.extend([self.personal_log, *personal_log_borders])
        self.personal_log.font_color = 2
        self.personal_log.display_round_turn = False

    def update_log(self, log: list[str]):
        self.log_view.log = log
        if log:
            self.log_view.drawable = True
        self.log_view.draw()

    def update_round_turn(self, round_number: int, acting_character_name: str):
        self.log_view.round_number = round_number
        self.log_view.acting_character_name = acting_character_name
        if round_number > 0 and acting_character_name:
            self.log_view.drawable = True
        else:
            self.log_view.drawable = False
        self.log_view.is_log_changed = True
        self.log_view.draw()

    def update_initiative_bar(
        self,
        sprite_names: list[str],
        healths: list[int],
        max_healths: list[int],
        teams: list[bool],
    ):
        self.initiative_bar_view.sprite_names = sprite_names
        self.initiative_bar_view.healths = healths
        self.initiative_bar_view.max_healths = max_healths
        self.initiative_bar_view.teams = teams
        if sprite_names:
            self.initiative_bar_view.drawable = True
        else:
            self.initiative_bar_view.drawable = False
        self.initiative_bar_view.draw()

    def update_action_card_log(self, action_card_log: list[str]):
        # reset the card page to 0 every time we load new action cards
        self.action_card_view.current_card_page = 0
        self.action_card_view.items = action_card_log
        if action_card_log:
            self.action_card_view.drawable = True
        else:
            self.action_card_view.drawable = False
        self.action_card_view.draw()

    def update_map(
        self,
        valid_floor_coordinates: list[tuple[int, int]],
        floor_color_map=[],
        wall_color_map=[],
    ) -> None:
        if valid_floor_coordinates:
            self.map_view.drawable = True
        else:
            self.map_view.drawable = False

        if floor_color_map:
            self.map_view.floor_color_map = floor_color_map
        if wall_color_map:
            self.map_view.wall_color_map = wall_color_map
        self.map_view.valid_map_coordinates = valid_floor_coordinates
        self.map_view.draw()
        self.map_view.draw_sprites()

    def update_sprites(self, entities: dict) -> None:
        """draws entity sprites with a notion of priority"""
        self.map_view.entities = entities
        self.map_view.draw()

    def remove_entity(self, entity_id: int) -> None:
        try:
            del self.map_view.entities[entity_id]
        except Exception as e:
            print(f"attempting to delete non-existent entity: {str(e)}")
            raise
        self.map_view.draw()

    def convert_grid_to_pixel_pos(self, tile_x: int, tile_y: int) -> tuple[int, int]:
        """Converts grid-based tile coordinates to pixel coordinates on the map."""
        return self.map_view.convert_grid_to_pixel_pos(tile_x, tile_y)

    def get_view_for_coordinate_px(
        self,
        px_x: int,
        px_y: int,
    ) -> Optional[view.ViewSection]:
        view = next(
            (
                curr_view
                for curr_view in self.views
                if curr_view.start_pos[0] <= px_x < curr_view.end_pos[0]
                and curr_view.start_pos[1] <= px_y < curr_view.end_pos[1]
                and curr_view.active
            ),
            None,
        )
        # print(view)
        # if view:
        #     print(view.active)
        return view

    def draw_grid(self, px_x: int, px_y: int, px_width: int, px_height: int) -> None:
        view.draw_grid(px_x, px_y, px_width, px_height)

    def draw_whole_game(self):
        for v in self.views:
            v.draw()

    def get_valid_map_coords_for_cursor_pos(
        self, px_x: int, px_y: int
    ) -> Optional[tuple[int, int]]:
        if not self.map_view:
            return None
        # get rid of offsets
        px_x -= self.map_view.start_pos[0]
        px_y -= self.map_view.start_pos[1]
        # figure out the tile number (not px)
        x_num = px_x / self.map_view.tile_width_px
        y_num = px_y / self.map_view.tile_height_px
        if (x_num, y_num) in self.map_view.valid_map_coordinates:
            return (x_num, y_num)
        return None

    def _get_active_carousel(self):
        active_carousel = [
            v for v in self.views if isinstance(v, view.CarouselView) and v.active
        ]
        if not active_carousel:
            return None
        elif len(active_carousel) > 1:
            raise ValueError(
                f"{len(active_carousel)} active carousels. Require 0 or 1."
            )
        else:
            return active_carousel[0]

    def scroll_carousel_right(self):
        active_carousel = self._get_active_carousel()
        if not active_carousel:
            return
        if (
            active_carousel.current_card_page + 1
        ) * active_carousel.cards_per_page < len(active_carousel.items):
            active_carousel.current_card_page += 1
            active_carousel.draw()

    def scroll_carousel_left(self):
        active_carousel = self._get_active_carousel()
        if not active_carousel:
            return
        # Go to previous page if we're not at the start
        if active_carousel.current_card_page > 0:
            active_carousel.current_card_page -= 1
            active_carousel.draw()

    def update_personal_log(self, output: str, clear=True):
        if clear:
            self.personal_log.log = [output]
            self.personal_log.is_log_changed = True
        else:
            self.personal_log.log += [output]
        self.personal_log.drawable = True
        self.personal_log.draw()

    def reset_personal_log(self):
        self.personal_log.drawable = False
        self.personal_log.log = []
        self.personal_log.draw()

    def reset_self(self):
        self.update_initiative_bar([], [], [], [])
        self.update_map([], [], [])
        self.update_action_card_log([])
        self.update_log([])
        self.update_personal_log([], clear=True)
        self.update_sprites({})
        self.update_round_turn(0, "")
        self.draw_whole_game()

    def turn_on_view_section(self, view_section: view.ViewSection) -> None:
        """
        Toggles the provided view_section on and redraws the whole screen
        (in case the view section doesn't perfectly overlap with the old one)
        """
        view_section.drawable = True
        view_section.active = True
        self.draw_whole_game()

    def turn_off_view_section(self, view_section: view.ViewSection) -> None:
        """
        toggles a view_section off and redraws it (to clear the bounds)
        we leave it in our

        """
        view_section.drawable = False
        view_section.active = False
        view_section.draw()

    def get_map_view(self):
        return self.map_view

    def get_carousel_view(self):
        return self.carousel_view

    def update_carousel(self, items):
        self.carousel_view.items = items
        self.carousel_view.drawable = True
        self.carousel_view.draw()

    def clear_screen(self):
        pyxel.rect(
            0,
            0,
            self.canvas_width,
            self.canvas_height,
            0,
        )
