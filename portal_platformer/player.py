from typing import List, Optional

import pygame


class Player:
    def __init__(
        self,
        game,
        x=None,
        y=None,
        checkpoint=(100, 1380),
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
        self.checkpoint = checkpoint
        self.x = x or self.checkpoint[0]
        self.y = y or self.checkpoint[1]
        self.update_rect()

    def set_checkpoint(self, checkpoint: List[int], map: str = None):
        self.checkpoint = (checkpoint.x, checkpoint.y)
        self.game.save_state.state.player.checkpoint = self.checkpoint
        self.game.save_state.state.player.x = int(self.x)
        self.game.save_state.state.player.y = int(self.y)
        if map is not None:
            self.game.save_state.state.map.name = map
        self.game.save_state.save()

    def reset_to_checkpoint(self):
        self.x = self.checkpoint[0]
        self.y = self.checkpoint[1]
        self.speedx = 0
        self.speedy = 0
        self.falling_timer = 0
        self.jump_timer = 0
        self.update_rect()

    def update_rect(self):
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def check_damage_collisions_after_moving(self):
        # check for collisions with damage causing objects
        collision = False
        for obj in [obj for obj in self.game.map.objects if obj.damage]:
            if self.rect.colliderect(obj.rect):
                collision = True
                # player died
                # go back to checkpoint
                self.reset_to_checkpoint()
        return collision

    def check_checkpoint_collisions_after_moving(self):
        # check for collisions with checkpoints
        # for obj in [obj for obj in self.game.map.objects if obj.checkpoint]:
        #     if self.rect.colliderect(obj.rect):
        #         self.checkpoint = obj.checkpoint

        for obj in [obj for obj in self.game.map.objects if obj.open]:
            if self.rect.colliderect(obj.rect):
                self.game.load_map(obj.link.name)
                # self.checkpoint = (obj.link.checkpoint.x, obj.link.checkpoint.y)
                self.set_checkpoint(obj.link.checkpoint, obj.link.name)
                self.reset_to_checkpoint()

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
        # check for collisions after moving y
        collision = False
        self.update_rect()
        for obj in [obj for obj in self.game.map.objects if obj.collision]:
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

    def move(self, keys, controller, dt):
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
                return
            collision = self.check_collisions_after_moving_y(keys, controller)

            counter += 1

        self.check_checkpoint_collisions_after_moving()

        self.game.messages.append(f"player pos: {round(self.x)}, {round(self.y)}")
        self.game.messages.append(
            f"player speed: {self.speedx:+02.1f}, {self.speedy:+02.1f}"
        )
        self.game.messages.append(
            f"last checkpoint: {self.checkpoint[0]}, {self.checkpoint[1]}"
        )
        self.game.messages.append(f"current map: {self.game.map.name}")

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
