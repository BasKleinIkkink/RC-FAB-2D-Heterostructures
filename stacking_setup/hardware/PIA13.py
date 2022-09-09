from pylablib.devices.Thorlabs.kinesis import KinesisPiezoMotor
from base import Base


class PIA13(Base):
    """Class to control a PIA13 Thorlabs piezo actuator."""
    _type = 'PIA13'
    _controller = 'KIM101'

    def __init__(self, id, channel):
        """
        Initialize the PIA13.
        """
        self._id = id
        self._channel = channel
        self._motor = KinesisPiezoMotor(id, channel)

    # CONNECTION FUNCTIONS
    def connect(self):
        """
        Connect the hardware.
        """
        self._motor.connect()

    def disconnect(self):
        """
        Disconnect the hardware.
        """
        self._motor.disconnect()

    # STATUS FUNCTIONS
    def is_connected(self):
        """
        Check if the hardware is connected.
        """
        return self._motor.is_connected()

    def is_moving(self):
        """
        Check if the hardware is moving.
        """
        return self._motor.is_moving()

    def _get_status(self):
        """
        Get the status of the hardware.

        Will return true if the hardware isnt busy doing something else.
        """
        if self.is_connected() and not self.is_moving():
            return True
        else:
            return False

    # MOVEMENT FUNCTIONS
    def move_by_steps(self, steps):
        """
        Move the hardware by given amount of steps.
        """
        # Check the hardware status
        if not self.is_connected():
            raise Exception('Hardware is not connected. ID {}; Type {}.'.format(self._id, self._type))
        if self.is_moving():
            raise Exception('Hardware is moving.')

        self._motor.move_by(steps)

    def move_by_distance(self, delta):
        """
        Move the hardware by a delta um.
        """
        self._motor.move_by(delta)

    def get_position(self):
        """
        Get the current position of the hardware.
        """
        return self._motor.get_position()

    def set_speed(self, speed):
        """
        Set the speed of the hardware.
        """
        self._motor.set_speed(speed)

    def get_speed(self):
        """
        Get the speed of the hardware.
        """
        return self._motor.get_speed()