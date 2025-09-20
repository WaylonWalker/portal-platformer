from pathlib import Path
from portal_platformer.keymap import KeyMap
from portal_platformer.keymap import EditorKeyMap

from portal_platformer.map import Checkpoint

from pydantic import BaseModel


class SaveState:
    def __init__(self, game, is_editor=False, save_file="save_state",):
        self.game = game
        self.is_editor = is_editor
        self.save_file = Path(__file__).parents[1] / "saves" / (save_file + ".json")
        if self.is_editor:
            self.state_model = EditorState
        else:
            self.state_model = State
        self.load()

    def save(self):
        self.save_file.parent.mkdir(parents=True, exist_ok=True)
        self.save_file.write_text(self.state.model_dump_json(indent=2))

    def load(self):
        if self.save_file.exists():

            self.state = self.state_model.model_validate_json(self.save_file.read_text())
        else:
            self.state = self.state_model()


class PlayerState(BaseModel):
    x: int = 100
    y: int = 1380
    checkpoint: Checkpoint = Checkpoint(name="test", x=100, y=1380)


class MapState(BaseModel):
    name: str = "test"


class State(BaseModel):
    player: PlayerState = PlayerState()
    map: MapState = MapState()
    keymap: KeyMap = KeyMap()

class EditorState(BaseModel):
    player: PlayerState = PlayerState()
    map: MapState = MapState()
    keymap: EditorKeyMap = EditorKeyMap()
