from .main_xy_controller import MainXYController
from ..configs.settings import Settings
from .base import Base
from typing import Union


class BaseStepper(Base):
    """Class for the steppers in the XY base controller."""

    _type = "BASESTEPPER"

    def __init__(self, settings: Settings, controller: MainXYController, id: str):
        """Initialize the stepper."""
        self._controller = controller
        self._id = id

        self._max_speed = settings.get(self._type + "." + self._id, "max_vel")
        self._max_acceleration = settings.get(self._type + "." + self._id, "max_acc")
        self._steps_per_um = settings.get(self._type + "." + self._id, "steps_per_um")

    @property
    def steps_per_um(self) -> Union[int, float]:
        """Get the steps per um of the hardware."""
        return self._steps_per_um

    @property
    def position(self) -> int:
        """Get the position of the stepper."""
        self._lock.acquire()
        res = self._controller.position(self._id)
        self._lock.release()
        return res

    @property
    def speed(self) -> Union[int, float]:
        """Get the set speed of the hardware in um/s or deg/s."""
        self._lock.acquire()
        res = self._controller.speed
        self._lock.release()
        return res

    @speed.setter
    def speed(self, speed) -> ...:
        """Set the speed of the hardware in um/s or deg/s."""
        if speed > self._max_speed:
            speed = self._max_speed
        speed = self._convert_to_steps(speed)

        self._lock.acquire()
        self._controller._send_and_receive("ss {}".format(speed))
        self._lock.release()

        self.acceleration = 4 * self._convert_to_steps(speed)

    @property
    def acceleration(self) -> Union[int, float]:
        """Get the acceleration of the hardware."""
        self._lock.acquire()
        res = self._controller.acceleration
        self._lock.release()
        return res

    @acceleration.setter
    def acceleration(self, acceleration) -> ...:
        """Set the acceleration of the hardware."""
        if acceleration > self._max_acceleration:
            acceleration = self._max_acceleration
        acceleration = self._convert_to_steps(acceleration)

        self._lock.acquire()
        # Set acceletration and deceleration to the same value
        self._controller._send_and_receive("sa{}".format(acceleration))
        self._controller._send_and_receive("sd{}".format(acceleration))
        self._lock.release()

    def _convert_to_steps(self, value: float) -> int:
        """Convert a value from um to steps."""
        return int(self._steps_per_um * value)

    def _convert_to_um(self, value: int) -> float:
        """Convert a value from steps to um."""
        return value / self._steps_per_um
