class ControllerState:
    def __init__(self, joystick, previous_controller_state):
        self.buttons = [
            joystick.get_button(i) for i in range(joystick.get_numbuttons())
        ]
        self.axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        self.hats = [joystick.get_hat(i) for i in range(joystick.get_numhats())]
        self.previous_controller_state = previous_controller_state

    def get_button(self, index):
        return self.buttons[index]

    def button_pressed(self, index):
        return self.buttons[index] and not self.previous_controller_state.buttons[index]

    def button_released(self, index):
        return not self.buttons[index] and self.previous_controller_state.buttons[index]
