from pydantic import BaseModel, field_validator
from typing import ClassVar, Set, List, Optional, Iterable
import pygame

# -----------------------
# Mouse name <-> indices
# -----------------------
# pygame.event MOUSEBUTTONDOWN: button numbers -> names
EVENT_BUTTON_TO_NAME = {
    1: "MOUSE_LEFT",
    2: "MOUSE_MIDDLE",
    3: "MOUSE_RIGHT",
    4: "MOUSE_WHEEL_UP",    # wheel is event-only (no "pressed" state)
    5: "MOUSE_WHEEL_DOWN",  # wheel is event-only (no "pressed" state)
    6: "MOUSE_X1",
    7: "MOUSE_X2",
}

# pygame.mouse.get_pressed() index -> names (holdable buttons only)
# get_pressed() returns tuple like (left, middle, right, x1, x2) on most platforms
MOUSE_INDEX_TO_NAME = {
    0: "MOUSE_LEFT",
    1: "MOUSE_MIDDLE",
    2: "MOUSE_RIGHT",
    3: "MOUSE_X1",
    4: "MOUSE_X2",
}
MOUSE_NAME_TO_INDEX = {v: k for k, v in MOUSE_INDEX_TO_NAME.items()}

# Wheel names (edge-only, detected from events, not holdable)
WHEEL_NAMES = {"MOUSE_WHEEL_UP", "MOUSE_WHEEL_DOWN"}


def wait_for_key():
    """Blocks until a key is pressed OR a mouse button/wheel event occurs.
    Returns names like 'K_SPACE' or 'MOUSE_LEFT' / 'MOUSE_WHEEL_UP'."""
    waiting = True
    result_name = None

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                # Reverse map: key code -> 'K_*'
                for key_name in dir(pygame):
                    if key_name.startswith("K_") and getattr(pygame, key_name) == event.key:
                        result_name = key_name
                        waiting = False
                        break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Map button number -> friendly mouse name
                result_name = EVENT_BUTTON_TO_NAME.get(event.button, f"MOUSE_{event.button}")
                waiting = False

            elif event.type == pygame.MOUSEWHEEL:
                result_name = "MOUSE_WHEEL_UP" if event.y > 0 else "MOUSE_WHEEL_DOWN"
                waiting = False

    if result_name is None:
        raise ValueError("Unrecognized input event")
    return result_name


class Key(BaseModel):
    key: str
    # All pygame K_* plus our mouse names
    _valid_keys: ClassVar[Set[str]] = (
        {k for k in dir(pygame) if k.startswith("K_")}
        | set(MOUSE_NAME_TO_INDEX.keys())
        | set(EVENT_BUTTON_TO_NAME.values())
        | WHEEL_NAMES
    )

    history: List[bool] = []
    history_length: int = 5

    def update(
        self,
        keys,  # from pygame.key.get_pressed()
        mouse_buttons: Optional[Iterable[bool]] = None,  # from pygame.mouse.get_pressed(5)
        recent_events: Optional[list] = None,  # list of events from this frame (for wheel edge)
    ):
        """Append current pressed-state for this key/mouse to `history`.

        Keyboard: uses `keys[pygame.K_*]`.
        Mouse buttons: uses `mouse_buttons[index]`.
        Wheel: True only on a frame where a matching MOUSEWHEEL event occurred.
        """
        state = False

        if self.key.startswith("K_"):
            state = keys[getattr(pygame, self.key)]

        elif self.key in MOUSE_NAME_TO_INDEX:
            if mouse_buttons is None:
                mouse_buttons = pygame.mouse.get_pressed(5)
            idx = MOUSE_NAME_TO_INDEX[self.key]
            # Guard against tuples shorter than expected
            if idx < len(mouse_buttons):
                state = bool(mouse_buttons[idx])

        elif self.key in WHEEL_NAMES:
            # Edge-triggered from events; "pressed" only on the frame we see the wheel event
            if recent_events:
                if self.key == "MOUSE_WHEEL_UP":
                    state = any(
                        (e.type == pygame.MOUSEWHEEL and getattr(e, "y", 0) > 0)
                        for e in recent_events
                    )
                else:  # MOUSE_WHEEL_DOWN
                    state = any(
                        (e.type == pygame.MOUSEWHEEL and getattr(e, "y", 0) < 0)
                        for e in recent_events
                    )

        # Record history
        self.history.append(state)
        if len(self.history) > self.history_length:
            self.history.pop(0)

    @property
    def key_id(self):
        """Keyboard constant or None for mouse (since mouse doesn't have a pygame K_* id)."""
        if self.key.startswith("K_"):
            return getattr(pygame, self.key)
        return None

    @property
    def is_pressed(self):
        return bool(self.history and self.history[-1])

    @property
    def is_released(self):
        return not self.is_pressed

    @property
    def key_down(self):
        # pressed this frame, not pressed last frame
        return bool(len(self.history) >= 2 and self.history[-1] and not self.history[-2])

    @property
    def key_up(self):
        # released this frame, pressed last frame
        return bool(len(self.history) >= 2 and (not self.history[-1]) and self.history[-2])

    def remap(self, game):
        self.key = wait_for_key()
        game.menu = game.menu.update(game)

    @field_validator("key")
    def validate_key(cls, v):
        if v not in cls._valid_keys:
            raise ValueError(
                f"{v} is not a valid key. Must be one of: {', '.join(sorted(cls._valid_keys))}"
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
    crouch: Key = Key(key="K_LSHIFT")
    sprint: Key = Key(key="K_LCTRL")

    def update(self, keys, mouse_buttons=None, recent_events=None):
        self.jump.update(keys, mouse_buttons, recent_events)
        self.left.update(keys, mouse_buttons, recent_events)
        self.right.update(keys, mouse_buttons, recent_events)
        self.up.update(keys, mouse_buttons, recent_events)
        self.down.update(keys, mouse_buttons, recent_events)
        self.menu.update(keys, mouse_buttons, recent_events)
        self.select.update(keys, mouse_buttons, recent_events)
        self.debug.update(keys, mouse_buttons, recent_events)
        self.fullscreen.update(keys, mouse_buttons, recent_events)
        self.crouch.update(keys, mouse_buttons, recent_events)
        self.sprint.update(keys, mouse_buttons, recent_events)


class EditorKeyMap(BaseModel):
    left: Key = Key(key="K_LEFT")
    right: Key = Key(key="K_RIGHT")
    up: Key = Key(key="K_UP")
    down: Key = Key(key="K_DOWN")

    place_tile: Key = Key(key="K_SPACE")        # e.g. map to MOUSE_LEFT if you want
    delete_tile: Key = Key(key="K_BACKSPACE")   # e.g. map to MOUSE_RIGHT
    next_color: Key = Key(key="K_n")

    grow_tile_x: Key = Key(key="K_l")
    shrink_tile_x: Key = Key(key="K_h")
    grow_tile_y: Key = Key(key="K_j")
    shrink_tile_y: Key = Key(key="K_k")
    boost: Key = Key(key="K_LSHIFT")
    save: Key = Key(key="K_BACKQUOTE")

    menu: Key = Key(key="K_ESCAPE")
    select: Key = Key(key="K_j")
    debug: Key = Key(key="K_F3")
    fullscreen: Key = Key(key="K_F11")

    def update(self, keys, mouse_buttons=None, recent_events=None):
        self.left.update(keys, mouse_buttons, recent_events)
        self.right.update(keys, mouse_buttons, recent_events)
        self.up.update(keys, mouse_buttons, recent_events)
        self.down.update(keys, mouse_buttons, recent_events)

        self.place_tile.update(keys, mouse_buttons, recent_events)
        self.delete_tile.update(keys, mouse_buttons, recent_events)
        self.next_color.update(keys, mouse_buttons, recent_events)
        self.grow_tile_x.update(keys, mouse_buttons, recent_events)
        self.shrink_tile_x.update(keys, mouse_buttons, recent_events)
        self.grow_tile_y.update(keys, mouse_buttons, recent_events)
        self.shrink_tile_y.update(keys, mouse_buttons, recent_events)
        self.boost.update(keys, mouse_buttons, recent_events)
        self.save.update(keys, mouse_buttons, recent_events)

        self.menu.update(keys, mouse_buttons, recent_events)
        self.select.update(keys, mouse_buttons, recent_events)
        self.debug.update(keys, mouse_buttons, recent_events)
        self.fullscreen.update(keys, mouse_buttons, recent_events)


# -----------------------
# Example loop usage
# -----------------------
# while running:
#     recent_events = list(pygame.event.get())
#     for e in recent_events:
#         if e.type == pygame.QUIT:
#             running = False
#
#     keys = pygame.key.get_pressed()
#     mouse_buttons = pygame.mouse.get_pressed(5)  # (L, M, R, X1, X2)
#
#     keymap.update(keys, mouse_buttons, recent_events)
#
#     if keymap.menu.key_down: ...
#     if keymap.jump.is_pressed: ...

