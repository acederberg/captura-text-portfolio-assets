import functools
import json
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
import typer
import uvicorn
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, TypeAdapter
from rich.console import Console


class ColorRGB(BaseModel):
    r: int
    g: int
    b: int


class ColorSchema(BaseModel):
    rgb: ColorRGB
    hex: str


# NOTE: Use this when a user lands on the page.
PRETTY_PAIRS = {
    ("cd0ddc", "eb7616"),
}


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

    def interpolate(
        self,
        to: Self,
        *,
        steps: int = 5,
        steps_further: int | None = None,
    ) -> Generator[Self, None, None]:
        diff = (self - to).scale(1 / steps)
        yield from (self + diff.scale(step) for step in range(steps))
        if not steps_further:
            yield to
            return

        k = 0
        rbg = to
        while all(value < 256 for value in rbg) and k < steps_further:
            yield rbg
            rbg = rbg + diff


def test_diff():
    a = Color(0, 1, 2)
    b = Color(128, 128, 128)
    c = a - b

    assert all(elem == index - 128 for index, elem in enumerate(c))


def test_interpolate():
    a = Color(0, 128, 0)
    b = Color(0, 0, 0)

    colors = list(a.interpolate(b, steps=128 // 8))
    assert len(colors) == 16

    for count, color in enumerate(colors):
        assert color.r == color.b == 0
        assert color.g == count * 8


def create_fastapi():
    app = fastapi.FastAPI()
    templates = Jinja2Templates(path.realpath(path.dirname(__file__)))

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
        list[Color], fastapi.Depends(colors, use_cache=True)
    ]

    @app.get("/interpolate/json")
    def interpolate_json(
        colors: DependsColors,
        as_hex: bool = True,
    ):
        if as_hex:
            return list(item.hex for item in colors)
        else:
            return list(item.color_schema().model_dump(mode="json") for item in colors)

    @app.get("/interpolate")
    def interpolate(
        request: fastapi.Request,
        colors: DependsColors,
        start: str = "#e9b863",
        stop: str = "#9c79ec",
        steps: int = 24,
    ):
        return templates.TemplateResponse(
            request,
            "colors.j2",
            context=dict(
                colors=colors,
                steps=steps,
                start=start,
                stop=stop,
            ),
        )

    return app


def create_typer():
    console = Console()
    cli = typer.Typer()

    @cli.command("parse-hex")
    def cmd_hex(hex: str):

        color = Color.fromHex(hex)
        console.print_json(json.dumps(color.color_schema().model_dump(mode="json")))

    @cli.command("parse-vector")
    def cmd_rgb(red: int, blue: int, green: int):

        color = Color(red, blue, green)
        console.print_json(json.dumps(color.color_schema().model_dump(mode="json")))

    @cli.command("interpolate")
    def cmd_interpolate(
        hex_start: str,
        hex_stop: str,
        *,
        steps: int = 5,
        steps_further: Optional[int] = None,
        as_hex: bool = True,
    ):

        start = Color.fromHex(hex_start)
        stop = Color.fromHex(hex_stop)

        colors = start.interpolate(
            stop,
            steps=steps,
            steps_further=steps_further,
        )

        if as_hex:
            colors = list(item.hex for item in colors)
        else:
            colors = list(
                item.color_schema().model_dump(mode="json") for item in colors
            )
        console.print_json(json.dumps(colors))

    @cli.command("run")
    def cmd_run():
        uvicorn.run("gencolors:create_fastapi", reload=True)

    return cli


if __name__ == "__main__":
    cli = create_typer()
    cli()
