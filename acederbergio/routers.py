# NOTE: DO NOT IMPORT FROM THE CLIENT HERE! IF YOU WANT TO IMPORT FROM THE
#       CLIENT MAKE A SEPARATE PACKAGE TO AVOID CIRCULAR IMPORT ERRORS!
# =========================================================================== #
from os import path
from typing import Annotated, TypeAlias

import fastapi
from acederbergio.controllers import Color
from app.views.base import BaseView
from fastapi.templating import Jinja2Templates

PRETTY_PAIRS = {
    ("cd0ddc", "eb7616"),
}


def colors(
    start: str = "#e9b863",
    stop: str = "#9c79ec",
    steps: int = 24,
    random: bool = False,
):

    if random:
        color_start, color_stop = Color.random(), Color.random()
    else:
        color_start = Color.fromHex(start)
        color_stop = Color.fromHex(stop)

    colors = color_start.interpolate(color_stop, steps=steps)
    return list(colors)


DependsColors: TypeAlias = Annotated[
    list[Color],
    fastapi.Depends(colors, use_cache=True),
]


class ColorView(BaseView):
    view_templates = Jinja2Templates(
        path.join(
            path.realpath(path.dirname(__file__)),
            "templates",
        )
    )
    view_routes = dict(
        get_interpolate_json="/interpolate/json",
        get_interpolate="/interpolate",
    )

    @classmethod
    def get_interpolate_json(
        cls,
        colors: DependsColors,
        as_hex: bool = True,
    ):
        if as_hex:
            return list(item.hex for item in colors)
        else:
            return list(item.color_schema().model_dump(mode="json") for item in colors)

    @classmethod
    def get_interpolate(
        cls,
        request: fastapi.Request,
        colors: DependsColors,
        start: str = "#e9b863",
        stop: str = "#9c79ec",
        steps: int = 24,
    ):
        return cls.view_templates.TemplateResponse(
            request,
            "colors.j2",
            context=dict(
                colors=colors,
                steps=steps,
                start=start,
                stop=stop,
            ),
        )
