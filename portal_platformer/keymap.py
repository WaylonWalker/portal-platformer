from pydantic import BaseModel
from pydantic import field_validator
from typing import ClassVar, Set
import pygame


class Key(BaseModel):
    key: str

    _valid_keys: ClassVar[Set[str]] = {k for k in dir(pygame) if k.startswith("K_")}

    @property
    def key_id(self):
        return getattr(pygame, self.key)

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


if __name__ == "__main__":
    print(KeyMap())
