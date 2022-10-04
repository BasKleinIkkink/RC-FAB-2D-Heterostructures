from ..hardware.KIM101 import KIM101
from ..hardware.PRMTZ8 import PRMTZ8


class SampleHolder(object):
    """Class to controll the sample holder."""

    def __init__(self, emergency_shutdown_event):
        self._emergency_shutdown_event = emergency_shutdown_event
        self._motor_controller = KIM101()
        self._axis = [
            
        ]