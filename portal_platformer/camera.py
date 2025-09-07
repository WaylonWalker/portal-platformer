from functools import lru_cache

import pygame


@lru_cache
def _rect(x, y, width, height):
    return pygame.Rect(x, y, width, height)


class Camera:
    def __init__(self, screen, player, width, height):
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
        self.editor_mode = False
        self.editor_speed = 10

    @property
    def rect(self):
        return _rect(self.x, self.y, self.width, self.height)

    def update(self):
        if self.editor_mode:
            self.update_editor()
        else:
            self.update_player()

    def update_editor(self):
        mouse_pos = pygame.mouse.get_pos()
        edge_threshold = 50

        # Move camera when mouse is near edges
        if mouse_pos[0] < edge_threshold:
            self.state.x -= self.editor_speed
        elif mouse_pos[0] > self.width - edge_threshold:
            self.state.x += self.editor_speed

        if mouse_pos[1] < edge_threshold:
            self.state.y -= self.editor_speed
        elif mouse_pos[1] > self.height - edge_threshold:
            self.state.y += self.editor_speed

    def update_player(self):
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
