from functools import lru_cache
from portal_platformer.menu import create_menu
from typing import Optional


import jinja2
import pygame
from pyinstrument import Profiler
from rich.console import Console

from portal_platformer.camera import Camera
from portal_platformer.map import Map
from portal_platformer.player import Editor as Player
from portal_platformer.state import SaveState
from portal_platformer.controller_state import ControllerState
from portal_platformer.config import config

console = Console()


templateLoader = jinja2.FileSystemLoader(searchpath=config.assets_dir / "maps")

templates = jinja2.Environment(loader=templateLoader)


@lru_cache
def _rect(x, y, width, height):
    return pygame.Rect(x, y, width, height)


class Editor:
    def __init__(
        self,
        debug=False,
        fullscreen=False,
        width=1920,
        height=1080,
        map: Optional[str] = None,
        save_file="editor_save_state",
    ):
        pygame.init()
        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=1,
            buffer=512,
        )

        self.save_state = SaveState(self, is_editor=True, save_file=save_file)
        self.state = self.save_state.state

        self.draw_rate = 4
        self.debug = debug
        self.messages = []
        self.running = True
        self.paused = False
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.events = pygame.event.get()
        self.player = Player.from_game_object(self)
        self.player.height = 10
        self.player.width = 10

        pygame.mouse.set_visible(False)  # Optional: Hides the mouse cursor
        pygame.event.set_grab(True)  # Grabs the mouse, confining it to the window

        if map is None and self.state.map.name is None:
            map = "test"
        if self.state.map.name is not None:
            map = self.state.map.name
        self.load_map(map)
        self.fps = []
        pygame.display.set_caption("Portal Platformer")
        try:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
            self.axes = self.controller.get_numaxes()
            self.controller_state = ControllerState(self.controller, self.controller)
        except pygame.error:
            self.controller = None

        self.camera = Camera(
            self.screen, self.player, self.screen.get_width(), self.screen.get_height()
        )
        self.camera.editor_mode = not self.camera.editor_mode
        self.font = pygame.font.SysFont(None, 30)

    def message(self, message):
        self.messages.append(message)

    @property
    def map_names(self):
        return [f.stem for f in (config.assets_dir / "maps").glob("*.json")]

    def load_map(self, map_name: str):
        self.map = Map.model_validate_json(
            templates.get_template(f"{map_name}.json").render({"game": self})
        )
        self.map.name = map_name

    def run(self):
        profile = Profiler()
        profile.start()
        self.frame = 0
        while self.running:
            self.frame += 1
            self.dt = self.clock.tick(800)
            # self.dt = self.clock.tick(120)
            self.tick()
        profile.stop()

        # console.print(f"FPS: {(int(self.clock.get_fps()/5)*5) / self.draw_rate}")
        console.print(f"Profile: {profile.output_text()}")

    def tick(self):
        if self.controller:
            self.controller_state = ControllerState(
                self.controller, self.controller_state
            )
        self.fps.append(self.clock.get_fps())
        self.fps = self.fps[-1000:]
        self.messages.append(f"FPS: {int((sum(self.fps) / len(self.fps)) / 5) * 5}")
        self.messages.append(
            f"DRAW FPS: {(int((sum(self.fps) / len(self.fps)) / 5) * 5) / self.draw_rate}"
        )
        # self.messages.append(
        #     f"FPS: {int((int(self.clock.get_fps()/5)*5) / self.draw_rate)}"
        # )
        if self.controller:
            self.messages.append(f"controller: {self.controller.get_name()}")
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                self.running = False

        self.screen.fill((125, 125, 125))
        # player movement
        keys = pygame.key.get_pressed()
        self.state.keymap.update(keys)

        if self.controller:
            if self.controller_state.button_pressed(8):
                self.paused = not self.paused
                if self.paused:
                    self.menu = create_menu(self)
                print(self.save_state.state.keymap)

        if self.state.keymap.menu.key_down:
            self.paused = not self.paused
            if self.paused:
                self.menu = create_menu(self)

        if self.paused:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
        else:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)

        if self.paused:
            if self.state.keymap.down.key_down:
                self.menu.move_down()
            if self.state.keymap.up.key_down:
                self.menu.move_up()
            if self.state.keymap.select.key_down:
                print("select")
                self.menu.select()
                self.save_state.save()
            self.menu.draw()

            if self.debug:
                self.render_messages()
            self.messages = []
            pygame.display.flip()
            return

        if self.state.keymap.debug.key_down:
            self.debug = not self.debug

        self.player.move(keys, self.controller, self.dt)
        self.camera.update()
        if self.frame % self.draw_rate != 0:
            # console.print("skipping draw")
            self.messages = []
            return

        self.message("map: " + self.map.name)
        for obj in self.map.objects:
            obj.draw(self.camera)

        self.player.draw(self.camera)
        # self.camera.update(self.player)
        if self.debug:
            self.camera.draw()

        if self.debug:
            self.render_messages()
        self.messages = []

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((255, 180, 100))
        overlay.set_alpha(50)
        # self.screen.blit(self.camera.surf, (0, 0))
        self.screen.blit(overlay, (0, 0))
        pygame.display.flip()

    def render_messages(self):
        message_height = 10
        # print("--" * 20)
        for message in self.messages:
            message_surface = self.font.render(message, True, (255, 255, 255))
            self.screen.blit(message_surface, (10, message_height))
            message_height += 20
            # print(message)


if __name__ == "__main__":
    editor = Editor(debug=True)
    editor.run()
