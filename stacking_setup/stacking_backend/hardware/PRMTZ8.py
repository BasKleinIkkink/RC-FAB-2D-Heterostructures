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
    def start_jog(self, direction, kind='continuous'):
        """Start a continuous movement in a given direction."""
        self._controller.start_jog(direction=direction, kind=kind)

    def stop_jog(self):
        """Stop the continuous movement."""
        self._controller.stop_jog()

    def home(self, hold_until_done=True):
        """Home the motor."""
        self._controller.home(hold_until_done=hold_until_done)

    def rotate_to(self, position, hold_until_done=True):
        """Move the motor to a position."""
        self._controller.rotate_to(position=position, hold_until_done=hold_until_done)

    def rotate_by(self, distance, hold_until_done=True):
        """Move the motor by a given distance."""
        self._controller.rotate_by(distance=distance, hold_until_done=hold_until_done)

    def stop(self):
        """Stop the motor."""
        self._controller.stop()


if __name__ == '__main__':
    from time import sleep
    controller = KDC101(serial_nr='27263640')
    rot = PRMTZ8(controller=controller)
    
    # Test drive functions.
    drive_params = rot.get_drive_parameters()
    print('original drive settings: {}'.format(drive_params))
    rot.setup_drive(max_velocity=20, max_acceleration=15)
    print('new drive settings: {}'.format(rot.get_drive_parameters()))
    rot.rotate_by(1000, scale=False)
    rot.rotate_to(25000, scale=False)

    # Reset the driving params
    rot.setup_drive(max_velocity=10, max_acceleration=10)
    print('reset drive settings: {}'.format(rot.get_drive_parameters()))

    # Test jog functions.
    jog_params = rot.get_jog_parameters()
    print('original jog settings: {}'.format(jog_params))
    rot.setup_jog(velocity=20, acceleration=20)
    print('new jog settings: {}'.format(rot.get_jog_parameters()))
    rot.start_jog('+')
    sleep(3)
    rot.stop_jog()
    rot.start_jog('-')
    sleep(3)
    rot.stop_jog()

    # Reset the jog params
    rot.setup_jog(velocity=15, acceleration=15)
    print('reset jog settings: {}'.format(rot.get_jog_parameters()))	

    rot.home()