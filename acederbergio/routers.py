# NOTE: DO NOT IMPORT FROM THE CLIENT HERE! IF YOU WANT TO IMPORT FROM THE
#       CLIENT MAKE A SEPARATE PACKAGE TO AVOID CIRCULAR IMPORT ERRORS!
# =========================================================================== #
import random
from os import path
from typing import Annotated, Any, TypeAlias

import fastapi
from acederbergio import config
from acederbergio.controllers import Color, Gradient
from acederbergio.schemas import FieldRandom, GradientRequest, GradientResponse
from app.views.base import BaseView
from fastapi.templating import Jinja2Templates

PRETTY_PAIRS = {
    ("cd0ddc", "eb7616"),
    ("e9b864", "9c79ec"),
    ("5c925b", "f8ba02"),
    ("e6d99f", "f42bba"),
    ("2b2115", "15a7ff"),
    ("79a981", "118487"),
    ("d10b3e", "efd5c2"),
    ("f89f17", "f89f17"),
}


def random_color(v: Any | None) -> Any:
    if v is not None:
        return v
    values = (random.randint(0, 255) for _ in range(3))
    return "#" + "".join(f"{hex(item)[2:]:0>2}" for item in values)


def gradient_request(
    stop: str | None = None,
    start: str | None = None,
    steps: int = 16,
) -> GradientRequest:
    """To get a random gradient, specify neither ``stop`` nor ``start``."""

    return GradientRequest(
        start=random_color(start),
        stop=random_color(stop),
        steps=steps,
    )


DependsGradientRequest: TypeAlias = Annotated[
    GradientRequest,
    fastapi.Depends(gradient_request, use_cache=True),
]


def gradient(gradient_request: DependsGradientRequest) -> Gradient:

    return Gradient(
        start=Color.fromHex(gradient_request.start),
        stop=Color.fromHex(gradient_request.stop),
        steps=gradient_request.steps,
    )


DependsGradient = Annotated[Gradient, fastapi.Depends(gradient)]


class ColorView(BaseView):
    view_templates = Jinja2Templates(config.PATH_TEMPLATES)
    view_routes = dict(
        get_gradient_json="/gradient/json",
        get_gradient="/gradient",
    )

    @classmethod
    def get_gradient_json(
        cls,
        grandient: DependsGradient,
        just_hex: bool = True,
    ):
        if just_hex:
            return list(item.hex for item in grandient)
        else:
            items = list(item.color_schema() for item in grandient)
            return GradientResponse(
                items=items,
                start=grandient.start.color_schema(),
                stop=grandient.stop.color_schema(),
                steps=grandient.steps,
            )

    @classmethod
    def get_gradient(
        cls,
        request: fastapi.Request,
        gradient: DependsGradient,
    ):
        return cls.view_templates.TemplateResponse(
            request,
            "gradient.j2",
            context=dict(gradient=gradient),
        )

    # NOTE: Want to put pallete in browser, offer rotations, gradients, etc.
    # @classmethod
    # def get_builder(
    #     cls,
    #     request: fastapi.Request,
    # ):
    #     """Get the pallete builder app."""
    #     ...
