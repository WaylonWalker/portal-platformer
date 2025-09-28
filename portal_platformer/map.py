from functools import cached_property
from portal_platformer.config import config
from typing import Optional
from pathlib import Path

import pygame
from pydantic import BaseModel

from portal_platformer.color import Color, ColorPalette


class Checkpoint(BaseModel):
    name: str
    x: int
    y: int


class Link(BaseModel):
    name: str
    checkpoint: Checkpoint


class Object(BaseModel):
    name: Optional[str] = None
    x: int
    y: int
    width: int
    height: int
    color: Optional[Color | ColorPalette] = ColorPalette.black
    damage: bool = False
    collision: bool = False
    hidden: bool = False
    open: bool = False
    link: Optional[Link] = None

    @cached_property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def screen(self) -> pygame.Surface:
        return pygame.display.get_surface()

    def draw(self, camera):
        if self.rect.colliderect(camera.state):
            try:
                color = self.color.rgb
            except AttributeError:
                color = self.color
            pygame.draw.rect(
                self.screen,
                # self.color.rgb,
                color,
                (
                    self.x - camera.state.left,
                    self.y - camera.state.top,
                    self.width,
                    self.height,
                ),
            )


class CheckpointObject(Object):
    def __init__(self, x, y, width, height, color, screen, checkpoint, checkpoint_name):
        super().__init__(x, y, width, height, color, screen)
        self.checkpoint = checkpoint
        self.checkpoint_name = checkpoint_name


class Map(BaseModel):
    name: str
    colors: list[Color] = []
    checkpoints: list[CheckpointObject] = []
    objects: list[Object] = []

    def save(self):
        save_file = config.assets_dir / "maps" / f"{self.name}.json"
        save_file.write_text(self.model_dump_json(indent=2))
