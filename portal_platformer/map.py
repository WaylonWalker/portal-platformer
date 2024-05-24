from functools import cached_property
from typing import Optional

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
    color: Optional[Color | ColorPalette] = ColorPalette.red
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
            pygame.draw.rect(
                self.screen,
                self.color.rgb,
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
