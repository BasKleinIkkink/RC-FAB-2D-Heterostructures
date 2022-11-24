from typing import Union
from typeguard import typechecked
from ..configs.settings import Settings
import threading as tr
import multiprocessing as mp

try:
    from .base import Base, NotCalibratedError
    from .KIM101 import KIM101
except ImportError:
    from base import Base, NotCalibratedError
    from KIM101 import KIM101


class PIA13(Base):
    """Class to control a PIA13 Thorlabs piezo actuator."""

    def __init__(self, id : str, channel : int, hardware_controller : KIM101, em_event : mp.Event,
                settings : Settings) -> None:
        """
        Initialize the PIA13.
        
        Parameters
        ----------
        id: str
            The id of the hardware.
        channel: int
            The channel of the hardware.
        actuator_id: int
            The id of the actuator.
        hardware_controller: KIM101
            The hardware controller to use.
        em_event: multiprocessing.Event
            The event to use for emergency stop.
        settings: Settings
            The settings object.

        Raises
        ------
        HardwareNotConnectedError
            If the hardware is not connected.
        """
        self._id = id
        self._type = 'PIA13'
        self._channel = channel
        self._hardware_controller = hardware_controller
        self._settings = settings
        self._em_event = em_event
        self._max_speed = self._settings.get(self._type+'.'+self._id, 'max_vel')
        self._max_acceleration = self._settings.get(self._type+'.'+self._id, 'max_acc')
        self._steps_per_um = self._settings.get(self._type+'.'+self._id, 'steps_per_um')
        self._lock = tr.Lock()  # Lock for the hardware

    # ATTRIBUTES
    @property
    def device_info(self) -> dict:
        """Get the device info."""
        self._lock.acquire()
        info = {'id': self._id,
                'type': self._type,
                'channel': self._channel,
                'controller': self._hardware_controller
                }
        self._lock.release()
        return info

    @property
    def steps_per_um(self) -> None:
        """Get the steps per um."""
        # Return the steps per um
        self._lock.acquire()
        steps = self._steps_per_um
        self._lock.release()
        return steps

    @property
    def position(self) -> Union[float, int]:
        """Get the position of the hardware."""
        self._lock.acquire()
        pos = self._hardware_controller.get_position(self._channel)
        self._lock.release()
        return pos

    @property
    def speed(self) -> Union[float, int]:
        """Get the speed of the hardware."""
        self._lock.acquire()
        drive = self._hardware_controller.get_drive_parameters(self._channel)
        self._lock.release()
        return drive[3]

    @speed.setter
    def speed(self, speed : Union[float, int]) -> None:
        """
        Set the speed of the hardware.

        Speed is always in um/s.
        
        Parameters:
        -----------
        speed: float or int
            The speed to set the hardware to.
        """
        # First convert to steps/s
        if speed > self._max_speed:
            speed = self._max_speed
        speed *= self._steps_per_um
        self._lock.acquire()
        self._hardware_controller.setup_drive(channel=self._channel, velocity=speed)
        self._hardware_controller.setup_jog(channel=self._channel, velocity=speed)
        self._lock.release()

        # Also change the acceleration
        self.acceleration = speed * 4 / self._steps_per_um

    @property
    def acceleration(self) -> float:
        """
        Get the acceleration of the hardware in um/s^2.
        
        Returns
        -------
        acceleration: float
            The acceleration of the hardware.
        """
        self._lock.acquire()
        drive = self._hardware_controller.get_drive_parameters(self._channel)
        self._lock.release()
        return drive[4]

    @acceleration.setter
    def acceleration(self, acceleration : Union[float, int]) -> None:
        """
        Set the acceleration of the hardware.
        
        Parameters
        ----------
        acceleration: float or int
            The acceleration to set the hardware to. 
        """
        # First convert to steps/s^2
        if acceleration > self._max_acceleration:
            acceleration = self._max_acceleration
        acceleration *= self._steps_per_um
        self._lock.acquire()
        self._hardware_controller.setup_drive(channel=self._channel, acceleration=acceleration)
        self._hardware_controller.setup_jog(channel=self._channel, acceleration=acceleration)
        self._lock.release()

    # CONNECTION FUNCTIONS
    def connect(self) -> None:
        """Connect the hardware."""
        self._lock.acquire()
        if not self._hardware_controller._connected:
            self._hardware_controller.connect()
        else:
            pass
        self._lock.release()

    def disconnect(self) -> None:
        """Disconnect the hardware."""
        self._lock.acquire()
        if self._hardware_controller.is_connected():
            self._hardware_controller.disconnect()
        else:
            pass
        self._lock.release()

    # STATUS FUNCTIONS
    def is_connected(self) -> bool:
        """
        Check if the hardware is connected.
        
        .. warning::
            This function is mostly used as a support function for other functions,
            and does not capture the lock. This means this function is not thread safe.
        """
        state = self._hardware_controller.is_connected()
        return state

    def is_moving(self) -> bool:
        """
        Check if the hardware is moving.
        
        .. warning::
            This function is mostly used as a support function for other functions,
            and does not capture the lock. This means this function is not thread safe.
        """
        state = self._hardware_controller.is_moving(self._channel)
        return state

    def get_status(self) -> dict:
        """Get the statusreport of the hardware."""
        self._lock.acquire()
        status = {'id': self._id,
                'is_moving': self.is_moving(),
                'position': self.position,
                'speed': self.speed,
                'acceleration': self.acceleration,
                'steps_per_mm': self.steps_per_mm,
                'max_speed': self._max_speed,
                'max_acceleration': self._max_acceleration,
                }
        self._lock.release()
        return status

    # MOVEMENT FUNCTIONS
    def start_jog(self, direction : str) -> None:
        """
        Start a jog.

        Parameters
        ----------
        direction: str
            The direction to jog in (+ or -).
        """
        self._lock.acquire()
        self._hardware_controller.start_jog(self._channel, direction)
        self._lock.release()

    def stop_jog(self) -> None:
        """Stop the jog."""
        self._lock.acquire()
        self._hardware_controller.stop_jog(self._channel)
        self._lock.release()
        
    def move_by(self, distance : Union[float, int]) -> None:
        """
        Move the hardware by a certain distance.

        Parameters
        ----------
        distance: float or int
            The distance to move the hardware.
        """
        # Convert to steps
        distance *= self._steps_per_um
        self._lock.acquire()
        self._hardware_controller.move_by(self._channel, distance)
        self._lock.release()

    def move_to(self, position : Union[float, int]) -> None:
        """
        Move the hardware to a certain position.

        Parameters
        ----------
        position: float or int
            The position to move the hardware to.
        """
        # Convert to steps
        position *= self._steps_per_um
        self._lock.acquire()
        if not self._steps_calibrated:
            raise NotCalibratedError('Steps per nm were not calibrated/set.')

        self._hardware_controller.move_to(self._channel, position)
        self._lock.release()

    def emergency_stop(self) -> None:
        """Stop the hardware."""
        self._em_event.set()


if __name__ == '__main__':
    controller = KIM101()
    piezo = PIA13('X', 1, 1, controller)
    piezo.connect()
    piezo.move_by(500)