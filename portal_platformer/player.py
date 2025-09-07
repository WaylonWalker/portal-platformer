from portal_platformer.map import Checkpoint
from typing import Optional
from portal_platformer.config import config

import pygame

from portal_platformer.light import Light


effects = {
    "feather falling": {"gravity": -0.1, "terminal_velocity": -1},
    "double jump": {"jump_count": 1},
    "speed": {
        "speed_factor": 0.5,
        "speed_sprint_factor": 0.75,
        "speed_crouch_factor": 0.25,
    },
}


class Player:
    def __init__(
        self,
        game,
        x=None,
        y=None,
        checkpoint=Checkpoint(name="test", x=100, y=1380),
        height=64,
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
        self.terminal_velocity_up = 1
        self.terminal_velocity = 2
        self.coyote_time = 250
        self.hang_time = 0
        self.gravity = 0.15
        self.jump_strength = 0.1
        self.jump_timer = 0
        self.max_jump_timer = self.jump_strength * 20
        self.falling_timer = 0
        self.jump_pressed = False
        self.friction = 0
        self.checkpoint = checkpoint
        self.x = x or self.checkpoint.x
        self.y = y or self.checkpoint.y
        self.update_rect()
        self.light = Light(
            game=self.game,
            x=self.x,
            y=self.y,
            radius=200,
            color=(255, 255, 255),
        )

        self.effects = ["featther falling"]

        self.facing_right = False
        self.facing_left = False
        self.facing_up = False
        self.facing_down = False

        self.falling = False
        self.jumping = False

        self.front = pygame.image.load(
            config.assets_dir / "player" / "front" / "player-front.png"
        ).convert_alpha()
        self.right = pygame.image.load(
            config.assets_dir / "player" / "side" / "player-side.png"
        ).convert_alpha()
        self.left = pygame.transform.flip(self.right, True, False)

    @classmethod
    def from_game_object(cls, obj):
        return cls(
            game=obj,
            x=obj.save_state.state.player.x,
            y=obj.save_state.state.player.y,
            checkpoint=obj.save_state.state.player.checkpoint,
        )

    def set_checkpoint(self, checkpoint: Checkpoint, map: Optional[str] = None):
        self.checkpoint = checkpoint
        self.game.save_state.state.player.checkpoint = self.checkpoint
        self.game.save_state.state.player.x = int(self.x)
        self.game.save_state.state.player.y = int(self.y)
        if map is not None:
            self.game.save_state.state.map.name = map
        self.game.save_state.save()

    def reset_to_checkpoint(self):
        self.x = self.checkpoint.x
        self.y = self.checkpoint.y
        self.speedx = 0
        self.speedy = 0
        self.falling_timer = 0
        self.jump_timer = 0
        self.update_rect()

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def check_damage_collisions_after_moving(self):
        collision = False
        for obj in [obj for obj in self.game.map.objects if obj.damage]:
            if self.rect.colliderect(obj.rect):
                collision = True
                self.reset_to_checkpoint()
        return collision

    def check_checkpoint_collisions_after_moving(self):
        for obj in [obj for obj in self.game.map.objects if obj.open]:
            if self.rect.colliderect(obj.rect):
                print(f"loading map {obj.link.name}")
                self.game.load_map(obj.link.name)
                self.set_checkpoint(obj.link.checkpoint, obj.link.name)
                print(f"checkpoint: {obj.link.name}.{self.checkpoint}")
                self.reset_to_checkpoint()
                print(f"player x,y: {self.x}, {self.y}")

    def check_collisions_after_moving_x(self):
        collision = False
        for obj in [obj for obj in self.game.map.objects if obj.collision]:
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

    def check_collisions_after_moving_y(self, keys, controller):
        collision = False

        if not controller:
            return collision

        self.update_rect()
        for obj in [obj for obj in self.game.map.objects if obj.collision]:
            if self.rect.colliderect(obj.rect):
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

    def move(self, keys, controller, dt):
        self.speedx = 0

        if controller is None:
            self.game.message("No controller connected")

        # determine speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.speed = self.speed_crouch_factor
        elif keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            self.speed = self.speed_sprint_factor

        elif controller is not None and controller.get_button(3):
            self.speed = self.speed_sprint_factor
        elif controller is not None and controller.get_button(1):
            self.speed = self.speed_crouch_factor
        else:
            self.speed = self.speed_factor

        # determine direction
        if self.game.state.keymap.left.is_pressed:
            self.speedx -= self.speed
        if self.game.state.keymap.right.is_pressed:
            self.speedx += self.speed
        if self.game.state.keymap.up.is_pressed:
            self.speedx -= self.speed
        if self.game.state.keymap.down.is_pressed:
            self.speedx += self.speed

        # now do controller
        if controller is not None and abs(controller.get_axis(0)) > 0.1:
            self.speedx += self.speed * controller.get_axis(0)

        # set speedy and jump_timer
        if (
            self.game.state.keymap.jump.is_pressed
            and self.jump_timer < self.max_jump_timer
        ):
            self.speedy = self.speedy + (self.jump_strength * dt)
            self.jump_timer += dt
        elif (
            (
                (controller is not None and controller.get_button(0))
                or (controller is not None and controller.get_button(4))
                or (controller is not None and controller.get_button(5))
            )
            and (controller is not None and controller.get_button(1))
            and self.jump_timer < self.max_jump_timer
        ):
            self.speedy = self.speedy + (self.jump_strength * dt / 20)
            self.jump_timer += dt
        elif (
            (
                (controller is not None and controller.get_button(0))
                or (controller is not None and controller.get_button(4))
                or (controller is not None and controller.get_button(5))
            )
            and (controller is not Nonw and controller.get_button(3))
            and self.jump_timer < self.max_jump_timer
        ):
            self.speedy = self.speedy + (self.jump_strength * dt / 8)
            self.jump_timer += dt
        elif (
            (controller is not None and controller.get_button(0))
            or (controller is not None and controller.get_button(4))
            or (controller is not None and controller.get_button(5))
        ) and self.jump_timer < self.max_jump_timer:
            self.speedy = self.speedy + (self.jump_strength * dt / 10)
            self.jump_timer += dt
        elif self.game.state.keymap.jump.is_pressed:
            self.falling_timer += dt
        elif self.falling_timer < self.hang_time:
            self.falling_timer += dt
        else:
            self.falling_timer += dt
            self.speedy = self.speedy - (self.gravity * dt / 10)
        if self.falling_timer > self.coyote_time:
            # coyote
            self.jump_timer = self.max_jump_timer

        if abs(self.speedy) > self.terminal_velocity:
            self.speedy = self.terminal_velocity * (self.speedy / abs(self.speedy))
            self.game.messages.append(f"terminal velocity: {round(self.speedy, 4)}")
        if self.speedy > self.terminal_velocity_up:
            self.speedy = self.terminal_velocity_up

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
            collision = self.check_collisions_after_moving_x()
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
                self.game.messages.append("damage collision")
                return
            collision = self.check_collisions_after_moving_y(keys, controller)

            counter += 1

        self.check_checkpoint_collisions_after_moving()

        self.facing = ""
        if self.game.state.keymap.left.is_pressed:
            self.facing_right = False
            self.facing_left = True
        if self.game.state.keymap.right.is_pressed:
            self.facing_left = False
            self.facing_right = True
        if self.game.state.keymap.up.is_pressed:
            self.game.messages.append("up is pressed")
            self.facing_down = False
            self.facing_up = True
        if self.game.state.keymap.down.is_pressed:
            self.facing_up = False
            self.facing_down = True

        if self.facing_left:
            self.facing += "left"
        elif self.facing_right:
            self.facing += "right"
        elif self.facing_up:
            self.facing += "up"
        elif self.facing_down:
            self.facing += "down"

        self.game.messages.append(f"player pos: {round(self.x)}, {round(self.y)}")
        self.game.messages.append(
            f"player speed: {self.speedx:+02.1f}, {self.speedy:+02.1f}"
        )
        self.game.messages.append(
            f"last checkpoint: {self.checkpoint.x}, {self.checkpoint.y}"
        )
        self.game.messages.append(f"current map: {self.game.map.name}")

        self.game.messages.append(f"facing: {self.facing}")

    def draw(self, camera):
        self.game.messages.append(f"player pos: {round(self.x)}, {round(self.y)}")
        self.game.message("jump_timer: " + str(self.jump_timer))
        self.game.message("falling_timer: " + str(self.falling_timer))
        self.game.message(
            "jumps_pressed: " + str(self.game.state.keymap.jump.is_pressed)
        )
        self.game.message("jump_strength" + str(self.jump_strength))

        self.light.x = self.x - camera.state.left
        self.light.y = self.y - camera.state.top
        self.light.draw()
        if self.facing_left:
            self.screen.blit(
                self.left,
                (
                    self.x - camera.state.left,
                    self.y - camera.state.top,
                    self.width,
                    self.height,
                ),
            )
        elif self.facing_right:
            self.screen.blit(
                self.right,
                (
                    self.x - camera.state.left,
                    self.y - camera.state.top,
                    self.width,
                    self.height,
                ),
            )
        else:
            self.screen.blit(
                self.front,
                (
                    self.x - camera.state.left,
                    self.y - camera.state.top,
                    self.width,
                    self.height,
                ),
            )


class Editor(Player):
    def move(self, keys, controller, dt):
        self.x, self.y = pygame.mouse.get_pos()

    def draw(self, camera):
        self.game.messages.append(
            f"camera pos: {round(camera.state.left)}, {round(camera.state.top)}"
        )
        self.game.messages.append(
            f"editor pos: {round(self.x + camera.state.left)}, {round(self.y + camera.state.top)}"
        )
        self.game.messages.append(
            f"mouse pos: {round(pygame.mouse.get_pos()[0])}, {round(pygame.mouse.get_pos()[1])}"
        )
        if self.x > camera.state.right:
            camera.padding_rect.right += 10

        # draw player
        pygame.draw.rect(
            self.screen,
            self.color,
            (
                self.x,
                self.y,
                # self.x - camera.state.left,
                # self.y - camera.state.top,
                self.width,
                self.height,
            ),
        )

        # draw mouse
        pygame.draw.rect(
            self.screen,
            (255, 0, 255),
            (
                pygame.mouse.get_pos()[0],
                pygame.mouse.get_pos()[1],
                10,
                10,
            ),
        )
