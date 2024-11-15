from dataclasses import dataclass, field

from .font import PixelFont


@dataclass
class ViewParams:
    font: PixelFont
    start_pos: tuple[int, int]
    bounding_coordinate: tuple[int, int]

    def to_kwargs(self):
        return {
            "font": self.font,
            "start_pos": self.start_pos,
            "bounding_coordinate": self.bounding_coordinate,
        }


@dataclass
class MapViewParams(ViewParams):
    floor_color_map: list[tuple[int, int]] = field(default_factory=list)
    wall_color_map: list[tuple[int, int]] = field(default_factory=list)

    def to_kwargs(self):
        return {
            "font": self.font,
            "start_pos": self.start_pos,
            "bounding_coordinate": self.bounding_coordinate,
            "floor_color_map": self.floor_color_map,
            "wall_color_map": self.wall_color_map,
        }
