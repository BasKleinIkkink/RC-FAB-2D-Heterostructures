from .base import Base


class TangoDesktop(Base):
    """
    Class for TangoDesktop hardware.

    IMPORTANT: This class is

    Communication interface:
    ------------------------
    All TANGO controllers communicate via a serial COM port interface, independent
    of the controller type (RS232C, USB, PCI, PCI-E). The default setting is
    57600,8,2,N.

    Instruction syntax:
    -------------------
    The instructions and parameters are sent as cleartext ASCII strings with a
    terminating carriage return [CR], which is 0x0d hex. Characters may be upper-,
    lower- or camel-case. The parameters are separated by a space character.
    This provides easy access to all functions by using a simple terminal program
    such as HyperTerminal. A typical instruction syntax is as follows: 

    [!,?][instruction][SP][optional axis] [parameter1][SP][parameter2] [etc…] [CR]

    A read instruction may return more than one parameter. In many cases the number
    of returned parameters depends on the amount of available axes:

    [axis X] [if available: axis Y] [if available: axis Z] [if available: axis A]

    """
    _id = None
    _type = "TANGO DESKTOP"

    def __init__(self):
        # Check if the tango desktop is connected

        # Check the serial number of the tango desktop
        pass

    # ATTRIBUTES
    @property
    def steps_per_um(self):
        # Unit is set on the contorller as steps per mm
        pass

    @property
    def position(self):
        # The position is given in mm
        pass

    @property
    def speed(self):
        # The speed is given in mm/s
        pass

    @speed.setter
    def speed(self, speed):
        # Speed should be converted to mm/s before sending
        pass

    @property
    def acceleration(self):
        pass

    @acceleration.setter
    def acceleration(self, acceleration):
        pass

    # CONNECTION FUNCTIONS
    def connect(self):
        # Connect the tango desktop

        # Activate extended mode

        pass

    def disconnect(self):
        # Make sure nothing is moving

        # Disconnect the tango desktop

        pass

    # STATUS FUNCTIONS
    def is_connected(self):
        # Check if the tango desktop is connected
        pass

    def is_moving(self):
        # Check if the tango desktop is moving
        pass

    def is_homed(self):
        # Check if the tango desktop is homed
        pass

    def is_homing(self):
        # Check if the tango desktop is homing
        pass

    # HOMING FUNCTIONS
    def home(self):
        # Home the tango desktop
        pass

    # MOVEMENT FUNCTIONS
    def start_jog(self, direction):
        # Start a jog movement in the given direction
        pass

    def stop_jog(self):
        # Stop a jog movement
        pass

    def move_to(self, position):
        # Move to the given position
        pass

    def move_by(self, distance):
        # Move by the given distance
        pass
