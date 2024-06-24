from pydantic import BaseModel


class ColorRGB(BaseModel):
    r: int
    g: int
    b: int


class ColorSchema(BaseModel):
    rgb: ColorRGB
    hex: str
