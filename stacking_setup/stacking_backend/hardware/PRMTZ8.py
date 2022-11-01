from .KDC101 import KDC101
from .exceptions import HardwareNotConnectedError
from .base import Base
from time import sleep


class PRMTZ8(Base):
    """Class to control communication with the PRMTZ8 piezocontroller."""

    def __init__(self, hardware_controller, id='L'):
        """Initialize the PRMTZ8."""
        self._type = 'PRMTZ8'
        self._id = id
        self._controller = hardware_controller

        # Check if the controller is connected.
        if not self._controller.is_connected():
            # Try to connect
            self._controller.connect()
            sleep(0.5)

        if not self._controller.is_connected():
            raise HardwareNotConnectedError('The external controller is not connected.')

    # ATTRIBUTES
    @property
    def device_info(self):
        return {'id' : self._id,
                'type': self._type,
                'controller': self._controller
                }

    @property
    def position(self):
        """Get the position of the hardware."""
        return self._controller.get_position()

    @property
    def steps_per_deg(self):
        """Return the steps per degree."""
        return self._steps_per_deg

    @property
    def speed(self):
        return self._controller.get_drive_parameters()[-1]

    @speed.setter
    def speed(self, speed):
        """Set the speed of the motor."""
        self._controller.setup_drive(velocity=speed)

    @property
    def acceleration(self):
        return self._controller.get_drive_parameters()[1]

    @acceleration.setter
    def acceleration(self, acceleration):
        """Set the acceleration of the motor."""
        self._controller.setup_drive(acceleration=acceleration)

    # CONNECTION FUNCTIONS
    def connect(self):
        """Connect the PRMTZ8."""
        if not self._controller.is_connected():
            self._controller.connect()

    def disconnect(self):
        """Disconnect the PRMTZ8."""
        if self._controller.is_connected():
            self._controller.disconnect()

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
        # Set the jogging parameters to the current driving parameters.
        self._controller.setup_jog(acceleration=self.acceleration, velocity=self.speed)
        self._controller.start_jog(direction=direction, kind=kind)

    def stop_jog(self):
        """Stop the continuous movement."""
        self._controller.stop_jog()

    def home(self, hold_until_done=True):
        """Home the motor."""
        self._controller.home(hold_until_done=hold_until_done)

    def rotate_to(self, position, hold_until_done=True, scale=True):
        """Move the motor to a position."""
        self._controller.rotate_to(position=position, hold_until_done=hold_until_done, scale=scale)

    def rotate_by(self, distance, hold_until_done=True, scale=True):
        """Move the motor by a given distance."""
        self._controller.rotate_by(distance=distance, hold_until_done=hold_until_done, scale=scale)

    def stop(self):
        """Stop the motor."""
        self._controller.stop()


if __name__ == '__main__':
    from time import sleep
    controller = KDC101(serial_nr='27263640')
    rot = PRMTZ8(id='L', hardware_controller=controller)
    
    """
    # Test drive functions.
    drive_params = [rot.speed, rot.acceleration]
    print('original drive settings: {}'.format(drive_params))
    rot.speed = 20
    rot.acceleration = 15
    print('new drive settings: {}'.format([rot.speed, rot.acceleration]))
    rot.rotate_by(25000, scale=False)
    rot.rotate_to(1000, scale=False)

    # Reset the driving params
    rot.speed = 10
    rot.acceleration = 10
    print('reset drive settings: {}'.format([rot.speed, rot.acceleration]))

    # Test jog functions.
    rot.start_jog('-')
    sleep(5)
    rot.stop_jog()
    print('Done with jog test.')
    """

    # Home the stage
    rot.home()
    print('Done homing')