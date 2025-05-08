import typer

from portal_platformer.game import Game
from portal_platformer.server import Server
from portal_platformer.controller_button_debug import listen_controller

app = typer.Typer()


@app.command()
def run(
    debug: bool = False,
    fullscreen: bool = False,
    width: int = 1920,
    height: int = 1080,
    map: str = "test",
    save_file: str = "save_state",
):
    args = {
        "debug": debug,
        "fullscreen": fullscreen,
        "width": width,
        "height": height,
        "map": map,
        "save_file": save_file,
    }

    game = Game(**args)
    game.run()


@app.command("listen-controller")
def cli_listen_controller():
    listen_controller()


@app.command()
def server():
    server = Server()
    server.run()


if __name__ == "__main__":
    app()
