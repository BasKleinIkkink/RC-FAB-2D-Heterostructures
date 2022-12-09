try:
    from .base import Base
except ImportError:
    from base import Base
import threading as tr
from .main_xy_controller import MainXYController
from ..configs.settings import Settings
from typing import Union
import multiprocessing as mp


class SampleBed(Base):
    """Class to control the sample bed."""
    _type = 'SAMPLE BED'

    def __init__(self, id : str, controller : MainXYController, 
            em_event : mp.Event, settings : Settings) -> ...:
        """
        Initialize the sample bed.
        
        Parameters
        ----------
        id: str
            The id of the sample bed.
        controller: MainXYController
            The controller to use.
        em_event: multiprocessing.Event
            The event to use for emergency stop.
        settings: Settings
            The settings object.
        """
        self._id = id
        self._controller = controller
        self._settings = settings
        self._lock = tr.Lock()
        self._em_event = em_event

        # Load some settings
        self._max_temperature = settings.get(self._type+'.DEFAULT', 'max_temperature')

    # ATTRIBUTES
    @property
    def device_info(self) -> dict:
        """Get the device info of the sample bed."""
        return {'id': self._id,
                'type': self._type,
                'controller': self._controller.type
                }

    @property
    def temperature(self) -> float:
        """Get the temperature of the sample bed."""
        self._lock.acquire()
        temp = self._controller.temperature
        self._lock.release()
        return temp

    @property
    def target_temperature(self) -> float:
        """Get the target temperature of the sample bed."""
        self._lock.acquire()
        temp = self._controller.target_temperature
        self._lock.release()
        return temp

    @target_temperature.setter
    def target_temperature(self, temperature : Union[float, int]) -> ...:
        """Set the target temperature of the sample bed."""
        if temperature > self._max_temperature:
            temperature = self._max_temperature
        self._lock.acquire()
        self._controller.target_temperature = temperature
        self._lock.release()

    @property
    def max_temperature(self) -> float:
        """Get the maximum temperature of the sample bed."""
        return self._max_temperature

    # CONNECTION FUNCTIONS
    def connect(self) -> ...:
        """Connect the sample bed."""
        self._lock.acquire()
        if not self._controller.is_connected():
            self._controller.connect()
        self._lock.release()

    def disconnect(self) -> ...:
        """Disconnect the sample bed."""
        self._lock.acquire()
        if self.controller.is_connected():
            self.controller.disconnect()
        self._lock.release()

    # STATUS FUNCTIONS
    def is_connected(self) -> bool:
        """Check if the sample bed is connected."""
        self._lock.acquire()
        state = self._controller.is_connected() 
        self._lock.release()
        return state

    def is_heating(self) -> bool:
        """Check if the sample bed is heating."""
        self._lock.acquire()
        state = self._controller.is_heating()
        self._lock.release()
        return state

    def is_cooling(self) -> bool:
        """Check if the sample bed is cooling."""
        self._lock.acquire()
        state = self._controller.is_cooling()
        self._lock.release()
        return state

    # OTHER FUNCTIONS
    def toggle_vacuum_pump(self):
        pass