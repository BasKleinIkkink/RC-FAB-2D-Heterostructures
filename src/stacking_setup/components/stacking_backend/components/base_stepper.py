from ..controllers.main_xy_controller import MainXYController
from ..configs.settings import Settings
from .base import Base
from typing import Union
import multiprocessing as mp
import threading as tr


class BaseStepper(Base):
    """Class for the steppers in the XY base controller."""

    _type = "BASESTEPPER"

    def __init__(self, settings: Settings, controller: MainXYController, id: str, em_event : mp.Event):
        """Initialize the stepper."""
        self._controller = controller
        self._id = id
        self._em_event = em_event

        self._max_speed = settings.get(self._type + "." + self._id, "max_vel")
        self._steps_per_um = settings.get(self._type + "." + self._id, "steps_per_um")
        self._lock = tr.Lock()

    # Attributes
    @property
    def position(self) -> int:
        """Get the position of the stepper."""
        self._lock.acquire()
        res = self._controller.get_position(self._id)
        self._lock.release()
        return self._convert_to_um(int(res))

    @property
    def speed(self) -> Union[int, float]:
        """Get the set speed of the hardware in um/s or deg/s."""
        self._lock.acquire()
        res = self._controller.speed
        self._lock.release()
        return self._convert_to_um(float(res))

    @speed.setter
    def speed(self, speed) -> ...:
        """Set the speed of the hardware in um/s or deg/s."""
        if speed > self._max_speed:
            speed = self._max_speed
        speed = self._convert_to_steps(speed)

        self._lock.acquire()
        self._controller._send_and_receive("ssx{}".format(speed))
        self._controller._send_and_receive("ssy{}".format(speed))
        self._lock.release()

    @property
    def acceleration(self) -> Union[int, float]:
        """Get the acceleration of the hardware."""
        self._lock.acquire()
        res = self._controller.acceleration
        self._lock.release()
        return res

    # CONNECTION METHODS
    @property
    def is_connected(self) -> bool:
        """Get the connection status of the stepper."""
        return self._controller.is_connected

    def connect(self) -> ...:
        """Connect the stepper."""
        self._lock.acquire()
        self._controller.connect()
        self._lock.release()

    def disconnect(self) -> ...:
        """Disconnect the stepper."""
        self._lock.acquire()
        self._controller.disconnect()
        self._lock.release()

    # METHODS
    def home(self):
        """Home the stepper."""
        self._lock.acquire()
        self._controller.home()
        self._lock.release()

    def move_by(self, distance: float, convert=True) -> ...:
        """Move the stepper by a certain distance."""
        if convert:
            distance = self._convert_to_steps(distance)

        self._lock.acquire()
        self._controller.move_by(self._id, distance)
        self._lock.release()

    def move_to(self, position: float, convert=True) -> ...:
        """Move the stepper to a certain position."""
        if convert:
            position = self._convert_to_steps(position)

        self._lock.acquire()
        self._controller.move_to(self._id, position)
        self._lock.release()

    def start_jog(self, direction: str, convert=True) -> ...:
        """Start jogging the stepper."""
        if convert:
            speed = self._convert_to_steps(self.speed)
        dir = -1 if direction == '-' else 1
        self._lock.acquire()
        self._controller.start_jog(self._id, dir*speed)
        self._lock.release()

    def stop_jog(self) -> ...:
        """Stop jogging the stepper."""
        self._lock.acquire()
        self._controller.stop_jog(self._id)
        self._lock.release()

    def emergency_stop(self):
        """Emergency stop the stepper immediately."""
        self._controller.emergency_stop()

    def stop(self) -> ...:
        """Stop the stepper."""
        self._lock.acquire()
        self._controller.stop()
        self._lock.release()

    # SUPPORT METHODS
    def _convert_to_steps(self, value: float) -> int:
        """Convert a value from um to steps."""
        return int(self._steps_per_um * value)

    def _convert_to_um(self, value: int) -> float:
        """Convert a value from steps to um."""
        return value / self._steps_per_um
