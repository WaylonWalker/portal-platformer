import pygame
from random import randint


class Light:
    def __init__(self, game, x, y, radius, color):
        self.game = game
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    @property
    def screen(self) -> pygame.Surface:
        return pygame.display.get_surface()

    def draw(self):
        LIGHT_COLOR = (255, 255, 200, 2)
        LIGHT_RADIUS = 200
        surface = pygame.Surface((LIGHT_RADIUS * 2, LIGHT_RADIUS * 2), pygame.SRCALPHA)

        pygame.draw.circle(
            surface, LIGHT_COLOR, (LIGHT_RADIUS, LIGHT_RADIUS), LIGHT_RADIUS
        )
        LIGHT_COLOR = (255, 255, 200, 5 * (randint(8, 10) / 10))
        pygame.draw.circle(
            surface, LIGHT_COLOR, (LIGHT_RADIUS, LIGHT_RADIUS), LIGHT_RADIUS / 1.2
        )
        LIGHT_COLOR = (255, 255, 200, 15 * (randint(8, 10) / 10))
        pygame.draw.circle(
            surface, LIGHT_COLOR, (LIGHT_RADIUS, LIGHT_RADIUS), LIGHT_RADIUS / 1.5
        )
        LIGHT_COLOR = (255, 255, 200, 50 * (randint(8, 10) / 10))
        pygame.draw.circle(
            surface, LIGHT_COLOR, (LIGHT_RADIUS, LIGHT_RADIUS), LIGHT_RADIUS / 8
        )
        LIGHT_COLOR = (255, 255, 200, 90 * (randint(8, 10) / 10))
        pygame.draw.circle(
            surface, LIGHT_COLOR, (LIGHT_RADIUS, LIGHT_RADIUS), LIGHT_RADIUS / 22
        )

        self.screen.blit(
            surface,
            (
                self.x - LIGHT_RADIUS + 40,
                self.y - LIGHT_RADIUS + 30,
            ),
        )
        # pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.radius)
