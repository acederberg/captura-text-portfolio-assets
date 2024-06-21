from typing import Generator, Tuple

import typer


def parse_hex(hex: str) -> Tuple[int, int, int]:
    if hex.startswith("#"):
        hex = hex[1:]
    if len(hex) != 6:
        raise ValueError("Must be 6 long.")

    hex_chunks = (hex[i : i + 2] for i in range(3))
    return tuple(int(hex_chunk, 16) for hex_chunk in hex_chunks)  # type: ignore


def parse_rgb(rgb: Tuple[int, int, int]) -> str:

    return "#" + "".join(hex(elem)[2:] for elem in rgb)


def interpolate(
    hex_start: str, hex_stop: str, steps: int = 5
) -> Generator[Tuple[int, int, int], None, None]:

    start, stop = parse_hex(hex_start), parse_hex(hex_stop)
    diff = tuple((1 + s - t) / (steps) for s, t in zip(stop, start))
    yield from (  # type: ignore
        tuple(int(s0 + (step * s)) for s0, s in zip(start, diff))
        for step in range(steps)
    )
    yield stop


if __name__ == "__main__":
    cli = typer.Typer()

    @cli.command("parse")
    def cmd_hex(hex: str):
        print(parse_hex(hex))

    @cli.command("parse")
    def cmd_rgb(red: int, blue: int, green: int):
        print(parse_rgb((red, blue, green)))

    @cli.command("interpolate")
    def cmd_interpolate(
        hex_start: str, hex_stop: str, steps: int = 5, as_hex: bool = True
    ):
        lines = interpolate(hex_start, hex_stop, steps)
        for line in lines:
            if as_hex:
                line = parse_rgb(line)

            print(line)

    cli()
