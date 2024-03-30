import pygame
import asyncio

# Initialize pygame
pygame.init()

# Window size
window_width = 800
window_height = 600
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Simple portal game")

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# Define the portal
portal_x = window_width // 2
portal_y = window_height - 100
portal_radius = 50

# Create a font for the portal's message
font = pygame.font.SysFont("arial", 36)
text = font.render("Press R to teleport", True, white)
text_rect = text.get_rect(center=(portal_x, portal_y))

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Check if the player wants to teleport
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Reset the game when teleporting
                portal_x = window_width // 2
                portal_y = window_height - 100

    # Fill the screen with black
    screen.fill(black)

    # Draw the portal and its message
    pygame.draw.circle(screen, blue, (portal_x, portal_y), portal_radius)
    screen.blit(text, text_rect)

    # Update the display
    pygame.display.flip()

# Quit pygame
pygame.quit()
