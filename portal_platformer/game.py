from functools import lru_cache
from pathlib import Path

import jinja2
import pygame
from pyinstrument import Profiler
from rich.console import Console

from portal_platformer.camera import Camera
from portal_platformer.map import Map
from portal_platformer.player import Player

console = Console()


templateLoader = jinja2.FileSystemLoader(
    searchpath=Path(__file__).parents[1] / "assets/maps"
)
templates = jinja2.Environment(loader=templateLoader)


@lru_cache
def _rect(x, y, width, height):
    return pygame.Rect(x, y, width, height)


class Game:
    def __init__(
        self,
        debug=False,
        fullscreen=False,
        width=1920,
        height=1080,
        map="test",
    ):
        pygame.init()
        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=1,
            buffer=512,
        )

        # pygame.mixer.pre_init(
        #     frequency=44100,
        #     size=-16,
        #     channels=2,
        #     buffer=2048,
        # )
        self.draw_rate = 4
        self.debug = debug
        self.messages = []
        self.running = True
        # self.screen = pygame.display.set_mode((1920, 1080))
        # self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        print("fullscreen")
        print(fullscreen)
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.events = pygame.event.get()
        self.player = Player(self)
        self.load_map(map)
        self.fps = []
        pygame.display.set_caption("Portal Platformer")
        try:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
            self.axes = self.controller.get_numaxes()
        except pygame.error:
            self.controller = None

        self.camera = Camera(
            self.screen, self.player, self.screen.get_width(), self.screen.get_height()
        )
        self.font = pygame.font.SysFont(None, 30)

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
            # self.dt = self.clock.tick(65)
            self.tick()
        profile.stop()

        # console.print(f"FPS: {(int(self.clock.get_fps()/5)*5) / self.draw_rate}")
        console.print(f"Profile: {profile.output_text()}")

    def tick(self):
        self.fps.append(self.clock.get_fps())
        self.fps = self.fps[-1000:]
        self.messages.append(f"FPS: {int((sum(self.fps) / len(self.fps))/5) * 5}")
        # self.messages.append(
        #     f"FPS: {int((int(self.clock.get_fps()/5)*5) / self.draw_rate)}"
        # )
        self.messages.append(f"controller: {self.controller.get_name()}")
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                self.running = False

        self.screen.fill("purple")
        # player movement
        keys = pygame.key.get_pressed()

        if keys[pygame.K_F3]:
            self.debug = not self.debug

        self.player.move(keys, self.controller, self.dt)
        self.camera.update()
        if self.frame % self.draw_rate != 0:
            # console.print("skipping draw")
            self.messages = []
            return
        # console.print("drawing")

        # player movement
        self.player.draw(self.camera)
        # for obj in self.objects:
        #     obj.draw(self.camera)
        # for obj in self.ohurt:
        #     obj.draw(self.camera)
        # if self.debug:
        #     for obj in self.checkpoints:
        #         obj.draw(self.camera)

        for obj in self.map.objects:
            obj.draw(self.camera)
        # self.camera.update(self.player)
        if self.debug:
            self.camera.draw()

        if self.debug:
            self.render_messages()
        self.messages = []

        self.screen.blit(self.camera.surf, (0, 0))
        pygame.display.flip()

    def render_messages(self):
        message_height = 10
        # print("--" * 20)
        for message in self.messages:
            message_surface = self.font.render(message, True, (255, 255, 255))
            self.screen.blit(message_surface, (10, message_height))
            message_height += 20
            # print(message)
