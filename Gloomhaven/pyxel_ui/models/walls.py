from dataclasses import dataclass
import itertools

from .canvas import Canvas
from ..enums import Direction


@dataclass
class Wall:
    """
    Represents a wall on the game board, defined by its starting position, thickness,
    direction, and the canvas it belongs to.

    Attributes:
        u (int): The x-coordinate where the wall starts.
        v (int): The y-coordinate where the wall starts.
        thickness (int): The width of the wall in pixels.
        direction (Direction): The wall's orientation (North, South, East, or West).
        canvas (Canvas): The canvas object defining the game board's layout.
    """

    u: int  # x coord of where to start this particular wall
    v: int  # y coord of where to start this wall
    thickness: int  # in px, what size chunk to take out of sprite sheet
    direction: Direction  # NWSE
    canvas: Canvas

    def pixels(
        self,
    ):  # -> Tuple[Iterable[int], Iterable[int]]: should be, but mypy has issues with this
        """
        Calculates the coordinates of the wall's pixels based on its position, thickness,
        and direction.

        Returns:
            Tuple[Iterable[int], Iterable[int]]: Two iterables representing x and y coordinates.
            - For horizontal walls (NORTH, SOUTH), x-values vary and y-values are constant.
            - For vertical walls (WEST, EAST), y-values vary and x-values are constant.

        Raises:
            ValueError: If the wall's direction is not supported.
        """
        canvas_width = self.canvas.canvas_width_px
        canvas_height = self.canvas.canvas_height_px

        if self.direction is Direction.NORTH or self.direction is Direction.SOUTH:
            x_values = range(self.u, canvas_width, self.thickness)
            y_values = itertools.repeat(self.v, canvas_width // self.thickness)
        elif self.direction is Direction.WEST or self.direction is Direction.EAST:
            x_values = itertools.repeat(self.u, canvas_height // self.thickness)
            y_values = range(self.v, canvas_height, self.thickness)
        else:
            raise ValueError(f"Unsupported direction: {self.direction}")

        return x_values, y_values
