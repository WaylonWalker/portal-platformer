from pydantic_settings import BaseSettings
import json
from pathlib import Path


class Config(BaseSettings):
    coyote_time: int = 25
    player_speed: float = 0.5
    gravity: float = 0.8
    assets_dir: Path = "assets"
    grid_size: int = 10

config = Config()

if (config.assets_dir / 'config.json').is_file():
    config = Config.parse_obj(json.loads((config.assets_dir / 'config.json').read_text()))



