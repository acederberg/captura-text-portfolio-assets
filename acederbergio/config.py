# =========================================================================== #
from os import environ, path

from app.util import from_env

PATH_ROOT = path.join(path.realpath(path.dirname(__file__)))
PATH_TEMPLATES = environ.get(
    "ACEDERBERG_IO_TEMPLATES",
    default=path.join(PATH_ROOT, "templates"),
)
