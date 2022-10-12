from exceptions import NotSupportedError

class Base():
    """
    Base class for hardware.
    
    This class contains all the functions the main control code expects
    connecter servos/motors/actuators to have. Functions that are supported
    should be overridden in the derived class. Functions that should be supported
    by all hardware raisa NotImplementedError, optional functions raise NotSupportedError.

    Each function should return an exit code (0 for success, 1 for failure) and
    and an error message, data, or None. 
    """
    _id = None
    _type = 'HARDWARE BASE CLASS'

    # COMPONENT LIMITS
    _max_speed = None
    _max_acceleration = None
    _max_temperature = None

    # ATTRIBUTES
    @property
    def id(self):
        """Get the class identifier."""
        return self._id

    @property
    def type(self):
        """Get the type of the hardware."""
        return self._type

    @property
    def device_info(self):
        """Get the device info of the hardware."""
        raise NotImplementedError()

    # MOVEMENT ATTRIBUTES
    @property
    def steps_per_mm(self):
        """Get the steps per mm of the hardware."""
        raise NotSupportedError()

    @steps_per_mm.setter
    def steps_per_nm(self, steps_per_mm):
        """Set the steps per mm of the hardware."""
        raise NotSupportedError()

    @property
    def position(self):
        """Get the position of the hardware."""
        raise NotSupportedError()

    @property
    def speed(self):
        """Get the set speed of the hardware in nm/s."""
        raise NotSupportedError()

    @speed.setter
    def speed(self, speed):
        """Set the speed of the hardware in nm/s."""
        raise NotSupportedError()

    @property
    def max_speed(self):
        """Get the maximum speed of the hardware."""
        return self._max_speed

    @max_speed.setter
    def max_speed(self, speed):
        """Set the maximum speed of the hardware."""
        raise NotSupportedError()

    @property
    def acceleration(self):
        """Get the acceleration of the hardware."""
        raise NotSupportedError()
    
    @acceleration.setter
    def acceleration(self, acceleration):
        """Set the acceleration of the hardware."""
        raise NotSupportedError()

    @property
    def max_acceleration(self):
        """Get the maximum acceleration of the hardware."""
        return NotSupportedError()

    @max_acceleration.setter
    def max_acceleration(self, acceleration):
        """Set the maximum acceleration of the hardware."""
        raise NotSupportedError()

    # TEMPERATURE ATTRIBUTES
    @property
    def temperature(self):
        """Get the temperature of the hardware."""
        raise NotSupportedError()

    @property
    def target_temperature(self):
        """Get the target temperature of the hardware."""
        raise NotSupportedError()

    @target_temperature.setter
    def target_temperature(self, temperature):
        """Set the target temperature of the hardware."""
        raise NotSupportedError()

    @property
    def max_temperature(self):
        """Get the maximum temperature of the hardware."""
        return self._max_temperature

    @max_temperature.setter
    def max_temperature(self, temperature):
        """Set the maximum temperature of the hardware."""
        raise NotSupportedError()

    # CONNECTION FUNCTIONS
    def connect(self):
        """Connect the hardware."""
        raise NotImplementedError()

    def disconnect(self):
        """Disconnect the hardware."""
        raise NotImplementedError()

    # STATUS FUNCTIONS
    def is_connected(self):
        """Check if the hardware is connected."""
        raise NotImplementedError()

    def is_moving(self):
        """Check if the hardware is moving."""
        raise NotSupportedError()

    def is_homed(self):
        """Check if the hardware is homed."""
        raise NotSupportedError()

    def get_status(self):
        """Give a status report."""
        raise NotImplementedError()

    # HOMING FUNCTIONS
    def home(self):
        """Home the hardware."""
        raise NotSupportedError()

    # MOVING FUNCTIONS
    def start_jog(self, direction):
        """Start a jog in a direction."""
        raise NotSupportedError()

    def stop_jog(self):
        """Stop a jog."""
        raise NotSupportedError()

    def set_position(self, position):
        """Set the position of the hardware."""
        raise NotSupportedError()

    def move_to(self, position):
        """Move the hardware to a position."""
        raise NotSupportedError()

    def move_by(self, position):
        """Move the hardware by a position."""
        raise NotSupportedError()

    def set_rotation(self, rotation):
        """Set the rotation of the hardware."""
        raise NotSupportedError()

    def rotate_to(self, rotation):
        """Rotate the hardware to a position."""
        raise NotSupportedError()

    def rotate_by(self, rotation):
        """Rotate the hardware by a position."""
        raise NotSupportedError()
