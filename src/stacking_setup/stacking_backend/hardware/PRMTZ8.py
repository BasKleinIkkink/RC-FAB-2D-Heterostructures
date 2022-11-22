from time import sleep
from typing import Union
from typeguard import typechecked
from ..configs.settings import Settings
import threading as tr
try:
    from .KDC101 import KDC101
    from .base import Base, HardwareNotConnectedError
except ImportError:
    from KDC101 import KDC101
    from base import Base, HardwareNotConnectedError



class PRMTZ8(Base):
    """Class to control communication with the PRMTZ8 piezocontroller."""
    _type = 'PRMTZ8/M'

    @typechecked
    def __init__(self, hardware_controller : KDC101, settings : Settings,
                id : str='L') -> None:
        """
        Initialize the PRMTZ8.

        .. important::
            All distances, positions and speeds are in um and um(/s)
        
        Parameters
        ----------
        hardware_controller: KDC101
            The hardware controller to use.
        id: str
            The id of the hardware.
        settings: Settings
            The settings object.

        Raises
        ------
        HardwareNotConnectedError
            If the hardware controller is not connected.
        """
        self._id = id
        self._controller = hardware_controller
        self.lock = tr.Lock()  # To ensure threadsafe serial communication
        self._settings = settings
        self._max_speed = self._settings.get(self._type+'.'+self._id, 'max_vel')
        self._max_acceleration = self._settings.get(self._type+'.'+self._id, 'max_acc')

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
        """
        Get the device info.
        
        Returns
        -------
        dict
            The device info.
        """
        self.lock.acquire()
        info = {'id' : self._id,
                'type': self._type,
                'controller': self._controller
                }
        self.lock.release()
        return info

    @property
    @typechecked
    def position(self) -> Union[int, float]:
        """
        Get the position of the hardware.
        
        All positions are given in udeg.

        Returns
        -------
        position: int or float
            The position of the hardware in udeg.
        """
        self.lock.acquire()
        pos = self._controller.get_position()
        self.lock.release()
        return pos * 10e3

    @property
    @typechecked
    def steps_per_udeg(self) -> Union[float, int]:
        """
        Return the steps per mu degree.
        
        Returns
        -------
        steps_per_udeg: int or float
            The steps per mu degree.
        """
        self.lock.acquire()
        steps = self._controller.steps_per_deg
        self.lock.release()
        return steps * 10e3

    @property
    @typechecked
    def speed(self) -> Union[float, int]:
        """
        Get the speed of the motor.
        
        The motor speed is given in udeg/s.
        
        Returns
        -------
        speed: int or float
            The speed of the motor in udeg/s.
        """
        self.lock.acquire()
        speed = self._controller.get_drive_parameters()[-1] 
        self.lock.release()
        return speed * 10e3

    @speed.setter
    @typechecked
    def speed(self, speed : Union[float, int]) -> None:
        """
        Set the speed of the motor.

        The motor speed is given in udeg/s.
        
        Parameters
        ----------
        speed: float
            The speed to set.
        """
        speed /= 10e3
        if speed > self._max_speed:
            speed = self._max_speed
        self.lock.acquire()
        self._controller.setup_drive(velocity=speed)
        self._controller.setup_jog(velocity=speed)
        self.lock.release()
        print('Speed set to {}'.format(speed))

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
        self.lock.acquire()
        acceleration = self._controller.get_drive_parameters()[0]
        self.lock.release()
        return acceleration * 10e3

    @acceleration.setter
    @typechecked
    def acceleration(self, acceleration : Union[float, int]) -> None:
        """
        Set the acceleration of the motor.

        The acceleration is given in udeg/s^2.
        
        Parameters
        ----------
        acceleration: float
            The acceleration to set.
        """
        acceleration /= 10e3
        if acceleration > self._max_acceleration:
            acceleration = self._max_acceleration
        self.lock.acquire()
        self._controller.setup_drive(acceleration=acceleration)
        self._controller.setup_jog(acceleration=acceleration)
        self.lock.release()
        print('Changed acceleration to', acceleration)

    # CONNECTION FUNCTIONS
    def connect(self) -> None:
        """Connect the PRMTZ8."""
        self.lock.acquire()
        if not self._controller.is_connected():
            self._controller.connect()
        self.lock.release()

    def disconnect(self) -> None:
        """Disconnect the PRMTZ8."""
        self.lock.acquire()
        if self._controller.is_connected():
            self._controller.disconnect()
        self.lock.release()

    # STATUS FUNCTIONS
    @typechecked
    def is_connected(self) -> bool:
        """
        Check if the PRMTZ8 is connected.

        .. important::
            This function is mostly used as a support function for other functions,
            and does not capture the lock. This means this function alone is not thread safe.
        
        Returns
        -------
        connected: bool
            True if the PRMTZ8 is connected, False otherwise.
        """
        state = self._controller.is_connected()
        return state

    @typechecked
    def is_moving(self) -> bool:	
        """
        Check if the piezo is moving.

        .. important::
            This function is mostly used as a support function for other functions,
            and does not capture the lock. This means this function alone is not thread safe.
        
        Returns
        -------
        moving: bool
            True if the piezo is moving, False otherwise.
        """
        state = self._controller.is_moving()
        return state

    @typechecked
    def get_position(self) -> Union[float, int]:	
        """
        Get the position of the piezo.
        
        Returns
        -------
        position: float
        """
        self.lock.acquire()
        pos = self._controller.get_position()
        self.lock.release()
        return pos * 10e3

    def is_homed(self) -> None:
        """
        Check if the motor is homed.
        
        .. important::
            This function is mostly used as a support function for other functions,
            and does not capture the lock. This means this function alone is not thread safe.
        """
        state = self._controller.is_homed()
        return state

    # MOVEMENT FUNCTIONS
    @typechecked
    def start_jog(self, direction : str, kind : str='continuous') -> tuple:
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
        self.lock.acquire()
        print('Starting jog')
        self._controller.start_jog(direction=direction, kind=kind)
        self.lock.release()
        return 0, None

    def stop_jog(self) -> tuple:
        """Stop the continuous movement."""
        self.lock.acquire()
        self._controller.stop_jog()
        self.lock.release()
        return 0, None

    @typechecked
    def home(self, hold_until_done : bool=True) -> None:
        """
        Home the motor.
        
        Parameters
        ----------
        hold_until_done: bool
            If True, the function will wait until the motor is homed.
        """
        self.lock.acquire()
        self._controller.home(hold_until_done=hold_until_done)
        self.lock.release()

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
        self.lock.acquire()
        self._controller.rotate_to(position=position / 10e3, hold_until_done=hold_until_done, scale=scale)
        self.lock.release()

    @typechecked
    def rotate_by(self, distance : Union[float, int], hold_until_done : bool=True, scale : bool=True) -> None:
        """Move the motor by a given distance."""
        self.lock.acquire()
        self._controller.rotate_by(distance=distance / 10e3, hold_until_done=hold_until_done, scale=scale)
        self.lock.release()

    def stop(self) -> None:
        """Stop the motor."""
        self.lock.acquire()
        self._controller.stop()
        self.lock.release()


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