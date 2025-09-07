import typer

from portal_platformer.game import Game
from portal_platformer.server import Server
from portal_platformer.controller_button_debug import listen_controller
from rich.console import Console
from portal_platformer.config import config

app = typer.Typer()
console = Console()


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


@app.command()
def validate_maps():
    game = Game()
    for map_name in game.map_names:
        try:
            game.load_map(map_name)
            console.print(f"[green]{map_name} is valid[/green]")
        except Exception as e:
            console.print(f"[red]{map_name} is invalid[/red]")
            if "Invalid JSON" in str(e):
                # get line, column from message
                # Invalid JSON: trailing characters at line 1 column 2
                message = [m for m in str(e).splitlines() if "Invalid JSON" in m][
                    0
                ].split()
                line = int(message[message.index("line") + 1])
                column = int(message[message.index("column") + 1])
                console.print(f"[red]   line: {line}, column: {column}[/red]")
            else:
                console.print(e)


@app.command("listen-controller")
def cli_listen_controller():
    listen_controller()


@app.command()
def server():
    server = Server()
    server.run()


@app.command()
def config_show():
    console.print(config.dict())


if __name__ == "__main__":
    app()
