try:
    from .base import Base
except ImportError:
    from base import Base


class SampleBed(Base):
    """Class to control the sample bed."""

    def __init__(self, controller):
        """Initialize the sample bed."""
        self._id = 'sample_bed'
        self._type = 'SAMPLE BED'
        self._controller = controller

    # ATTRIBUTES
    @property
    def device_info(self):
        """Get the device info of the sample bed."""
        raise NotImplementedError()

    @property
    def temperature(self):
        """Get the temperature of the sample bed."""
        raise NotImplementedError()

    @property
    def target_temperature(self):
        """Get the target temperature of the sample bed."""
        raise NotImplementedError()

    @target_temperature.setter
    def target_temperature(self, temperature):
        """Set the target temperature of the sample bed."""
        raise NotImplementedError()

    @property
    def max_temperature(self):
        """Get the maximum temperature of the sample bed."""
        return NotImplementedError()

    @max_temperature.setter
    def max_temperature(self, temperature):
        """Set the maximum temperature of the sample bed."""
        raise NotImplementedError()

    # CONNECTION FUNCTIONS
    def connect(self):
        """Connect the sample bed."""
        if not self._controller.is_connected():
            self._controller.connect()

    def disconnect(self):
        """Disconnect the sample bed."""
        if self.controller.is_connected():
            self.controller.disconnect()

    # STATUS FUNCTIONS
    def is_connected(self):
        """Check if the sample bed is connected."""
        return self._controller.is_connected()
