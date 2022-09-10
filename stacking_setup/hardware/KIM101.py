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

    def __init__(self):
        """Initialize the KIM101."""
        self._type = 'KIM101'

        # Check if the controller is connected.
        if self._external_controller not in list_kinesis_devices():
            raise HardwareNotConnectedError('The external controller is not connected.')

    # CONNECTION FUNCTIONS
    def connect(self):
        """Connect the KIM101."""
        self._controller = KinesisPiezoMotor(id, self._channel)

    def disconnect(self):
        """Disconnect the KIM101."""
        raise NotImplementedError()

    # STATUS FUNCTIONS
    def is_connected(self):
        """Check if the KIM101 is connected."""
        return self._controller.is_connected()

    def is_moving(self, channel):
        """Check if the piezo is moving."""
        return self._controller.is_moving(channel=channel)

    def get_position(self, channel):
        """Get the position of the piezo."""
        return self._controller.get_position(channel=channel)

    def get_status(self, channel):
        """Get the status of the piezo."""
        return self._controller.get_status_n(channel=channel)

    # PARAMETER FUNCTIONS
    # JOG setting (self, mode=None, step_size_fw=None, step_size_bk=None, velocity=None, acceleration=None, channel=None
    def set_speed(self, channel, speed):
        """Set the speed of the piezo."""
        raise NotImplementedError()

    # MOVEMENT FUNCTIONS
    def move_to(self, channel, position):
        """Move one of the connected piezos."""
        self._controller.move_to(position=position, channel=channel)

    def move_by(self, channel, distance):
        """Move one of the connected piezos."""
        self._controller.move_by(distance=distance, channel=channel)

    def stop(self, channel):
        """Stop one of the connected piezos."""
        self._controller.stop(channel=channel)

    
