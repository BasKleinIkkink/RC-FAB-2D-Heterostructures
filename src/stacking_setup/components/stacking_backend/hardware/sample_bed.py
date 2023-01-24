from .base import Base
from .KDC101 import KDC101
import threading as tr
from .main_xy_controller import MainXYController
from ..configs.settings import Settings
from typing import Union
import multiprocessing as mp
from typing import List


class SampleBed(Base):
    """Class to control the sample bed."""

    _connected = False
    _type = "SAMPLEHOLDER"

    def __init__(
        self,
        id: str,
        base_controller: MainXYController,
        motor_controller: KDC101,
        em_event: mp.Event,
        settings: Settings,
    ) -> ...:
        """
        Initialize the sample bed.

        Parameters
        ----------
        id: str
            The id of the sample bed.
        base_controller: MainXYController
            The controller used for the vacuum and temperature.
        motor_controller: KDC101
            The controller used for the motor.
        em_event: multiprocessing.Event
            The event to use for emergency stop.
        settings: Settings
            The settings object.
        """
        self._id = id
        self._base_controller = base_controller
        self._motor_controller = motor_controller
        self._settings = settings
        self._lock = tr.Lock()
        self._em_event = em_event

        # Load some settings
        self._max_temperature = self._settings.get(
            self._type + "." + self._id, "max_temperature"
        )
        self._max_speed = self._settings.get(self._type + "." + self._id, "max_vel")
        self._max_acceleration = self._settings.get(
            self._type + "." + self._id, "max_acc"
        )

    # ATTRIBUTES
    @property
    def device_info(self) -> dict:
        """Get the device info of the sample bed."""
        return {
            "id": self._id,
            "type": self._type,
            "temp_and_vacuum_controller": self._controller.device_info,
            "motor_controller": self._motor_controller.device_info,
        }

    @property
    def position(self) -> Union[int, float]:
        """Get the position of the hardware (udeg from zero)."""
        self._lock.acquire()
        pos = self._motor_controller.get_position()
        self._lock.release()
        return pos * 10e3

    @property
    def speed(self) -> Union[float, int]:
        """Get the speed of the motor (mdeg/s)."""
        self._lock.acquire()
        speed = self._motor_controller.get_drive_parameters()[-1]
        self._lock.release()
        return speed * 10e3

    @speed.setter
    def speed(self, speed: Union[float, int]) -> None:
        """Set the speed of the motor (mdeg/s)."""
        if speed > self._max_speed:
            speed = self._max_speed
        # speed /= 10e3
        self._lock.acquire()
        self._motor_controller.setup_drive(velocity=speed)
        self._motor_controller.setup_jog(velocity=speed)
        self._lock.release()

        self.acceleration = speed * 4 * 10e3

    @property
    def acceleration(self) -> Union[float, int]:
        """Get the acceleration of the motor (mdeg/s^2)."""
        self._lock.acquire()
        acceleration = self._motor_controller.get_drive_parameters()[0]
        self._lock.release()
        return acceleration * 10e3

    @acceleration.setter
    def acceleration(self, acceleration: Union[float, int]) -> None:
        """Set the acceleration of the motor (mdeg/s^2)."""
        if acceleration > self._max_acceleration:
            acceleration = self._max_acceleration
        # acceleration /= 10e3
        self._lock.acquire()
        self._motor_controller.setup_drive(acceleration=25)
        self._motor_controller.setup_jog(acceleration=25)
        self._lock.release()

    @property
    def temperature(self) -> float:
        """Get the temperature of the sample bed (C)."""
        self._lock.acquire()
        temp = self._base_controller.temperature
        self._lock.release()
        return temp

    @property
    def target_temperature(self) -> float:
        """Get the target temperature of the sample bed."""
        self._lock.acquire()
        temp = self._base_controller.target_temperature
        self._lock.release()
        return temp

    @target_temperature.setter
    def target_temperature(self, temperature: Union[float, int]) -> ...:
        """Set the target temperature of the sample bed."""
        if temperature > self._max_temperature:
            temperature = self._max_temperature
        self._lock.acquire()
        self._base_controller.target_temperature = temperature
        self._lock.release()

    @property
    def max_temperature(self) -> float:
        """Get the maximum temperature of the sample bed."""
        return self._max_temperature

    # CONNECTION FUNCTIONS
    def connect(self) -> ...:
        """Connect the sample bed."""
        self._lock.acquire()
        if not self._base_controller.is_connected():
            self._base_controller.connect()

        if not self._motor_controller.is_connected():
            self._motor_controller.connect()
        self._lock.release()

    def disconnect(self) -> ...:
        """Disconnect the sample bed."""
        self._lock.acquire()
        if self._base_controller.is_connected():
            self._base_controller.disconnect()
        if self._motor_controller.is_connected():
            self._motor_controller.disconnect()
        self._lock.release()

    # STATUS FUNCTIONS
    def is_connected(self) -> bool:
        """Check if the sample bed is connected."""
        self._lock.acquire()
        if (
            not self._base_controller.is_connected()
            and not self._motor_controller.is_connected()
        ):
            state = False
        else:
            state = True
        self._lock.release()
        return state

    def is_heating(self) -> bool:
        """Check if the sample bed is heating."""
        self._lock.acquire()
        state = self._base_controller.is_heating()
        self._lock.release()
        return state

    def is_cooling(self) -> bool:
        """Check if the sample bed is cooling."""
        self._lock.acquire()
        state = self._base_controller.is_cooling()
        self._lock.release()
        return state

    def is_moving(self) -> bool:
        """
        Check if the piezo is moving.

        .. important::
            This function is mostly used as a support function for other functions,
            and does not capture the _lock. This means this function alone is not thread safe.

        Returns
        -------
        moving: bool
            True if the piezo is moving, False otherwise.
        """
        state = self._motor_controller.is_moving()
        return state

    def is_homed(self) -> ...:
        """
        Check if the motor is homed.

        .. important::
            This function is mostly used as a support function for other functions,
            and does not capture the _lock. This means this function alone is not thread safe.
        """
        state = self._motor_controller.is_homed()
        return state

    # MOVEMENT AND OTHER FUNCTIONS
    def toggle_vacuum_pump(self) -> ...:
        raise NotImplementedError()

    def start_jog(self, direction: str, kind: str = "continuous") -> tuple:
        """
        Start a continuous movement in a given direction.

        Parameters
        ----------
        direction: str
            The direction to move in (+ or -).
        kind: str
            The kind of movement to perform (continuous or buildin).
        """
        if self._em_event.is_set():
            return None
        self._lock.acquire()
        self._motor_controller.start_jog(direction=direction, kind=kind)
        self._lock.release()
        return 0, None

    def stop_jog(self) -> tuple:
        """Stop the continuous movement."""
        self._lock.acquire()
        self._motor_controller.stop_jog()
        self._lock.release()
        return 0, None

    def home(self, hold_until_done: bool = True) -> None:
        """
        Home the motor.

        Parameters
        ----------
        hold_until_done: bool
            If True, the function will wait until the motor is homed.
        """
        if self._em_event.is_set():
            return None
        self._lock.acquire()
        self._motor_controller.home(hold_until_done=hold_until_done)
        self._lock.release()

    def rotate_to(
        self,
        position: Union[int, float],
        hold_until_done: bool = True,
        scale: bool = True,
    ) -> None:
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
        if self._em_event.is_set():
            return None
        self._lock.acquire()
        self._motor_controller.rotate_to(
            position=position / 10e3, hold_until_done=hold_until_done, scale=scale
        )
        self._lock.release()

    def rotate_by(
        self,
        distance: Union[float, int],
        hold_until_done: bool = True,
        scale: bool = True,
    ) -> ...:
        """Move the motor by a given distance."""
        if self._em_event.is_set():
            return None
        self._lock.acquire()
        self._motor_controller.rotate_by(
            distance=distance / 10e3, hold_until_done=hold_until_done, scale=scale
        )
        self._lock.release()

    def stop(self) -> None:
        """Stop the motor."""
        self._motor_controller.stop()

    def emergency_stop(self) -> None:
        """Stop the motor."""
        self._em_event.set()
        self._motor_controller._controller.stop(immediate=True, sync=False)
        self._base_controller.emergency_stop()
