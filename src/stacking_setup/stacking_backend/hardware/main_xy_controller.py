from .base import NotSupportedError, Base, HardwareNotConnectedError
import serial
from typing import Union, Tuple
import time
import threading as tr
from ..configs.settings import Settings
import multiprocessing as mp


class MainXYController(Base):
    """
    This is the main class responsible for communication with the eld controller.
    
    This class is the support class for the following hardware classes
    - :class:`SampleStage`
    - :class:`EmergencyBreaker`

    .. note::
        The controler uses steps as the unit of measurement. This means all values from
        the user should be converted from um to steps
    """
    _type = 'MAINXYCONTROLLER'

    def __init__(self, settings : Settings, em_event : mp.Event) -> ...:
        """
        Initialize the main xy controller.
        
        Parameters
        ----------
        settings: Settings
            The settings object.
        em_event: mp.Event
            The emergency event.
        """
        # Get the settings
        self._em_event = em_event
        self._port = settings.get(self._type+'.DEFAULT', 'port')
        self._baud_rate = settings.get(self._type+'.DEFAULT', 'baud_rate')
        self._timeout = settings.get(self._type+'.DEFAULT', 'timeout')
        self._max_temperature = settings.get(self._type+'.DEFAULT', 'max_temperature')
        # self._serial_nr = settings.get(self._type+'.DEFAULT', 'serial_nr')
        self._temp_control_active = False
        self._lock = tr.Lock()
        self._homed = False

    # COMMUNICATION
    def _send_and_receive(self, command : str, expect_confirmation : bool=True, 
            expect_response : bool=False) -> Union[None, list]:
        """
        Send a command to the base controller and receive the response.

        .. important::
            Most functions acquire a lock before sending a command to the the controller, this is to prevent
            multiple threads from sending commands at the same time. This function is an exception to this rule,
            it is the responsibility of the calling function to acquire the lock before calling this function.
        
        Parameters:
        -----------
        command: str
            The command to send to the tango desktop.
        expect_confirmation: bool
            If the command should expect a confirmation.
        expect_response: bool
            If the command should expect a response.

        Raises:
        -------
        HardwareNotConnectedError: 
            If the tango desktop is not connected.
        ValueError:
            If the command caused an error

        Returns:
        --------
        response: str or None
            The response of the tango desktop.
        """
        if self._ser is None:
            raise HardwareNotConnectedError("The Base stage controller is not connected.")
        elif self._em_event.is_set():
            return None  # Do nothing to give other classes a chance to stop the emergency stop

        if '\r\n' not in command:
            command = command.strip()
            command += '\r\n'

        self._ser.reset_input_buffer() # Empty the serial buffer
        self._ser.write(command.encode())  # Send the command

        got_response = False
        
        if expect_confirmation or expect_response:
            etime = time.time() + self._timeout
            while time.time() < etime and not got_response:
                # Check if a confirmation is expected
                time.sleep(0.001)

                if expect_confirmation or expect_response:
                    if self._ser.in_waiting > 0:
                        data_resp = self._ser.readlines()
                        for i in range(len(data_resp)):
                            data_resp[i] = data_resp[i].strip()

                        to_remove = []
                        for cnt, i in enumerate(data_resp):
                            if i == b'':
                                to_remove.append(cnt)
                        for i in to_remove[::-1]:
                            data_resp.pop(i)

                        if expect_confirmation and not data_resp[0][-2:] == b'OK':
                            raise ValueError('Received an unexpected confirmation {}'.format(data_resp))
                        if not expect_response:
                            return
                        else:
                            return data_resp[1:]  # Leave out the confirmation
                                
            if not got_response:
                # Waiting for response timed out
                print("The command {} did not receive a response.".format(command))
                raise HardwareNotConnectedError("The tango desktop did not respond to the command {}.".format(command))

    # MOVEMENT PROFILE ATTRIBUTES
    @property
    def speed(self) -> int:
        """Get the speed of the controller."""
        self._lock.acquire()
        res = self._send_and_receive('l', expect_response=True)
        self._lock.release()
        return res[0]

    @property
    def acceleration(self) -> int:
        """Get the acceleration of the controller."""
        self._lock.acquire()
        res = self._send_and_receive('l', expect_response=True)
        self._lock.release()
        return res[1]

    def position(self, axis : Union[str, None]=None) -> Union[int, Tuple[int]]:
        """
        Get the position of the hardware.

        Parameters
        ----------
        axis: str or None
            The axis to get the position of. If None, the position of all axes will be returned.
        """
        self._lock.acquire()
        res1 = self._send_and_receive('gpx', expect_response=True)[0]
        res2 = self._send_and_receive('gpy', expect_response=True)[0]
        self._lock.release()
        
        if axis.lower() == 'x':
            return int(res1)
        elif axis.lower() == 'y':
            return int(res2)
        else:
            return int(res1), int(res2)

    # TEMPERATURE ATTRIBUTES
    @property
    def temperature(self) -> float:
        """Get the temperature of the hardware."""
        self._lock.acquire()
        res = self._send_and_receive('gt', expect_response=True)[0]
        self._lock.release()
        return float(res.decode())

    @property
    def target_temperature(self) -> float:
        """Get the target temperature of the hardware."""
        self._lock.acquire()
        res = self._send_and_receive('l', expect_response=True)
        self._lock.release()
        return float(res[3].decode()) / 10

    @target_temperature.setter
    def target_temperature(self, temperature):
        """Set the target temperature of the hardware."""
        if temperature > self._max_temperature:
            temperature = self._max_temperature
        
        self._lock.acquire()
        self._send_and_receive('st{}'.format(temperature * 1000))

        if not self._temp_control_active:
            # Activate the temp control
            self._send_and_receive('fp1')
        self._lock.release()

    # CONNECTION FUNCTIONS
    def connect(self):
        """Connect the hardware."""
        self._ser = serial.Serial(self._port, self._baud_rate, timeout=self._timeout)

        # Read the welcome message
        m1 = b'BaseStage Controller V0.1 starting...'
        m2 = b'Initialization done, starting control tasks...'
        msg_list = self._ser.readlines()
        for i in range(len(msg_list)):
            msg_list[i] = msg_list[i].strip()

        if not m1 in msg_list or not m2 in msg_list:
            raise HardwareNotConnectedError("The base controller did not respond with the correct welcome message.")

        # Enter run mode so the controller can be used
        self._send_and_receive('n', expect_confirmation=True)

    def disconnect(self):
        """Disconnect the hardware."""
        self._send_and_receive('p', expect_confirmation=True)
        self._ser.close()

    # STATUS FUNCTIONS
    def is_connected(self) -> bool:
        """Check if the hardware is connected."""
        self._lock.acquire()
        resp = self._send_and_receive('gb', expect_response=True)
        self._lock.release()
        if resp is not None:
            return True
        else:
            return False

    def is_moving(self):
        """Check if the hardware is moving."""
        raise NotSupportedError()

    def is_homed(self):
        """Check if the hardware is homed."""
        raise NotSupportedError()

    def get_status(self):
        """Give a status report."""
        raise NotImplementedError()

    # HOMING FUNCTIONS
    def home(self):
        """Home the hardware."""
        raise NotSupportedError()

    # MOVING FUNCTIONS
    def start_jog(self, direction):
        """Start a jog in a direction."""
        raise NotSupportedError()

    def stop_jog(self):
        """Stop a jog."""
        raise NotSupportedError()

    def move_to(self, id, position):
        """Move the hardware to a position."""
        self._lock.acquire()
        self._send_and_receive('sp{}{}'.format(id.lower(), position))
        self._lock.release()

    def move_by(self, id, distance):
        """Move the hardware by a position."""
        pos = self.position(id)
        self._lock.acquire()
        self._send_and_receive('sp{}{}'.format(id.lower(), pos + distance))
        self._lock.release()

    def rotate_to(self, rotation):
        """Rotate the hardware to a position."""
        raise NotSupportedError()

    def rotate_by(self, rotation):
        """Rotate the hardware by a position."""
        raise NotSupportedError()

    def stop(self):
        """Unconditionally stop the hardware."""
        raise NotImplementedError()

    def emergency_stop(self):
        """Unconditionally stop the hardware."""
        self.send_and_receive('x')
