from pathlib import Path
from typing import List

from pydantic import BaseModel


class SaveState:
    def __init__(self, game, save_file="save_state"):
        self.game = game
        self.save_file = Path(__file__).parents[1] / "saves" / (save_file + ".json")
        self.load()

    def save(self):
        self.save_file.parent.mkdir(parents=True, exist_ok=True)
        self.save_file.write_text(self.state.model_dump_json(indent=2))

    def load(self):
        if self.save_file.exists():
            self.state = State.model_validate_json(self.save_file.read_text())
        else:
            self.state = State()


class PlayerState(BaseModel):
    x: int = 100
    y: int = 1380
    checkpoint: List[int] = (100, 1380)


class MapState(BaseModel):
    name: str = "test"


class State(BaseModel):
    player: PlayerState = PlayerState()
    map: MapState = MapState()
