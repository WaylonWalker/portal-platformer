import pygame
from portal_platformer.controller_state import ControllerState


def listen_controller():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No controller connected.")
        return

    controller = pygame.joystick.Joystick(0)
    controller.init()
    print(f"Controller connected: {controller.get_name()}")

    pygame.display.set_mode((300, 100))
    pygame.display.set_caption("Controller Listener")
    controller_state = ControllerState(controller, controller)

    running = True
    clock = pygame.time.Clock()

    while running:
        controller_state = ControllerState(controller, controller_state)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            #
            # # Button pressed
            # elif event.type == pygame.JOYBUTTONDOWN:
            #     print(f"Button {event.button} pressed")
            #
            # # Button released
            # elif event.type == pygame.JOYBUTTONUP:
            #     print(f"Button {event.button} released")
            #
            # # Axis movement (controllers or triggers)
            # elif event.type == pygame.JOYAXISMOTION:
            #     print(f"Axis {event.axis} moved to {event.value:.2f}")
            #
            # # Hat switch (D-pad)
            # elif event.type == pygame.JOYHATMOTION:
            #     print(f"D-pad moved to {event.value}")

        for button in range(len(controller_state.buttons)):
            if controller_state.button_pressed(button):
                print(f"Button {button} pressed")
            elif controller_state.button_released(button):
                print(f"Button {button} released")
        for axis in range(len(controller_state.axes)):
            if (
                abs(
                    controller_state.axes[axis]
                    - controller_state.previous_controller_state.axes[axis]
                )
                > 0.01
            ):
                print(f"Axis {axis} moved to {controller_state.axes[axis]:.2f}")
        for hat in range(len(controller_state.hats)):
            if (
                controller_state.hats[hat]
                != controller_state.previous_controller_state.hats[hat]
            ):
                print(f"D-pad moved to {controller_state.hats[hat]}")

        clock.tick(60)

    pygame.quit()
