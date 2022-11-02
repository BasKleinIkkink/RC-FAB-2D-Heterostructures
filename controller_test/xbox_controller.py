from xbox360controller import Xbox360Controller
import signal


class CustomXbox360Controller:
    """
    Class to make the configuring and usinf of the controller easier.

    The class is a wrapper around the xbox360controller library.

    Default controll layout:
    ------------------------
    left joystick:
        - left/right: Move the mask left/right
        - up/down: move 
    right joystick:
        - left/right: 
        - up/down: 
    left trigger:
        - pressed:
        - released:
    right trigger:
        - pressed:
        - released:
    button A:
        - pressed:
        - released:
    button B:
        - pressed:
        - released:
    button X:
        - pressed:
        - released:
    button Y:
        - pressed:
        - released:
    button LB:
        - pressed:
        - released:
    button RB:
        - pressed:
        - released:
    button status:
        - pressed: 
        - released:
    button menu:
        - pressed:
        - released:
    button left joystick:
        - pressed:
        - released:
    button right joystick:
        - pressed:
        - released:
    dpad:
        - up:
        - down:
        - left:
        - right:
    xbox button:
        - pressed:
        - released:
    
    """
    
    def __init__(self):
        self._controller = Xbox360Controller(0, axis_threshold=0.2)

        # Define the default callback functions