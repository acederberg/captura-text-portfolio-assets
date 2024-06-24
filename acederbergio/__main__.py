import uvicorn
from fastapi import FastApi


def create_fastapi(app=None):

    app = FastApi() if app is None else app
    app.include_router(app, "/colors")
    return app


def create_typer():
    @cli.command("run")
    def cmd_run():
        uvicorn.run("gencolors:__main__:create_fastapi", reload=True)

    return cli


if __name__ == "__main__":
    cli = create_typer()
    cli()
