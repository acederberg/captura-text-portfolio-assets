# =========================================================================== #
from typing import Type

from app.views import AppView


def captura_plugins_app(app_view: Type[AppView]):
    """The text extension is required!"""

    from acederbergio import ColorView
    from text_app.router import TextView

    app_view.view_router.include_router(TextView.view_router, prefix="/text")
    app_view.view_router.include_router(ColorView.view_router, prefix="/colors")


def captura_plugins_client(requests):

    from text_client import TextCommands

    requests.typer_children.update(text=TextCommands)
