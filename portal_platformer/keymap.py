from pydantic import BaseModel
from pydantic import field_validator
from typing import ClassVar, Set, List
import pygame


def wait_for_key():
    waiting = True
    key_pressed = None
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                key_pressed = event.key
                waiting = False
    # Reverse map: key code -> pygame constant name (e.g., 32 -> "K_SPACE")
    for key_name in dir(pygame):
        if key_name.startswith("K_") and getattr(pygame, key_name) == key_pressed:
            return key_name

    raise ValueError(f"Unrecognized key code: {key_pressed}")
    # return pygame.key.name(key_pressed)


class Key(BaseModel):
    key: str
    _valid_keys: ClassVar[Set[str]] = {k for k in dir(pygame) if k.startswith("K_")}
    history: List[bool] = []
    history_length: int = 5

    def update(self, keys):
        self.history.append(keys[self.key_id])
        if len(self.history) > self.history_length:
            self.history.pop(0)

    @property
    def key_id(self):
        return getattr(pygame, self.key)

    @property
    def is_pressed(self):
        return self.history[-1]

    @property
    def is_released(self):
        return not self.is_pressed()

    @property
    def key_down(self):
        if self.history:
            if self.history[-1] and not self.history[-2]:
                return True

    @property
    def key_up(self):
        if self.history:
            if not self.history[-1] and self.history[-2]:
                return True

    def remap(self, game):
        key = wait_for_key()
        self.key = key
        game.menu = game.menu.update(game)

    @field_validator("key")
    def validate_key(cls, v):
        if v not in cls._valid_keys:
            raise ValueError(
                f"{v} is not a valid pygame key. Must be one of: {', '.join(sorted(cls._valid_keys))}"
            )
        return v


class KeyMap(BaseModel):
    jump: Key = Key(key="K_SPACE")
    left: Key = Key(key="K_LEFT")
    right: Key = Key(key="K_RIGHT")
    up: Key = Key(key="K_UP")
    down: Key = Key(key="K_DOWN")
    menu: Key = Key(key="K_ESCAPE")
    select: Key = Key(key="K_j")
    debug: Key = Key(key="K_F3")
    fullscreen: Key = Key(key="K_F11")

    def update(self, keys):
        self.jump.update(keys)
        self.left.update(keys)
        self.right.update(keys)
        self.up.update(keys)
        self.down.update(keys)
        self.menu.update(keys)
        self.select.update(keys)
        self.debug.update(keys)
        self.fullscreen.update(keys)


if __name__ == "__main__":
    print(KeyMap())
