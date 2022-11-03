from xbox360controller import Xbox360Controller
import signal


class CustomXbox360Controller:
    """
    Class to make the configuring and usinf of the controller easier.

    The class is a wrapper around the xbox360controller library.

    IMPORTANT: There are a few important things to know about the control 
    with the Xbox controller:
        - When the mask an microscope stages are synced (see status button)
        the microscope z control and mask z control will behave the same way
        (lifting mask will also lift the microscope stage). This also means that
        if one of both is locked, the other will also not move, even if unlocked

        - When saving the instrument state all axis positions will also be saved.
        It is important to know that the PIA13 actuators in the mask are not
        calibrated for absolute positioning. This means that if the mask is
        moved to a saved position there is no guarantee that the mask will be
        in the same position as when the state was saved.

    Default controll layout:
    ------------------------
    left joystick:
        - left/right: Move the mask stage left/right
        - up/down: move Move the mask stage forward/backward
    right joystick:
        - left/right: Move the base stage left/right
        - up/down: Move the base stage forward/backward
    button left joystick:
        - pressed: Toggle lock mask stage movement
        - released: pass
    button right joystick:
        - pressed: Toggle lock base stage movement
        - released: pass
    left trigger:
        - pressed: Lower the set axis (see button Y)
        - released: pass
    right trigger:
        - pressed: Raise the set axis (see button Y)
        - released: pass
    button A:
        - pressed:
        - released:
    button B:
        - pressed: Rotate sample right
        - released: pass
    button X:
        - pressed: Rotate sample left
        - released: pass
    button Y:
        - pressed: Toggle triggers between microscope and mask z axis
        - released: pass
    button LB:
        - pressed: Decrease speed of all stages
        - released: pass
    button RB:
        - pressed: Increase speed of all stages
        - released: pass
    button status:
        - pressed: Toggle sync mask and microscope z axis
        - released: pass
    button menu:
        - pressed: Save instrument state
        - released: pass
    dpad:
        - up:
        - down:
        - left:
        - right:
    xbox button:
        - pressed: Stop all movement
        - released: pass
    
    """
    
    def __init__(self):
        self._controller = Xbox360Controller(0, axis_threshold=0.2)

        # Define the default callback functions
        pass