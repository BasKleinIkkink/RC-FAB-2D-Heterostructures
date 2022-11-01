from pylablib.devices.Thorlabs.kinesis import KinesisMotor, list_kinesis_devices
from .exceptions import HardwareNotConnectedError
from typing import Union


class KDC101():
    """Class to control communication with the KCD101 motorcontroller."""

    def __init__(self, serial_nr='27263640'):
        """
        Initialize the KCD101.
        
        Parameters:
        -----------
        serial_nr : str
            The serial number of the KCD101.

        Raises:
        -------
        HardwareNotConnectedError
            If the KCD101 is not connected.
        
        """
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
    def connect(self) -> None:
        """Connect the KCD101."""
        # Device model PRM1-Z8 is used bcause the PRMTZ8/M is not officially supported by pylablib.
        self._controller = KinesisMotor(self._serial_nr, scale="PRM1-Z8")
        self._connected = True

    def disconnect(self):
        """Disconnect the KCD101."""
        self._controller.stop
        del self

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

    def setup_homing(self, velocity=None, acceleration=None):
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

    # JOG AND DRIVE PARAMETERS
    def get_drive_parameters(self, scale=True):
        return self._controller.get_velocity_parameters(scale=scale)

    def setup_drive(self, velocity=None, acceleration=None, scale=True):
        """
        Set the drive parameters of the rotation plate.
        
        The drive parameters are used for detemining the movement behavoir when moving by relative or absolute positioning.
        """
        self._controller.setup_velocity(max_velocity=velocity, acceleration=acceleration, scale=scale)
    
    def get_jog_parameters(self, scale=True):
        return self._controller.get_jog_parameters(scale=scale)

    def setup_jog(self, velocity=None, acceleration=None, scale=True):
        """
        Set the jog parameters of the rotation plate.
        
        The jog parameters are used for detemining the movement behavoir when moving by relative or absolute positioning.
        """
        self._controller.setup_jog(max_velocity=velocity, acceleration=acceleration, scale=scale)

    # MOVEMENT FUNCTIONS
    def start_jog(self, direction, kind='continuous'):
        """
        Start a jog movement.

        Parameters
        ----------
        direction : str
            The direction to move in. Can be forward=1 or + or backward=0 or -.
        kind : str
            The kind of movement. Can be 'continuous' or 'single'.
        """
        self._controller.jog(direction=direction, kind=kind)

    def stop_jog(self):
        """Stop the jog movement."""
        self._controller.stop()

    def rotate_to(self, position, hold_until_done=True, scale=True):
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
        self._controller.move_to(position=position, scale=scale)
        if hold_until_done:
            self._controller.wait_move()

    def rotate_by(self, distance, hold_until_done=True, scale=True):
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
        self._controller.move_by(distance=distance, scale=scale)
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
        self._controller.stop(immediate=True)


if __name__ == '__main__':
    from time import sleep
    # Connect to the controller.
    controller = KDC101('27263640')
    controller.connect()

    # Test drive functions.
    drive_params = controller.get_drive_parameters()
    print('original drive settings: {}'.format(drive_params))
    controller.setup_drive(max_velocity=20, max_acceleration=15)
    print('new drive settings: {}'.format(controller.get_drive_parameters()))
    controller.rotate_by(1000, scale=False)
    controller.rotate_to(25000, scale=False)

    # Reset the driving params
    controller.setup_drive(max_velocity=10, max_acceleration=10)
    print('reset drive settings: {}'.format(controller.get_drive_parameters()))

    # Test jog functions.
    jog_params = controller.get_jog_parameters()
    print('original jog settings: {}'.format(jog_params))
    controller.setup_jog(velocity=20, acceleration=20)
    print('new jog settings: {}'.format(controller.get_jog_parameters()))
    controller.start_jog('+')
    sleep(3)
    controller.stop_jog()
    controller.start_jog('-')
    sleep(3)
    controller.stop_jog()

    # Reset the jog params
    controller.setup_jog(velocity=15, acceleration=15)
    print('reset jog settings: {}'.format(controller.get_jog_parameters()))	

    controller.home()