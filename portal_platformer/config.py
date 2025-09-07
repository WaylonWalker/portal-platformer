from pydantic_settings import BaseSettings
from pathlib import Path


class Config(BaseSettings):
    coyote_time: int = 25
    assets_dir: Path = "assets"


config = Config()
