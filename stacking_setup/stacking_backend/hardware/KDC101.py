from pylablib.devices.Thorlabs.kinesis import KinesisMotor, list_kinesis_devices
from exceptions import HardwareNotConnectedError


class KCD101():
    """Class to control communication with the KCD101 piezocontroller."""

    def __init__(self, serial_nr):
        """Initialize the KCD101."""
        self._type = 'KCD101'
        self._connected = False
        self._controller = None

        if not isinstance(serial_nr, str):
            self._serial_nr = str(serial_nr)
        else:
            self._serial_nr = serial_nr

        # Check if the controller is connected.
        connected_devices = list_kinesis_devices()
        device_found = False
        for connection in connected_devices:
            if connection[0] == self._serial_nr:
                device_found = True
                break

        if not device_found:
            print('The connected deviced: {}'.format(list_kinesis_devices()))
            raise HardwareNotConnectedError('The external controller is not connected.')

    # CONNECTION FUNCTIONS
    def connect(self):
        """Connect the KCD101."""
        self._controller = KinesisMotor(self._serial_nr, scale="stage")
        self._connected = True

    def disconnect(self):
        """Disconnect the KCD101."""
        raise NotImplementedError()

    def emergency_stop(self):
        """Stop all the connected piezos and disconnect the controller."""
        self._controller.stop()

    # STATUS FUNCTIONS
    def is_connected(self):
        """Check if the KCD101 is connected."""
        return self._connected

    def is_moving(self):
        """Check if the motor is moving."""
        return self._controller.is_moving()

    def get_position(self):
        """Get the position of the motor."""
        return self._controller.get_position()

    def is_homed(self):
        """Check if the motor is homed."""
        return self._controller.is_homed()

    def is_homing(self):
        """Check if the motor is homing."""
        return self._controller.is_homing()

    # HOMING FUNCTIONS
    def home(self, hold_until_done=True):
        """Home the motor."""
        self._controller.home()
        if hold_until_done:
            self._controller.wait_for_home()

    def get_homing_parameters(self):
        """Get the homing parameters."""
        return self._controller.get_homing_parameters()

    def set_homing_parameters(self, velocity=None, acceleration=None):
        """
        Set the homing parameters.

        If the value is None, the parameter will not be changed.

        Parameters
        ----------
        velocity : float
            The velocity to home with.
        acceleration : float
            The acceleration to home with.
        """
        self._controller.setup_homing(velocity=velocity, acceleration=acceleration)

    # MOVEMENT FUNCTIONS
    def move_to(self, position, velocity, acceleration, hold_until_done=True):
        """
        Move the piezo to the given position.

        Parameters
        ----------
        channel : int
            The channel of the piezo to move.
        position : float
            The position to move to.
        velocity : float
            The velocity to move with.
        acceleration : float
            The acceleration to move with.
        hold_until_done : bool
            If True, the function will wait until the movement is done.
        """
        self._controller.move_to(position=position, velocity=velocity, acceleration=acceleration)
        if hold_until_done:
            self._controller.wait_move()

    def move_by(self, distance, velocity, acceleration, hold_until_done=True):
        """
        Move the piezo by the given distance.

        Parameters
        ----------
        channel : int
            The channel of the piezo to move.
        distance : float
            The distance to move.
        velocity : float
            The velocity to move with.
        acceleration : float
            The acceleration to move with.
        hold_until_done : bool
            If True, the function will wait until the movement is done.
        """
        self._controller.move_by(distance=distance, velocity=velocity, acceleration=acceleration)
        if hold_until_done:
            self._controller.wait_move()

    def stop(self):
        """
        Stop the piezo.

        Parameters
        ----------
        channel : int
            The channel of the piezo to stop.
        """
        self._controller.stop()


if __name__ == '__main__':
    controller = KCD101('27263640')
    controller.connect()
    controller.move_by(5, 5, 1)