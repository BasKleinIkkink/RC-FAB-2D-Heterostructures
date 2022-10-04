from KDC101 import KDC101
from exceptions import HardwareNotConnectedError
from base import Base


class PRMTZ8(Base):
    """Class to control communication with the PRMTZ8 piezocontroller."""

    def __init__(self, controller):
        """Initialize the PRMTZ8."""
        self._type = 'PRMTZ8'
        self._controller = controller

    # CONNECTION FUNCTIONS
    def connect(self):
        """Connect the PRMTZ8."""
        if not self._controller.is_connected():
            self._controller.connect()

    def disconnect(self):
        """Disconnect the PRMTZ8."""
        if self.controller.is_connected():
            self.controller.disconnect()

    # STATUS FUNCTIONS
    def is_connected(self):
        """Check if the PRMTZ8 is connected."""
        return self._controller.is_connected()

    def is_moving(self, channel):
        """Check if the piezo is moving."""
        return self._controller.is_moving()

    def get_position(self, channel):
        """Get the position of the piezo."""
        return self._controller.get_position()

    def is_homed(self):
        """Check if the motor is homed."""
        return self._controller.is_homed()

    # MOVEMENT FUNCTIONS
    def home(self, hold_until_done=True):
        """Home the motor."""
        self._controller.home(hold_until_done=hold_until_done)

    def move_to(self, position, hold_until_done=True):
        """Move the motor to a position."""
        self._controller.move_to(position=position, hold_until_done=hold_until_done)

    def move_by(self, distance, hold_until_done=True):
        """Move the motor by a given distance."""
        self._controller.move_by(distance=distance, hold_until_done=hold_until_done)

    def stop(self):
        """Stop the motor."""
        self._controller.stop()