from typing import Optional

from pyxel_ui.models.view_section import BorderView, ViewSection
from pyxel_ui.models.view_params import ViewParams


class ViewFactory:
    def create_view_with_border(
        self,
        view_cls: ViewSection,
        view_params: ViewParams,
        borders: list[int] = [0, 0, 0, 0],
    ) -> tuple[ViewSection, Optional[ViewSection]]:
        """Create view and any related border views
        Borders function like CSS box padding where the final size of all
        views and their borders will match the size specified in view_params.

        The view content will shrink to accommodate the borders. Bottom and top borders do
        not extend beyond the sides of the content while left and right borders will extend
        beyond the top/bottom to match borders. No voids at corners!

        Args:
            borders: top, right, bottom, left thickness in px
        """
        assert (
            isinstance(borders, list)
            and len(borders) == 4
            and all(isinstance(x, int) for x in borders)
        ), "Borders must be a list of exactly four integers"

        top_px, right_px, bottom_px, left_px = borders
        border_views = []
        if top_px:
            border_views.append(
                BorderView(
                    view_params.font,
                    (
                        view_params.start_pos[0] + left_px,
                        view_params.start_pos[1],
                    ),
                    (
                        view_params.bounding_coordinate[0] - right_px,
                        view_params.start_pos[1] + top_px,
                    ),
                )
            )
        if bottom_px:
            border_views.append(
                BorderView(
                    view_params.font,
                    (
                        view_params.start_pos[0] + left_px,
                        view_params.bounding_coordinate[1] - bottom_px,
                    ),
                    (
                        view_params.bounding_coordinate[0] - right_px,
                        view_params.bounding_coordinate[1],
                    ),
                )
            )
        if left_px:
            border_views.append(
                BorderView(
                    view_params.font,
                    (
                        view_params.start_pos[0],
                        view_params.start_pos[1],
                    ),
                    (
                        view_params.start_pos[0] + left_px,
                        view_params.bounding_coordinate[1],
                    ),
                )
            )
        if right_px:
            border_views.append(
                BorderView(
                    view_params.font,
                    (
                        view_params.bounding_coordinate[0] - right_px,
                        view_params.start_pos[1],
                    ),
                    (
                        view_params.bounding_coordinate[0],
                        view_params.bounding_coordinate[1],
                    ),
                )
            )

        adjusted_params = view_params.to_kwargs()
        adjusted_params.update(
            {
                "start_pos": (
                    view_params.start_pos[0] + left_px,
                    view_params.start_pos[1] + top_px,
                ),
                "bounding_coordinate": (
                    view_params.bounding_coordinate[0] - right_px,
                    view_params.bounding_coordinate[1] - bottom_px,
                ),
            }
        )
        new_view = view_cls(**adjusted_params)

        return new_view, border_views
