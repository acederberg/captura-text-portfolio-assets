# =========================================================================== #
import random
from typing import Annotated, Any, List

from fastapi import Query
from pydantic import BaseModel, BeforeValidator, Field, model_validator


class ColorRGB(BaseModel):
    r: int
    g: int
    b: int


class ColorSchema(BaseModel):
    rgb: ColorRGB
    hex: str


FieldRandom = Annotated[bool, Query()]
FieldSteps = Annotated[int, Field(default=16, gt=0, lt=64)]


FieldColorIn = Annotated[str, Field()]
FieldColorOut = Annotated[ColorSchema, Field()]


class GradientRequest(BaseModel):
    start: FieldColorIn
    stop: FieldColorIn
    steps: FieldSteps


class GradientResponse(BaseModel):
    start: FieldColorOut
    stop: FieldColorOut
    steps: FieldSteps
    items: List[ColorSchema]
