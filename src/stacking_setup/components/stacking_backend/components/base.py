from typing import Union
from ..exceptions import NotSupportedError


class Base:
    """
    Base class for abstraction layer between the backend and the controller.

    This class is used to create an interface between the backend and the
    controller used to control physical hardware. The backend expects the
    controller to have certain functions, which are defined in this class.
    By inheriting from this class, the controller can be used with the backend.

    Functions that are supported should be overridden in the derived class. 
    Functions that should be supported by all 
    hardware raise a :class:`NotImplementedError`, optional functions raise 
    :class:`NotSupportedError`. The :class:`NotSupportedError` is always caught 
    by the :class:`StackingSetupBackend` class, so it is safe to raise.

    """

    _id = None
    _type = "HARDWARE BASE CLASS"

    def __init__(self, id: str) -> ...:
        """
        Initialize the component.
        
        Parameters
        ----------
        id: str
            The axis id of the hardware. This should be unique for each component.
        """
        self._id = id

    # ATTRIBUTES
    @property
    def id(self) -> str:
        """Get the class identifier."""
        return self._id

    @property
    def type(self) -> str:
        """
        Get the type of the hardware.
        
        Used as an easier alternative for the user to identify the hardware.
        """
        return self._type

    @property
    def device_info(self) -> dict:
        """
        Get the device info.
        
        Returns a dictionary containing at least the device id, type
        and controller type. Optional information can be added by the
        user as long as the keys are unique strings and the values are
        Pickle serializable (object cannot contain any code based on
        c-types).
        """
        raise NotImplementedError()

    # STEP ATTRIBUTES
    # The component can either support steps/um or steps/deg, not both.
    @property
    def steps_per_um(self) -> Union[float, int]:
        """Get the steps per um of the hardware."""
        raise NotSupportedError()

    @property
    def steps_per_deg(self):
        """Get the steps per udegree of the hardware."""
        raise NotSupportedError()

    # MOVEMENT PROFILE ATTRIBUTES
    @property
    def position(self) -> Union[float, int]:
        """Get the position of the hardware."""
        raise NotSupportedError()

    @property
    def speed(self) -> Union[float, int]:
        """Get the set speed of the hardware in um/s or deg/s."""
        raise NotSupportedError()

    @speed.setter
    def speed(self, speed: Union[float, int]) -> ...:
        """Set the speed of the hardware in um/s or deg/s."""
        raise NotSupportedError()

    @property
    def acceleration(self) -> Union[float, int]:
        """Get the acceleration of the hardware."""
        raise NotSupportedError()

    @acceleration.setter
    def acceleration(self, acceleration: Union[float, int]) -> ...:
        """Set the acceleration of the hardware."""
        raise NotSupportedError()

    # TEMPERATURE ATTRIBUTES
    @property
    def temperature(self) -> Union[float, int]:
        """Get the temperature of the hardware."""
        raise NotSupportedError()

    @property
    def target_temperature(self) -> Union[float, int]:
        """Get the target temperature of the hardware."""
        raise NotSupportedError()

    @target_temperature.setter
    def target_temperature(self, temperature: Union[float, int]) -> ...:
        """Set the target temperature of the hardware."""
        raise NotSupportedError()

    # CONNECTION FUNCTIONS
    def connect(self) -> ...:
        """Connect the hardware."""
        raise NotImplementedError()

    def disconnect(self) -> ...:
        """Disconnect the hardware."""
        raise NotImplementedError()

    # STATUS FUNCTIONS
    def is_connected(self) -> bool:
        """Check if the hardware is connected."""
        raise NotImplementedError()

    def is_moving(self) -> bool:
        """Check if the hardware is moving."""
        raise NotSupportedError()

    def is_homed(self) -> bool:
        """Check if the hardware is homed."""
        raise NotSupportedError()

    # HOMING FUNCTIONS
    def home(self) -> ...:
        """Home the hardware."""
        raise NotSupportedError()

    # MOVING FUNCTIONS
    def start_jog(self, direction: str) -> ...:
        """
        Start a jog in a direction.
        
        Parameters
        ----------
        direction: str
            The direction to jog in. Can be either "+" or "-".
        """
        raise NotSupportedError()

    def stop_jog(self) -> ...:
        """Stop a jog."""
        raise NotSupportedError()

    def move_to(self, position: Union[float, int]) -> ...:
        """
        Move the hardware to a position.
        
        Parameters
        ----------
        position: float or int
            The position to move to in um from the home position.
        """
        raise NotSupportedError()

    def move_by(self, position: Union[float, int]) -> ...:
        """
        Move the hardware by a position.
        
        Parameters
        ----------
        position: float or int
            The position to move by in um from the current position.
        """
        raise NotSupportedError()

    def rotate_to(self, rotation: Union[float, int]) -> ...:
        """
        Rotate the hardware to a position.
        
        Parameters
        ----------
        rotation: float or int
            The rotation to move to in udegrees from the home position.
        """
        raise NotSupportedError()

    def rotate_by(self, rotation: Union[float, int]) -> ...:
        """
        Rotate the hardware by a position.
        
        Parameters
        ----------
        rotation: float or int
            The rotation to move by in udegrees from the current position.
        """
        raise NotSupportedError()

    def stop(self):
        """
        Unconditionally stop the hardware.
        
        This method is different from the emergency_stop method, as it does not stop
        all the other hardware.
        It should call the thread safe stop function of the used controller. This method
        also does not disable any follow up calls to the controller.
        """
        raise NotImplementedError()

    def emergency_stop(self):
        """
        Unconditionally stop all the connected hardware.
        
        Should call the non-blocking, non thread-safe stop function of the used controller.
        Make sure to use a non thread safe method to stop the hardware, otherwise the
        hardware might not stop and wait for the move to finish. Calling this method
        might crash some controllers and the system should be restarted after calling
        this method.
        """
        raise NotImplementedError()

    def toggle_vacuum(self, state):
        """Toggle the vacuum on/off."""
        raise NotSupportedError()

    def toggle_temp_control(self, state):
        """Toggle the temperature control on/off."""
        raise NotSupportedError()
