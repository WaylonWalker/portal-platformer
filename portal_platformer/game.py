import random
from functools import lru_cache

import pygame
from pyinstrument import Profiler
from rich.console import Console

console = Console()


@lru_cache
def _rect(x, y, width, height):
    return pygame.Rect(x, y, width, height)


class Object:
    def __init__(self, x, y, width, height, color, screen):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.screen = pygame.display.get_surface()
        self.rect = pygame.Rect(x, y, width, height)

    # @property
    # def rect(self):
    #     return _rect(self.x, self.y, self.width, self.height)
    #
    def draw(self, camera):
        if self.rect.colliderect(camera.state):
            pygame.draw.rect(
                self.screen,
                self.color,
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


class Player:
    def __init__(
        self,
        game,
        x=None,
        y=None,
        height=50,
        width=50,
        color=(255, 255, 175),
    ):
        self.game = game
        self.screen = self.game.screen
        self.height = height
        self.width = width
        self.color = color
        self.screen = pygame.display.get_surface()
        self.speed_factor = 0.5
        self.speed_sprint_factor = 0.75
        self.speed_crouch_factor = 0.25
        self.speed = 1
        self.speedx = 0
        self.speedy = 0
        self.terminal_velocity = 2
        self.gravity = 0.1
        self.jump_timer = 0
        self.max_jump_timer = 150
        self.falling_timer = 0
        self.jump_pressed = False
        self.friction = 0
        self.device_angle = 0
        self.checkpoint = (100, 1380)
        self.x = x or self.checkpoint[0]
        self.y = y or self.checkpoint[1]
        self.update_rect()

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def check_damage_collisions_after_moving(self):
        # check for collisions with damage causing objects
        collision = False
        for obj in self.game.ohurt:
            if self.rect.colliderect(obj.rect):
                collision = True
                self.x = self.checkpoint[0]
                self.y = self.checkpoint[1]
                self.speedx = 0
                self.speedy = 0
                self.update_rect()
        return collision

    def check_checkpoint_collisions_after_moving(self):
        # check for collisions with damage causing objects
        for obj in self.game.checkpoints:
            print(f"checking for checkpoint collision with {obj.checkpoint}")
            if self.rect.colliderect(obj.rect):
                self.checkpoint = obj.checkpoint

    def check_collisions_after_moving_x(self, objects):
        collision = False
        for obj in objects:
            if self.rect.colliderect(obj.rect):
                collision = True

                if self.rect.bottom - obj.rect.top < 5:
                    self.y = obj.rect.top - self.height
                    self.speedy = 0
                elif self.speedx >= 0:
                    self.x = obj.rect.left - self.width
                elif self.speedx < 0:
                    self.x = obj.rect.right
                self.update_rect()

                # wall slide / wall jump
                if self.speedy < 0:
                    self.speedy = self.speedy / 2
                    self.jump_timer = 0
                    self.falling_timer = 0

        return collision

    def check_collisions_after_moving_y(self, objects, keys, controller):
        # check for collisions after moving y
        collision = False
        self.update_rect()
        for obj in objects:
            if self.rect.colliderect(obj.rect):
                # and (
                # self.rect.right > obj.rect.left or self.rect.left < obj.rect.right
                # ):
                collision = True
                if self.speedy < 0:
                    # landed
                    self.y = obj.rect.top - self.height
                    self.speedy = 0
                    self.falling_timer = 0
                    if (
                        not keys[pygame.K_SPACE]
                        and not controller.get_button(0)
                        and not controller.get_button(5)
                    ):
                        self.jump_timer = 0
                elif self.speedy > 0:
                    # hit head
                    self.y = obj.rect.bottom
                    self.speedy = 0
                    self.jump_timer = self.max_jump_timer
                    self.falling_timer = 0
                self.update_rect()
                break

        return collision

    def move(self, keys, objects, controller, dt):
        self.speedx = 0

        # determine speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.speed = self.speed_crouch_factor
        elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            self.speed = self.speed_sprint_factor
        elif controller.get_button(3):
            self.speed = self.speed_sprint_factor
        elif controller.get_button(1):
            self.speed = self.speed_crouch_factor
        else:
            self.speed = self.speed_factor

        # determine direction
        if keys[pygame.K_LEFT]:
            self.speedx -= self.speed
        if keys[pygame.K_RIGHT]:
            self.speedx += self.speed
        if keys[pygame.K_a]:
            self.speedx -= self.speed
        if keys[pygame.K_d]:
            self.speedx += self.speed

        # now do controller
        if abs(controller.get_axis(0)) > 0.1:
            self.speedx += self.speed * controller.get_axis(0)

        # set device angle
        if abs(controller.get_axis(3)) > 0.1:
            vec = pygame.Vector2(controller.get_axis(4), controller.get_axis(3))
            radius, angle = vec.as_polar()  # angle is between -180 and 180.
            # Map the angle that as_polar returns to 0-360 with 0 pointing up.
            adjusted_angle = (angle - 90) % 360
            # adjusted_angle = 180 - adjusted_angle
            # unmirror the angle

            pygame.display.set_caption(
                f"angle: {self.device_angle}, adjusted_angle: {adjusted_angle}"
            )
            self.device_angle = adjusted_angle

        # set speedy and jump_timer
        if keys[pygame.K_SPACE] and self.jump_timer < self.max_jump_timer:
            self.speedy = self.speedy + (self.gravity * dt / 10)
            self.jump_timer += dt
        elif (
            (
                controller.get_button(0)
                or controller.get_button(4)
                or controller.get_button(5)
            )
            and controller.get_button(1)
            and self.jump_timer < self.max_jump_timer
        ):
            self.speedy = self.speedy + (self.gravity * dt / 20)
            self.jump_timer += dt
        elif (
            (
                controller.get_button(0)
                or controller.get_button(4)
                or controller.get_button(5)
            )
            and controller.get_button(3)
            and self.jump_timer < self.max_jump_timer
        ):
            self.speedy = self.speedy + (self.gravity * dt / 8)
            self.jump_timer += dt
        elif (
            controller.get_button(0)
            or controller.get_button(4)
            or controller.get_button(5)
        ) and self.jump_timer < self.max_jump_timer:
            self.speedy = self.speedy + (self.gravity * dt / 10)
            self.jump_timer += dt
        else:
            self.speedy = self.speedy - (self.gravity * dt / 10)
            self.falling_timer += dt
        if self.falling_timer > 25:
            # cyote
            self.jump_timer = self.max_jump_timer

        if abs(self.speedy) > self.terminal_velocity:
            self.speedy = self.terminal_velocity * (self.speedy / abs(self.speedy))
            self.game.messages.append(f"terminal velocity: {round(self.speedy, 4)}")

        # move the character
        self.x += self.speedx * dt
        self.update_rect()

        collision = True
        counter = 0
        while collision and counter < 50:
            self.update_rect()
            damage_collision = self.check_damage_collisions_after_moving()
            if damage_collision:
                return
            collision = self.check_collisions_after_moving_x(objects)
            counter += 1

        # move y
        self.y -= self.speedy * dt
        self.update_rect()

        collision = True
        counter = 0
        while collision and counter < 50:
            self.update_rect()
            damage_collision = self.check_damage_collisions_after_moving()
            if damage_collision:
                return
            collision = self.check_collisions_after_moving_y(objects, keys, controller)

            counter += 1

        self.check_checkpoint_collisions_after_moving()

        self.game.messages.append(f"player pos: {round(self.x)}, {round(self.y)}")
        self.game.messages.append(
            f"player speed: {self.speedx:+02.1f}, {self.speedy:+02.1f}"
        )
        self.game.messages.append(
            f"last checkpoint: {self.checkpoint[0]}, {self.checkpoint[1]}"
        )

        # if controller.get_axis(5) > -0.95:
        #     print("R2 pressed")
        # if controller.get_axis(2) > -0.95:
        #     print("L2 pressed")
        # if controller.get_button(4):
        #     print("L1 pressed")
        # if controller.get_button(5):
        #     print("R1 pressed")

    def draw(self, camera):
        self.game.messages.append(f"player pos: {round(self.x)}, {round(self.y)}")
        device_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        device_surf.set_colorkey("purple")
        device_surf.fill("purple")
        pygame.draw.rect(device_surf, (55, 55, 105), (125, 100, 20, 5))
        # rotate around center
        device_surf = pygame.transform.rotate(device_surf, self.device_angle)
        device_surf = pygame.transform.scale(device_surf, (200, 200))
        self.screen.blit(
            device_surf,
            (
                self.rect.centerx - camera.state.left - 100,
                self.rect.centery - camera.state.top - 100,
            ),
        )

        pygame.draw.rect(
            self.screen,
            self.color,
            (
                self.x - camera.state.left,
                self.y - camera.state.top,
                self.width,
                self.height,
            ),
        )


class Camera:
    def __init__(self, screen, player, width, height):
        # self.camera_func = camera_func
        self.surf = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        self.surf = self.surf.convert_alpha()
        self.screen = screen
        self.player = player
        self.state = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        # padding represents the box when the player is near the edge of the screen and will cause the camera to move
        self.padding = [int(width * 0.8), int(height * 0.8)]
        self.padding_rect = pygame.Rect(
            int(width * 0.2), int(height * 0.2), int(width * 0.6), int(height * 0.6)
        )

    @property
    def rect(self):
        return _rect(self.x, self.y, self.width, self.height)

    def update(self):
        # if (self.player.y - self.player.height) > self.height * 0.6:
        #     self.padding_rect.bottom = int(self.player.y + self.player.height)

        # else:
        #     self.padding_rect.bottom = int(self.height * 0.8)

        if self.player.x < self.padding_rect.left:
            self.padding_rect.left = self.player.x
        if self.player.x + self.player.width > self.padding_rect.right:
            self.padding_rect.right = self.player.x + self.player.width

        if self.player.y < self.padding_rect.top:
            self.padding_rect.top = self.player.y
        if self.player.y + self.player.height > self.padding_rect.bottom:
            self.padding_rect.bottom = self.player.y + self.player.height

        self.state.center = self.padding_rect.center
        # draw a box outline representing the camera
        # draw the collision box

    def draw(self):
        pygame.draw.rect(
            self.surf,
            (255, 0, 0),
            (
                0,
                0,
                self.width,
                self.height,
            ),
            1,
        )

        # draw the collision box
        pygame.draw.rect(
            self.surf,
            (0, 255, 0),
            (
                self.padding_rect.left - self.state.left,
                self.padding_rect.top - self.state.top,
                self.padding_rect.width,
                self.padding_rect.height,
            ),
            1,
        )

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    # def update(self, target):
    #     self.state = self.camera_func(self.state, target)


class Game:
    def __init__(self, debug=False, fullscreen=False):
        pygame.init()
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
            self.screen = pygame.display.set_mode((1920, 1080))
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.events = pygame.event.get()
        self.player = Player(self)
        self.fps = []
        pygame.display.set_caption("Portal Platformer")
        try:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
            self.axes = self.controller.get_numaxes()
        except pygame.error:
            self.controller = None

        self.ohurt = [
            Object(
                -12000,
                self.screen.get_height() + 40 + 100,
                12000 * 2,
                self.screen.get_height(),
                (255, 75, 75),
                self.screen,
            )
        ]
        self.checkpoints = [
            CheckpointObject(
                1200,
                0,
                50,
                self.screen.get_height(),
                (175, 255, 175),
                self.screen,
                (1200, 1200),
                "in the lava",
            ),
            CheckpointObject(
                100,
                0,
                50,
                self.screen.get_height(),
                (175, 255, 175),
                self.screen,
                (100, 1200),
                "spawn",
            ),
        ]

        self.objects = [
            Object(
                300, self.screen.get_height() - 200, 50, 50, (255, 0, 255), self.screen
            ),
            Object(
                600,
                self.screen.get_height() - 200,
                50,
                250,
                (175, 255, 175),
                self.screen,
            ),
            # Object(
            #     -600, self.screen.get_height(), 12000, 50, (100, 155, 255), self.screen
            # ),
            *[
                Object(
                    -600 + 50 * i,
                    self.screen.get_height() + random.randint(-2, 2),
                    40,
                    40,
                    (55, 55, 55),
                    self.screen,
                )
                for i in range(1200)
                if not i % 10 == 0 and not (i - 1) % 10 == 0
            ],
        ]
        self.camera = Camera(
            self.screen, self.player, self.screen.get_width(), self.screen.get_height()
        )
        self.font = pygame.font.SysFont(None, 30)

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

        self.player.move(keys, self.objects, self.controller, self.dt)
        self.camera.update()
        if self.frame % self.draw_rate != 0:
            # console.print("skipping draw")
            self.messages = []
            return
        # console.print("drawing")

        # player movement
        self.player.draw(self.camera)
        for obj in self.objects:
            obj.draw(self.camera)

        for obj in self.ohurt:
            obj.draw(self.camera)
        if self.debug:
            for obj in self.checkpoints:
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
