from ..hardware.KIM101 import KIM101
from ..hardware.PIA13 import PIA13


class MaskHolder(object):
    """Class to controll the mask holder."""

    def __init__(self, emergency_shutdown_event):
        self._emergency_shutdown_event = emergency_shutdown_event
        self._piezo_controller = KIM101()
        self._axis = [
            PIA13('X', 1, self._piezo_controller), 
            PIA13('Y', 2, self._piezo_controller), 
            PIA13('Z', 3, self._piezo_controller),
        ]
