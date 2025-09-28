from pydantic_settings import BaseSettings
import json
from pathlib import Path
# from pygame import Color
from portal_platformer.color import Color
from pydantic import field_validator


class Config(BaseSettings):
    coyote_time: int = 25
    jump_time: int = 500
    player_speed: float = 0.5
    gravity: float = 0.01
    apex_hang_time:float = 1.08          # seconds of grace near the top
    apex_speed_threshold:float = 20.0    # px/s | consider “near apex” if |speedy| <= this
    apex_gravity_scale:float = 0.05      # apply only 25% gravity during hang
    assets_dir: Path = "assets"
    grid_size: int = 10
    color_palette: list[str | Color] = ["#343434", "#7b7b7b", "#36ad69", "#e2d6b5"]

    @field_validator("color_palette")
    @classmethod
    def validate_color_palette(cls, value):
        colors = []
        for color in value:
            if not isinstance(color, Color):
                colors.append(Color.from_str(color))
            else:
                colors.append(color)
        return colors



config = Config()

if (config.assets_dir / 'config.json').is_file():
    config = Config.parse_obj(json.loads((config.assets_dir / 'config.json').read_text()))



