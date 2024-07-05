# =========================================================================== #
from typing import Type

from app.views import AppView


def captura_plugins_app(app_view: Type[AppView]):
    """The text extension is required!"""

    from acederbergio import ColorView
    from app.depends import DependsSessionMaker
    from text_app import depends
    from text_app.router import TextView

    @app_view.view_router.get("/text")
    def get_home(
        sessionmaker: DependsSessionMaker,
        status: depends.DependsTextBuilderStatus,
        template: depends.DependsTemplate,
    ):
        data = depends.get_by_name_json(sessionmaker, status, name="home")  # type: ignore
        return depends.get_by_name_text(data, template, "home")  # type: ignore

    app_view.view_router.include_router(TextView.view_router, prefix="/text")
    app_view.view_router.include_router(ColorView.view_router, prefix="/colors")


def captura_plugins_client(requests):

    from text_client import TextCommands

    requests.typer_children.update(text=TextCommands)
