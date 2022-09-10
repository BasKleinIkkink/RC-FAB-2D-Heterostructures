
from selectors import EpollSelector
from base import Base
from exceptions import HardwareNotConnectedError


class PIA13(Base):
    """Class to control a PIA13 Thorlabs piezo actuator."""
    _type = 'PIA13'

    def __init__(self, id, channel, actuator_id, hardware_controller):
        """
        Initialize the PIA13.
        """
        self._id = id
        self._channel = channel
        self._hardware_controller = hardware_controller
        self._actuator_id = actuator_id

    # ATTRIBUTES
    @property
    def steps_per_mm(self):
        # Get the jog settings from the hardware controller.
        # Return the steps per nm
        raise NotImplementedError()

    @steps_per_mm.setter
    def steps_per_mm(self, steps_per_mm):
        # Set the jog settings on the hardware controller.
        return self._hardware_controller.set_steps_per_nm(self._channel, 
                                                        steps_per_mm)

    @property
    def position(self):
        """Get the position of the hardware."""
        return self._hardware_controller.get_position(self._channel)

    @property
    def speed(self):
        """Get the speed of the hardware."""
        return self._hardware_controller.get_speed(self._channel)

    @speed.setter
    def speed(self, speed):
        """Set the speed of the hardware."""
        self._hardware_controller.set_speed(self._channel, speed)

    # CONNECTION FUNCTIONS
    def connect(self):
        """Connect the hardware."""
        if not self._hardware_controller.is_connected():
            self._hardware_controller.connect()
        else:
            pass

    def disconnect(self):
        """Disconnect the hardware."""
        if self._hardware_controller.is_connected():
            self._hardware_controller.disconnect()
        else:
            pass

    # STATUS FUNCTIONS
    def is_connected(self):
        """Check if the hardware is connected."""
        return self._hardware_controller.is_connected()

    def get_status(self):
        """Get the statusreport of the hardware."""
        return self._hardware_controller.get_status(self._channel)

    def is_moving(self):
        """Check if the hardware is moving."""
        return self._hardware_controller.is_moving(self._channel)

    # MOVEMENT FUNCTIONS
    def move_by(self, distance):
        """
        Move the hardware by a certain distance.

        Parameters:
        -----------
        distance: float or int
            The distance to move the hardware.
        """
        self._hardware_controller.move_by(self._channel, distance)

    def move_to(self, position):
        """
        Move the hardware to a certain position.

        Parameters:
        ----------
        position: float or int
            The position to move the hardware to.
        """
        self._hardware_controller.move_to(self._channel, position)

    def stop(self):
        """Stop the hardware."""
        self._hardware_controller.stop(self._channel)
