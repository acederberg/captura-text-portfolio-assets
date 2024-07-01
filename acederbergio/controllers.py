# NOTE: DO NOT IMPORT FROM THE CLIENT HERE! IF YOU WANT TO IMPORT FROM THE
#       CLIENT MAKE A SEPARATE PACKAGE TO AVOID CIRCULAR IMPORT ERRORS!
# =========================================================================== #
import functools
import json
import math
import random
from os import path
from typing import (
    Annotated,
    Any,
    ClassVar,
    Dict,
    Generator,
    List,
    Optional,
    Self,
    Tuple,
    TypeAlias,
)

import fastapi

# import numpy as np
# import numpy.typing as nptypes
import typer
import uvicorn
from acederbergio.schemas import ColorSchema
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, TypeAdapter
from rich.console import Console
from typing_extensions import Doc


# NOTE: See https://pypi.org/project/colour/.
class Color:

    # ----------------------------------------------------------------------- #
    # Constructors etc.

    color_keys: ClassVar[Tuple[str, str, str]] = ("r", "g", "b")

    r: int
    g: int
    b: int

    diff: bool

    @classmethod
    def random(cls) -> Self:
        values = (random.randint(0, 255) for _ in range(3))
        return cls(*values)

    @classmethod
    def fromHex(
        cls,
        hexcode: str,
        *,
        diff: bool = False,
    ) -> Self:
        if hexcode.startswith("#"):
            hexcode = hexcode[1:]
        if len(hexcode) != 6:
            raise ValueError("Must be 6 long.")

        hex_chunks = tuple(hexcode[i : i + 2] for i in range(0, 6, 2))
        hex_chunks = (int(item, 16) for item in hex_chunks)

        return cls(*hex_chunks, diff=diff)

    def __init__(self, r: int, g: int, b: int, *, diff: bool = False):

        bad = {
            key: value
            for key, value in zip(self.color_keys, (r, g, b))
            if abs(value) >= 256
        }
        if len(bad):
            raise ValueError(f"The following values cannot be used: `{bad}`.")

        if not diff and len(bad := tuple(v for v in bad.values() if v < 0)) > 0:
            raise ValueError(f"Illegal negative values in {bad}`.")

        self.r = r
        self.g = g
        self.b = b
        self.diff = diff

    @property
    def hex(self) -> str | None:
        "Self as a hex string."
        if self.diff:
            return None

        return "#" + "".join(f"{hex(item)[2:]:0>2}" for item in self)  # type: ignore

    @property
    def rgb(self) -> Dict[str, int]:
        return dict(r=self.r, g=self.g, b=self.b)

    # ----------------------------------------------------------------------- #
    # MATH

    def __iter__(self):
        yield from (self.r, self.g, self.b)

    def __add__(self, other: Self) -> Self:
        return self.__class__(*((s + t) for s, t in zip(self, other)), diff=False)

    def __sub__(self, other: Self) -> Self:
        return self.__class__(
            r=other.r - self.r,
            g=other.g - self.g,
            b=other.b - self.b,
            diff=True,
        )

    def scale(self, scalar: float) -> Self:
        return self.__class__(
            round(scalar * self.r),
            round(scalar * self.g),
            round(scalar * self.b),
        )

    # ----------------------------------------------------------------------- #
    # Methods

    def __repr__(self) -> str:
        return f"Color({self.r}, {self.g}, {self.b}, diff={self.diff})"

    def color_schema(self) -> ColorSchema:
        return ColorSchema(rgb=self.rgb, hex=self.hex)  # type: ignore


#
# def bound(v):
#     if v < 0:
#         return 0
#     if v > 255:
#         return 255
#     return int(v + 0.5)
#
#
# # NOTE: Idk what I'm going to do with this yet, but it does appear to work.
# # https://en.wikipedia.org/wiki/HSL_and_HSV
# # https://stackoverflow.com/questions/8507885/shift-hue-of-an-rgb-color
# class RotationTransformation:
#
#     const_sqrt: ClassVar[float] = 1.0 / 3.0
#     const: ClassVar[float] = math.sqrt(const_sqrt)
#
#     phi: Annotated[float, Doc("Degrees in radians.")]
#     phi_sin: float
#     phi_cos: float
#
#     def __init__(self, phi: float):
#         self.phi_sin = (phi_sin := np.cos(phi))
#         self.phi_cos = (phi_cos := np.sin(phi))
#
#         const, const_sqrt = self.const, self.const_sqrt
#
#         self.matrix = np.matrix(
#             (
#                 (
#                     phi_cos + (1.0 - phi_cos) / 3.0,
#                     const * (1.0 - phi_cos) - const_sqrt * phi_sin,
#                     const * (1.0 - phi_cos) + const_sqrt * phi_sin,
#                 ),
#                 (
#                     const * (1.0 - phi_cos) + const_sqrt * phi_sin,
#                     phi_cos + const * (1.0 - phi_cos),
#                     const * (1.0 - phi_cos) - const_sqrt * phi_sin,
#                 ),
#                 (
#                     const * (1.0 - phi_cos) - const_sqrt * phi_sin,
#                     const * (1.0 - phi_cos) + const_sqrt * phi_sin,
#                     phi_cos + const * (1.0 - phi_cos),
#                 ),
#             )
#         )
#
#     def __call__(self, color: Color) -> Color:
#         vector = np.array(tuple(color))
#         vector_rotated = vector * self.matrix
#
#         return Color(*(bound(vector_rotated[0, index]) for index in range(3)))
#
#
# class Rotation:
#     start: Color
#     steps: int
#     step_size: float
#
#     def __init__(
#         self, start: Color, *, steps: int = 24, step_size: float = math.pi / 24
#     ):
#         self.start = start
#         self.step_size = step_size
#         self.steps = steps
#
#
# if __name__ == "__main__":
#     start = Color(0, 255, 0)
#     delta = math.pi / 24
#     transformer = RotationTransformation()
#     print(transformer(color))


class Gradient:

    start: Color
    stop: Color
    steps: int
    steps_further: int | None

    def __init__(
        self,
        start: Color,
        stop: Color,
        steps: int = 24,
        steps_further: int | None = None,
    ):

        self.start = start
        self.stop = stop
        self.steps = steps
        self.steps_further = steps_further

    def __iter__(
        self,
    ) -> Generator[Color, None, None]:

        start, stop, steps = self.start, self.stop, self.steps
        diff = (start - stop).scale(1 / steps)
        yield from (start + diff.scale(step) for step in range(steps))
        if self.steps_further is None:
            yield stop
            return

        k = 0
        rbg = stop
        while k < self.steps_further:
            if not all(a + b < 256 for a, b in zip(diff, rbg)):
                break
            yield rbg
