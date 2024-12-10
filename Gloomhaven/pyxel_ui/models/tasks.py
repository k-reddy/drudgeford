from dataclasses import dataclass
from collections import deque
from typing import Optional
import abc
from pyxel_ui.models.entity import Entity
from pyxel_ui.enums import AnimationFrame
from pyxel_ui.constants import FRAME_DURATION_MS

# from pyxel_ui.models.view_section import ActionCardView, CharacterPickerView


@dataclass
class Task(abc.ABC):
    @abc.abstractmethod
    def perform(self, view_manager, user_input_manager):
        pass


@dataclass
class AddEntitiesTask(Task):
    """
    A task that tells pyxel to load an entity onto the game map.

    entities is a list of dicts with:
        - entity_id - unique id for the entity
        - position - where on the map to put the entity
        - sprite_name - name of the sprite to display for the entity
        - priority - kind of a "z" index, with higher numbers showing up on top
            when the map draws
    """

    entities: list

    def perform(self, view_manager, user_input_manager):
        entities = view_manager.map_view.entities
        for entity in self.entities:
            row_px, col_px = view_manager.convert_grid_to_pixel_pos(
                entity["position"][0],
                entity["position"][1],
            )

            entities[entity["id"]] = Entity(
                id=entity["id"],
                name=entity["name"],
                x=row_px,
                y=col_px,
                z=10,
                priority=entity["priority"],
                animation_frame=AnimationFrame.SOUTH,
                alive=True,
            )
        view_manager.update_sprites(entities)


@dataclass
class RemoveEntityTask(Task):
    """
    A task that tells pyxel to remove an entity from the game map.
    Pyxel will have no record of that entity going forward
    """

    entity_id: int

    def perform(self, view_manager, user_input_manager):
        view_manager.remove_entity(self.entity_id)


@dataclass
class LoadCharactersTask(Task):
    """
    A task that tells pyxel to update the characters/healths/ordering in the
    initiative bar
    """

    healths: list[int]
    max_healths: list[int]
    sprite_names: list[str]
    teams: list[bool]

    def perform(self, view_manager, user_input_manager):
        view_manager.update_initiative_bar(
            self.sprite_names, self.healths, self.max_healths, self.teams
        )


@dataclass
class LoadLogTask(Task):
    """
    task that updates the pyxel log
    """

    log: list[str]

    def perform(self, view_manager, user_input_manager):
        view_manager.update_log(self.log)


@dataclass
class LoadActionCardsTask(Task):
    """
    task that updates the action cards area
    """

    action_card_log: list[str]

    def perform(self, view_manager, user_input_manager):
        view_manager.update_action_card_log(self.action_card_log)


@dataclass
class LoadRoundTurnInfoTask(Task):
    """
    task that updates the round number and who's turn it is
    """

    round_number: int
    acting_character_name: str

    def perform(self, view_manager, user_input_manager):
        view_manager.update_round_turn(self.round_number, self.acting_character_name)


# board init tasks are the only task that shouldn't be performed
# because they're only used to set up the board once
@dataclass
class BoardInitTask:
    """
    Initializes the board
    """

    map_height: int
    map_width: int
    valid_map_coordinates: list[tuple[int, int]]
    floor_color_map: Optional[list[tuple[int, int]]] = None
    wall_color_map: Optional[list[tuple[int, int]]] = None

    def perform(self, view_manager, user_input_manager):
        view_manager.load_game_screen(self.floor_color_map, self.wall_color_map)
        view_manager.update_map(
            self.valid_map_coordinates, self.floor_color_map, self.wall_color_map
        )


@dataclass
class ActionTask(Task):
    """
    Represents an action performed by a entity in the game, including movement
    and animation details.

    Attributes:
        entity id (int)): The id of the entity performing the action.
        from_grid_pos (tuple): The starting position on the grid (x, y).
        to_grid_pos (tuple): The target position on the grid (x, y).
        duration_ms (int): The duration of the action in milliseconds (default is 1000 ms).
        action_steps (Optional[deque[tuple[int, int]]]): A sequence of pixel positions
            representing the path of the action (optional).
    """

    entity_id: int
    from_grid_pos: tuple
    to_grid_pos: tuple
    duration_ms: int = 1000
    action_steps: Optional[deque[tuple[int, int]]] = None
    is_jump: bool = False

    def perform(self, view_manager, user_input_manager):
        # if you don't have action steps, create them
        if not self.action_steps:
            self.action_steps = self.get_px_move_steps_between_tiles(
                view_manager, self.is_jump
            )

        px_pos_x, px_pos_y, scale = self.action_steps.popleft()
        # !!! yuck! fix this later
        view_manager.map_view.entities[self.entity_id].update_position(
            px_pos_x, px_pos_y
        )
        view_manager.map_view.entities[self.entity_id].update_scale(scale)
        view_manager.map_view.draw()

    def get_px_move_steps_between_tiles(
        self,
        view_manager,
        is_jump,
    ) -> deque[tuple[int, int, int]]:
        """
        Calculates the pixel-based steps for movement between two tiles.

        Movement is broken into discrete steps, where the number of steps determines
        the speed of the animation. The steps are stored as tuples of (x, y) pixel coordinates.

        The third value in the tuple represents the size of the sprite. Default is 1.
        """
        assert (
            self.duration_ms > FRAME_DURATION_MS
        ), "ActionTask smaller than frame rate"

        start_px_x, start_px_y = view_manager.convert_grid_to_pixel_pos(
            *self.from_grid_pos
        )
        end_px_x, end_px_y = view_manager.convert_grid_to_pixel_pos(*self.to_grid_pos)

        step_count = self.duration_ms // FRAME_DURATION_MS
        diff_px_x = end_px_x - start_px_x
        diff_px_y = end_px_y - start_px_y

        return deque(
            (
                int(start_px_x + i / step_count * (diff_px_x)),
                int(start_px_y + i / step_count * (diff_px_y)),
                (
                    parabolic_scaling(i, step_count)
                    if is_jump
                    else parabolic_scaling(i, step_count, peak_scale=1.2)
                ),
            )
            for i in range(step_count + 1)
        )


def parabolic_scaling(
    i: int, step_count: int, base_scale: int = 1, peak_scale: int = 2
):
    """Adjusts the scale parabolically over step_count frames.

    Args:
        i: Current step
        step_count: Total steps
        base_scale: Starting scale
        peak_scale: Max scale.
    """
    return (
        -4 * (peak_scale - base_scale) / step_count**2 * i**2
        + 4 * (peak_scale - base_scale) / step_count * i
        + base_scale
    )


@dataclass
class InputTask(Task):
    """
    task that asks user for input in pyxel
    """

    prompt: str
    reachable_positions: Optional[list[tuple[int, int]]] = None
    reachable_paths: Optional[dict[tuple[int, int], list[tuple[int, int]]]] = None

    def perform(self, view_manager, user_input_manager):
        user_input_manager.get_keyboard_input(self.prompt)

    # this was just for terminal input
    # def clear_input(self):
    #     # windows
    #     try:
    #         import msvcrt
    #         while msvcrt.kbhit():
    #             msvcrt.getch()
    #     # Unix/Linux
    #     except ImportError:
    #         import sys, termios
    #         termios.tcflush(sys.stdin, termios.TCIOFLUSH)


@dataclass
class MouseInputTask(Task):
    """
    task that asks for mouse input in pyxel
    """

    prompt: str
    reachable_positions: Optional[list[tuple[int, int]]] = None
    reachable_paths: Optional[dict[tuple[int, int], list[tuple[int, int]]]] = None

    def perform(self, view_manager, user_input_manager):
        user_input_manager.get_mouse_input(self.prompt)
        # reachable_paths is an empty dict for jumps
        if self.reachable_positions and self.reachable_paths is not None:
            user_input_manager.set_reachable_values(
                self.reachable_positions, self.reachable_paths
            )


# @dataclass
# class TerminalInputTask(Task):
#     """
#     task that asks user for input in the terminal
#     """
#     prompt: str
#     valid_inputs: Optional[list] = None

#     def perform(self, view_manager, user_input_manager):
#         self.clear_input()
#         user_input = input(self.prompt)

#         # if there's no validation, return any input given
#         if self.valid_inputs is None:
#             return user_input

#         while user_input not in self.valid_inputs:
#             user_input = input("Invalid key pressed. Try again.")

#         # send this input to the server
#         return user_input

#     def clear_input(self):
#         # windows
#         try:
#             import msvcrt
#             while msvcrt.kbhit():
#                 msvcrt.getch()
#         # Unix/Linux
#         except ImportError:
#             import sys, termios
#             termios.tcflush(sys.stdin, termios.TCIOFLUSH)


@dataclass
class PrintTerminalMessage(Task):
    """
    task that prints message in user terminal
    """

    message: str

    def perform(self, view_manager, user_input_manager):
        print(self.message)


@dataclass
class AddToPersonalLog(Task):
    """
    task that updates the personal log
    """

    string_to_add: str
    clear: bool

    def perform(self, view_manager, user_input_manager):
        view_manager.update_personal_log(self.string_to_add, self.clear)


@dataclass
class SaveCampaign(Task):
    """
    task that asks the user if they'd like to save and saves if so
    """

    # ideally this would be a CampaignState but it's creating circular dependencies
    campaign_state: any

    def perform(self, view_manager, user_input_manager):
        import os
        from backend.utils.config import SAVE_FILE_DIR
        import json

        filename = self.get_unused_filename()
        os.makedirs(SAVE_FILE_DIR, exist_ok=True)
        with open(SAVE_FILE_DIR + filename, "wb") as f:
            json.dump(self.campaign_state, f)
        return filename

    def get_unused_filename(self):
        from backend.utils.utilities import get_campaign_filenames

        file_names = get_campaign_filenames()
        i = 0
        filename = f"campaign_{i}.json"
        while True:
            if filename in file_names:
                i += 1
                filename = f"campaign_{i}.json"
            else:
                break
        return filename


@dataclass
class LoadCampaign(Task):
    """
    loads all campaign data and sends it to the backend
    """

    def perform(self, view_manager, user_input_manager):
        import json
        import os
        from backend.utils.utilities import get_campaign_filenames
        from backend.utils.config import SAVE_FILE_DIR

        filenames = get_campaign_filenames()
        file_dict = {}
        for i, filename in enumerate(filenames):
            file_path = SAVE_FILE_DIR + filename
            # validate that the file size is reasonable
            file_size = os.path.getsize(file_path)
            if file_size > 1_000_000:  # 1MB in bytes
                print(f"Save file {filename} is too large ({file_size} bytes)")
                continue
            with open(file_path, "rb") as f:
                campaign_state = json.load(f)
                file_dict[f"{i}: {filename}"] = campaign_state.__dict__
        return file_dict


@dataclass
class ResetViewManager(Task):
    def perform(self, view_manager, user_input_manager):
        view_manager.reset_self()


@dataclass
class ShowCharacterPickerTask(Task):
    """
    A task that tells pyxel to show the character picker so player can choose their character class
    """

    names: list[str]
    sprite_names: list[str]
    backstories: list[str]

    def perform(self, view_manager, user_input_manager):
        view_manager.load_carousel_log_screen("CharacterPickerView")
        view_manager.update_carousel(
            items=[
                {"name": name, "sprite_name": sprite_name, "backstory": backstory}
                for name, sprite_name, backstory in zip(
                    self.names, self.sprite_names, self.backstories
                )
            ]
        )


@dataclass
class MakeCarouselUndrawable(Task):
    # makes the carousel undrawable, which means a black box will cover it
    def perform(self, view_manager, user_input_manager):
        active_carousel = view_manager.get_carousel_view()
        active_carousel.drawable = False
        active_carousel.draw()


@dataclass
class LoadPlotScreen(Task):
    plot: str

    def perform(self, view_manager, user_input_manager):
        view_manager.load_carousel_log_screen("ActionCardView")
        view_manager.carousel_view.font_color = 5
        view_manager.carousel_view.cards_per_page = 1
        view_manager.update_carousel(items=[self.plot])


@dataclass
class HighlightMapTiles(Task):
    color: int
    tiles: list[tuple[int, int]]

    def perform(self, view_manager, user_input_manager):
        # user_input_manager.draw_grid_shape(self.tiles, self.color)
        user_input_manager.set_reachable_values(
            reachable_positions=self.tiles, reachable_paths={}
        )


@dataclass
class RedrawMap(Task):
    def perform(self, view_manager, user_input_manager):
        view_manager.map_view.draw()


@dataclass
class DrawCursorGridShape(Task):
    tile_shape_offsets: list[tuple[int, int]]
    grid_color: int
    valid_starting_squares: list[tuple[int, int]]

    def perform(self, view_manager, user_input_manager):
        user_input_manager.draw_shape_with_cursor = True
        user_input_manager.cursor_shape_offsets = self.tile_shape_offsets
        user_input_manager.grid_color = self.grid_color
        user_input_manager.valid_starting_squares = self.valid_starting_squares


@dataclass
class TurnOffCursorGridShape(Task):
    def perform(self, view_manager, user_input_manager):
        user_input_manager.draw_shape_with_cursor = False
        user_input_manager.cursor_shape_offsets = []
        user_input_manager.grid_color = user_input_manager.default_grid_color
        user_input_manager.valid_starting_squares = []
