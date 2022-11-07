from time import sleep
from typing import Union
from typeguard import typechecked

try:
    from .KDC101 import KDC101
    from .base import Base, HardwareNotConnectedError
except ImportError:
    from KDC101 import KDC101
    from base import Base, HardwareNotConnectedError



class PRMTZ8(Base):
    """Class to control communication with the PRMTZ8 piezocontroller."""

    @typechecked
    def __init__(self, hardware_controller : KDC101 , id : str='L') -> None:
        """
        Initialize the PRMTZ8.
        
        Parameters
        ----------
        hardware_controller: KDC101
            The hardware controller to use.
        id: str
            The id of the hardware.

        Raises
        ------
        HardwareNotConnectedError
            If the hardware controller is not connected.
        """
        self._type = 'PRMTZ8'
        self._id = id
        self._controller = hardware_controller

        # Check if the controller is connected.
        if not self._controller.is_connected():
            # Try to connect
            self._controller.connect()
            sleep(0.5)

        if not self._controller.is_connected():
            raise HardwareNotConnectedError('The external controller is not connected.')

    # ATTRIBUTES
    @property
    @typechecked
    def device_info(self) -> dict:
        """Get the device info."""
        return {'id' : self._id,
                'type': self._type,
                'controller': self._controller
                }

    @property
    @typechecked
    def position(self) -> None:
        """Get the position of the hardware."""
        return self._controller.get_position()

    @property
    @typechecked
    def steps_per_deg(self) -> Union[float, int]:
        """Return the steps per degree."""
        return self._steps_per_deg

    @property
    @typechecked
    def speed(self) -> Union[float, int]:
        return self._controller.get_drive_parameters()[-1]

    @speed.setter
    @typechecked
    def speed(self, speed : Union[float, int]) -> None:
        """
        Set the speed of the motor.
        
        Parameters
        ----------
        speed: float
            The speed to set.
        """
        self._controller.setup_drive(velocity=speed)

    @property
    @typechecked
    def acceleration(self) -> Union[float, int]:
        """
        Get the acceleration of the motor.
        
        Returns
        -------
        acceleration: float
            The acceleration of the motor.
        """
        return self._controller.get_drive_parameters()[1]

    @acceleration.setter
    @typechecked
    def acceleration(self, acceleration : Union[float, int]) -> None:
        """
        Set the acceleration of the motor.
        
        Parameters
        ----------
        acceleration: float
            The acceleration to set.
        """
        self._controller.setup_drive(acceleration=acceleration)

    # CONNECTION FUNCTIONS
    def connect(self) -> None:
        """Connect the PRMTZ8."""
        if not self._controller.is_connected():
            self._controller.connect()

    def disconnect(self) -> None:
        """Disconnect the PRMTZ8."""
        if self._controller.is_connected():
            self._controller.disconnect()

    # STATUS FUNCTIONS
    @typechecked
    def is_connected(self) -> bool:
        """
        Check if the PRMTZ8 is connected.
        
        Returns
        -------
        connected: bool
            True if the PRMTZ8 is connected, False otherwise.
        """
        return self._controller.is_connected()

    @typechecked
    def is_moving(self) -> bool:	
        """
        Check if the piezo is moving.
        
        Returns
        -------
        moving: bool
            True if the piezo is moving, False otherwise.
        """
        return self._controller.is_moving()

    @typechecked
    def get_position(self) -> Union[float, int]:	
        """
        Get the position of the piezo.
        
        Returns
        -------
        position: float
        """
        return self._controller.get_position()

    def is_homed(self) -> None:
        """Check if the motor is homed."""
        return self._controller.is_homed()

    # MOVEMENT FUNCTIONS
    @typechecked
    def start_jog(self, direction : str, kind : str='continuous') -> None:
        """
        Start a continuous movement in a given direction.
        
        Parameters
        ----------
        direction: str
            The direction to move in (+ or -).
        kind: str
            The kind of movement to perform (continuous or buildin).
        """
        # Set the jogging parameters to the current driving parameters.
        self._controller.setup_jog(acceleration=self.acceleration, velocity=self.speed)
        self._controller.start_jog(direction=direction, kind=kind)

    def stop_jog(self) -> None:
        """Stop the continuous movement."""
        self._controller.stop_jog()

    @typechecked
    def home(self, hold_until_done : bool=True) -> None:
        """
        Home the motor.
        
        Parameters
        ----------
        hold_until_done: bool
            If True, the function will wait until the motor is homed.
        """
        self._controller.home(hold_until_done=hold_until_done)

    @typechecked
    def rotate_to(self, position : Union[int, float], hold_until_done : bool=True, scale: bool=True) -> None:
        """
        Move the motor to a position.
        
        Parameters
        ----------
        position: float
            The position to move to.
        hold_until_done: bool
            If True, the function will wait until the motor is done moving.
        scale: bool
            If True, the position will be scaled to the steps per degree.
        """
        self._controller.rotate_to(position=position, hold_until_done=hold_until_done, scale=scale)

    @typechecked
    def rotate_by(self, distance : Union[float, int], hold_until_done : bool=True, scale : bool=True) -> None:
        """Move the motor by a given distance."""
        self._controller.rotate_by(distance=distance, hold_until_done=hold_until_done, scale=scale)

    def stop(self) -> None:
        """Stop the motor."""
        self._controller.stop()


if __name__ == '__main__':
    from time import sleep
    controller = KDC101(serial_nr='27263640')
    rot = PRMTZ8(id='L', hardware_controller=controller)
    
    # Test drive functions.
    drive_params = [rot.speed, rot.acceleration]
    print('original drive settings: {}'.format(drive_params))
    rot.speed = 20
    rot.acceleration = 15
    print('new drive settings: {}'.format([rot.speed, rot.acceleration]))
    rot.rotate_by(25000, scale=False)
    rot.rotate_to(1000, scale=False)

    # Reset the driving params
    rot.speed = 10
    rot.acceleration = 10
    print('reset drive settings: {}'.format([rot.speed, rot.acceleration]))

    # Test jog functions.
    rot.start_jog('-')
    sleep(5)
    rot.stop_jog()
    print('Done with jog test.')

    # Home the stage
    rot.home()
    print('Done homing')