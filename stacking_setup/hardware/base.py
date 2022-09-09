

class Base():
    """
    Base class for hardware.
    
    This class contains all the functions the main control code expects
    connecter servos/motors/actuators to have. Functions that are supported
    should be overridden in the derived class.

    Each function should return an exit code (0 for success, 1 for failure) and
    and an error message, data, or None. 
    """
    _id = None
    _type = None
    _steps_per_mm = None

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
    def steps_per_mm(self):
        """Get the steps per mm of the hardware."""
        return self._steps_per_mm

    @steps_per_mm.setter
    def steps_per_nm(self, steps_per_mm):
        """
        Set the steps per mm of the hardware.
        """
        raise NotImplementedError()

    @property
    def position(self):
        """
        Get the position of the hardware.
        """
        raise NotImplementedError()

    @property
    def speed(self):
        """
        Get the set speed of the hardware in nm/s.
        """
        raise NotImplementedError()

    @speed.setter
    def speed(self, speed):
        """
        Set the speed of the hardware in nm/s.
        """
        raise NotImplementedError()

    # CONNECTION FUNCTIONS
    def connect(self):
        """
        Connect the hardware.
        """
        raise NotImplementedError()

    def disconnect(self):
        """
        Disconnect the hardware.
        """
        raise NotImplementedError()

    def emergency_stop(self):
        """
        Emergency stop the hardware.
        """
        raise NotImplementedError()

    # STATUS FUNCTIONS
    def is_connected(self):
        """
        Check if the hardware is connected.
        """
        raise NotImplementedError()

    def is_moving(self):
        """
        Check if the hardware is moving.
        """
        raise NotImplementedError()

    def is_homed(self):
        """
        Check if the hardware is homed.
        """
        raise NotImplementedError()

    def get_status(self):
        """
        Get the status of the hardware.
        """
        raise NotImplementedError()

    # HOMING FUNCTIONS
    def home(self):
        """
        Home the hardware.
        """
        raise NotImplementedError()

    # MOVING FUNCTIONS
    def set_position(self, position):
        """
        Set the position of the hardware.
        """
        raise NotImplementedError()

    def move_to(self, position):
        """
        Move the hardware to a position.
        """
        raise NotImplementedError()

    def move_by(self, position):
        """
        Move the hardware by a position.
        """
        raise NotImplementedError()