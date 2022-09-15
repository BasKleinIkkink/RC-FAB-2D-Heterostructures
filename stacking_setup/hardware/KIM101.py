from pylablib.devices.Thorlabs.kinesis import KinesisPiezoMotor, list_kinesis_devices
import threading as tr
from exceptions import HardwareNotConnectedError

class KIM101Task():
    """A Task for the hardware controller to perform."""

    def __init__(self, sender, command, parameters):
        self._sender = sender
        self._task_status = False
        self._command = command
        self._parameters = parameters
        self._return_data = None

    # ATTRIBUTES
    @property
    def sender(self):
        return self._sender

    @property
    def task_status(self):
        return self._task_status

    @property
    def command(self):
        return self._command

    @property
    def parameters(self):
        return self._parameters

    @property
    def return_data(self):
        return self._return_data

    @return_data.setter
    def return_data(self, return_data):
        self._return_data = return_data

    # METHODS    
    def done(self):
        self.task_status = True


class KIM101():
    """Class to control communication with the KIM101 piezocontroller."""

    def __init__(self, serial_nr='97101742'):
        """Initialize the KIM101."""
        self._type = 'KIM101'
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
        """Connect the KIM101."""
        self._controller = KinesisPiezoMotor(self._serial_nr)

    def disconnect(self):
        """Disconnect the KIM101."""
        raise NotImplementedError()

    def emergency_stop(self):
        """Stop all the connected piezos and disconnect the controller."""
        for i in range(4):
            self._controller.stop(channel=i)

    # STATUS FUNCTIONS
    def is_connected(self):
        """Check if the KIM101 is connected."""
        if self._connected:
            return self._controller.is_connected()
        else:
            return False

    def is_moving(self, channel):
        """Check if the piezo is moving."""
        return self._controller.is_moving(channel=channel)

    def get_position(self, channel):
        """
        Get the position of the piezo.
        
        Return list of status strings, which can include ``"sw_fw_lim"`` (forward limit switch reached), ``"sw_bk_lim"`` (backward limit switch reached),
        ``"moving_fw"`` (moving forward), ``"moving_bk"`` (moving backward), ``"jogging_fw"`` (jogging forward), ``"jogging_bk"`` (jogging backward),
        ``"homing"`` (homing), ``"homed"`` (homing done), ``"tracking"``, ``"settled"``,
        ``"motion_error"`` (excessive position error), ``"current_limit"`` (motor current limit exceeded), or ``"enabled"`` (motor is enabled).
        """
        return self._controller.get_position(channel=channel)

    def get_status(self, channel):
        """Get the status of the piezo."""
        return self._controller.get_status_n(channel=channel)

    def get_parameters(self, channel):
        """
        Get the parameters of the piezo.
        
        Get current piezo-motor drive parameters ``(max_voltage, velocity, acceleration)``
        Voltage is defined in volts, velocity in steps/s, and acceleration in steps/s^2.
        """
        return self._controller.get_parameters(channel=channel)

    def _wait_move(self, channel):
        """Wait until the piezo is not moving anymore."""
        self._controller.wait_move(channel=channel)

    # JOG AND DRIVE PARAMETERS
    def setup_jog(self, channel, velocity=None, acceleration=None):
        """Set the jog paramters of the piezo."""
        self._controller.setup_jog(velocity=velocity, acceleration=acceleration, channel=channel)

    def get_jog_parameters(self, channel):
        """Get the jog parameters of the piezo."""
        return self._controller.get_jog_parameters(channel=channel)

    def setup_drive(self, channel, max_voltage=None, velocity=None, acceleration=None):
        """
        Set the drive parameters of the piezo.
        
        The drive parameters are used for detemining the movement behavoir when moving by relative or absolute positioning.
        """
        self._controller.setup_drive(max_voltage=max_voltage, velocity=velocity, acceleration=acceleration, channel=channel)
    
    def get_drive_parameters(self, channel):
        """
        Get the drive parameters of the piezo.
        
        The drive parameters are used for detemining the movement behavoir when moving by relative or absolute positioning.
        """
        return self._controller.get_drive_parameters(channel=channel)

    # MOVEMENT FUNCTIONS
    def start_jog(self, channel, direction, kind='buildin'):
        """
        Start a jog.
        
        ATTENTION: The jog has to be terminated by the stop method.

        If ``kind=="continuous"``, simply start motion in the given direction at the standard jog speed
        until either the motor is stopped explicitly, or the limit is reached.
        If ``kind=="builtin"``, use the built-in jog command, whose parameters are specified by :meth:`get_jog_parameters`.
        Note that ``kind=="continuous"`` is still implemented through the builtin jog, so it changes its parameters;
        hence, afterwards the jog parameters need to be manually restored.
        """
        self._controller.jog(direction=direction, kind=kind, channel=channel)

    def move_to(self, channel, position):
        """
        Move one of the connected piezos.
        
        Position is the distance in steps from the zero point (home).

        Parameters
        ----------
        channel : int
            The channel of the piezo to move.
        position : int
            The position to move to (in steps).

        Returns
        -------
        None

        """
        self._controller.move_to(position=position, channel=channel)
        self._wait_move(channel=channel)

    def move_by(self, channel, distance):
        """
        Move one of the connected piezos.
        
        Distance is the distance in steps to move.
        
        Parameters
        ----------
        channel : int
            The channel of the piezo to move.
        distance : int
            The distance to move (in steps).

        Returns
        -------
        None
        """
        self._controller.move_by(distance=distance, channel=channel)
        self._wait_move(channel=channel)

    def stop(self, channel):
        """Stop one of the connected piezos."""
        self._controller.stop(channel=channel)

    

if __name__ == '__main__':
    controller = KIM101()
    controller.connect()
    controller.move_by(1, 1500)
    controller.move_by(2, 1500)
    controller.move_by(3, 1500)