from .base import NotSupportedError, Base, HardwareNotConnectedError, HardwareError
import serial
from typing import Union, Tuple
import time
import threading as tr
from ..configs.settings import Settings
import multiprocessing as mp
from time import sleep


class MainXYController:
    """
    This is the main class responsible for communication with the eld controller.

    .. attention::
        The controler uses steps as the unit of measurement. This means all values from
        the user should be converted from um to steps. This is not done in this class
        and is the responsibility of the overlaying class
    """

    _type = "MAINXYCONTROLLER"
    _is_connected = False

    def __init__(self, settings: Settings, em_event: mp.Event) -> ...:
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
        self._port = settings.get(self._type + ".DEFAULT", "port")
        self._baud_rate = settings.get(self._type + ".DEFAULT", "baud_rate")
        self._timeout = settings.get(self._type + ".DEFAULT", "timeout")
        self._zero_timeout = settings.get(self._type + ".DEFAULT", "zero_timeout")
        self._temp_control_active = False
        self._lock = tr.Lock()
        self._ser_lock = tr.Lock()
        self._homed = False
        self._zeroed = False
        self._vacuum_state = False
        self._ser = None

    # COMMUNICATION
    def _send_and_receive(
        self,
        command: str,
        expect_confirmation: bool = True,
        expect_response: bool = False,
    ) -> Union[None, list]:
        """
        Send a command to the base controller and receive the response.

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
            raise HardwareNotConnectedError(
                "The Base stage controller is not connected."
            )

        self._ser_lock.acquire()
        if "\r\n" not in command:
            command = command.strip()
            command += "\r\n"

        self._ser.reset_input_buffer()  # Empty the serial buffer
        self._ser.write(command.encode())  # Send the command

        got_response = False
        if expect_confirmation or expect_response:
            etime = time.time() + self._timeout
            while time.time() < etime and not got_response:
                # Check if a confirmation is expected
                time.sleep(0.01)

                if self._ser.in_waiting > 0:
                    data_resp = self._ser.readlines()
                    for i in range(len(data_resp)):
                        data_resp[i] = data_resp[i].strip()

                    to_remove = []

                    # Remove empty lines
                    for cnt, i in enumerate(data_resp):
                        if i == b"":
                            to_remove.append(cnt)
                    for i in to_remove[::-1]:
                        data_resp.pop(i)

                    if len(data_resp) == 0:
                        continue
                    if expect_confirmation and not data_resp[0][-2:] == b"OK":
                        raise ValueError(
                            "Received an unexpected confirmation {}".format(
                                data_resp
                            )
                        )
                    if not expect_response:
                        self._ser_lock.release()
                        return
                    else:
                        self._ser_lock.release()
                        return data_resp[1:]  # Leave out the confirmation

            if not got_response:
                # Waiting for response timed out
                print("The command {} did not receive a response.".format(command))
                raise HardwareError(
                    "The base controller did not respond to the command {}.".format(
                        command
                    )
                )
            self._ser_lock.release()

    def _get_axis_id(self, axis: str) -> str:
        """
        Get the axis id from the axis name.

        Parameters
        ----------
        axis: str
            The axis name.

        Returns
        -------
        axis_id: str
            The axis id.
        """
        if axis.lower() == "h":
            return "x"
        elif axis.lower() == "j":
            return "y"
        else:
            raise ValueError("The axis {} is not supported.".format(axis))

    def start_check_error(self):
        self._check_error_flag = tr.Event()
        self.error_thread = tr.Tread(target=self._check_error, args=(0.2, self._check_error_flag))
        self.error_thread.start()

    def stop_check_error(self):
        self._check_error_flag.set()
        self.error_thread.join()
    
    def _check_error(self, interval : Union[float, int], stop_flag : tr.Event()) -> ...:
        """Check if the controller has an error."""
        while not stop_flag.is_set() or self._em_event.is_set():
            # Does not capture the serial lock because there is no further interaction with the class
            res = self._send_and_receive("ge", expect_response=True)

            # Check critical error codes
            if res[0] != b"0":
                self.emergency_stop()
                raise HardwareError(
                    "The base control box is not powered."
                )
            if not self._em_event.is_set():
                if res[1] != b"0":
                    self.emergency_stop()
                    raise HardwareError("The emergency stop button was triggered.")
                elif res[3] != b"0" or res[4] != b"0" or res[5] != b"0":
                    self.emergency_stop()
                    raise HardwareError("The heater response timed out while the PID is active.")
                elif res[6] != b"0":
                    self.emergency_stop()
                    raise HardwareError("The stepper response timed out while zero-ing.")

            time.sleep(interval)

        if self._em_event.is_set():
            stop_flag.set()

    # MOVEMENT ATTRIBUTES
    @property
    def is_homed(self) -> bool:
        """Check if the hardware is homed."""
        return self._homed

    @property
    def is_zeroed(self) -> bool:
        """Check if the hardware has performed the zero move."""
        return self._zeroed

    @property
    def speed(self) -> int:
        """Get the speed of the controller."""
        self._lock.acquire()
        res = self._send_and_receive("l", expect_response=True)
        self._lock.release()
        return res[0]

    @property
    def acceleration(self) -> int:
        """Get the acceleration of the controller."""
        self._lock.acquire()
        res = self._send_and_receive("l", expect_response=True)
        self._lock.release()
        return res[1]

    # TEMPERATURE ATTRIBUTES
    @property
    def temperature(self) -> float:
        """Get the temperature of the hardware."""
        self._lock.acquire()
        res = self._send_and_receive("gt", expect_response=True)[0]
        self._lock.release()
        return float(res.decode())

    @property
    def target_temperature(self) -> float:
        """Get the target temperature of the hardware."""
        self._lock.acquire()
        res = self._send_and_receive("l", expect_response=True)
        self._lock.release()
        return float(res[5].decode())

    @target_temperature.setter
    def target_temperature(self, temperature: Union[float, int]) -> ...:
        """Set the target temperature of the hardware."""
        if self._em_event.is_set():
            return
        self._lock.acquire()
        if not self._temp_control_active:
            # Activate the temp control
            self._send_and_receive("fp1")

        self._send_and_receive("st{}".format(temperature * 100))
        self._lock.release()

    # CONNECTION FUNCTIONS
    def connect(self) -> ...:
        """Connect the hardware."""
        if self._is_connected:
            return
        self._lock.acquire()
        # time.sleep(0.1)
        self._ser = serial.Serial(self._port, self._baud_rate, timeout=self._timeout)
        m3 = b"Base Stage Controller10\r\n"

        # Reset the input buffer
        time.sleep(0.5)
        self._ser_lock.acquire()
        self._ser.reset_input_buffer()
        self._ser.write(b"gid\r\n")
        msg_list = self._ser.readlines()
        self._ser_lock.release()
        if not m3 in msg_list:
            raise HardwareError(
                "The base controller did not respond with the correct id. {}".format(
                    msg_list
                )
            )

        # Enter run mode so the controller can be used
        self._send_and_receive("n", expect_confirmation=True)

        # Set the velocity to max to make zero faster
        self._send_and_receive("ssx25600", expect_response=True)
        self._send_and_receive("ssy25600", expect_response=True)
        self._send_and_receive('sa200', expect_response=True)
        self._send_and_receive('sd200, expect_response=True')
        self._is_connected = True
        
        self._lock.release()

        self.start_check_error()

    def disconnect(self) -> ...:
        """Disconnect the hardware."""
        if not self._is_connected:
            return
        self._send_and_receive("p")
        self._ser.close()
        self._is_connected = False

    def is_connected(self) -> bool:
        """Check if the hardware is connected."""
        return self._is_connected

    # STATUS FUNCTIONS
    def is_heating(self) -> bool:
        """Check if the hardware is heating."""
        self._lock.acquire()
        res = self._send_and_receive("ga", expect_response=True)
        self._lock.release()
        return res

    def is_cooling(self) -> bool:
        """Check if the hardware is cooling."""
        self._lock.acquire()
        res = self._send_and_receive("ga", expect_response=True)
        self._lock.release()
        return res

    def is_moving(self, axis=Union[str, None]) -> bool:
        """Check if the hardware is moving."""
        self._lock.acquire()
        res = self._send_and_receive("gb", expect_response=True)
        self._lock.release()
        if axis is None:
            if res[15] == b"1" or res[31] == b"1" or res[47] == b"1":
                return True
            else:
                return False
        if axis.lower() not in ["j", "h"]:
            raise HardwareError(
                "Unknown axis {}, could not determine if moving".format(axis)
            )
        else:
            if axis.lower() == "h":
                if res[15] == b"1":
                    return True
                else:
                    return False
            elif axis.lower() == "j":
                if res[31] == b"1":
                    return True
                else:
                    return False

    # HOMING FUNCTIONS
    def zero(self) -> ...:
        """
        Zero the connected stepper motors.

        .. note::
            The axis will be homed separately, first the x-axis and then the y-axis.

        Raises
        ------
        HardwareError
            If the stepper motors do not successfully zero.
        """
        if self._em_event.is_set():
            return
        self._lock.acquire()
        self._send_and_receive("z")

        # Wait for the homing to finish
        x_homed = False
        y_homed = False

        etime = time.time() + self._zero_timeout  # Max 20 seconds to home
        while not (x_homed and y_homed) and time.time() < etime:
            if self._ser.in_waiting > 0:
                data = self._ser.readlines()
                for i in data:
                    if i.strip()[:8] == b"ENDPOS X":
                        x_homed = True
                    if i.strip()[:8] == b"ENDPOS Y":
                        y_homed = True
        self._lock.release()

        if not x_homed or not y_homed:
            raise HardwareError(
                "The base controller did not home within the time limit."
            )
        self._homed = True
        self._zeroed = True

    def home(self) -> ...:
        """
        Home the connected stepper motors.

        Will home the x and y axis (not zero) if the axis has been zeroed. If the servos
        were not set to zeo first that will be done instead. Go to position
        is used instead of the build in home function to prevent the stepper from moving simultaneously.

        .. note::
            This method will move the x and y axis to the internal 0 position.
        """
        if self._em_event.is_set():
            return
        if not self._zeroed:
            self.zero()
        else:
            self._lock.acquire()
            self._send_and_receive("h")
            self._lock.release()
            self._homed = True

    # MOVING FUNCTIONS
    def get_position(self, axis: Union[str, None] = None) -> Union[int, Tuple[int]]:
        """
        Get the position of the hardware.

        Parameters
        ----------
        axis: 'x', 'y' or None
            The axis to get the position of. If None, the position of all axes will be returned.
        """
        if self._em_event.is_set():
            return
        id = self._get_axis_id(axis)
        self._lock.acquire()
        res1 = self._send_and_receive("gp{}".format(id), expect_response=True)[0]
        self._lock.release()
        return res1

    def start_jog(self, axis: str, velocity: Union[float, int]) -> ...:
        """
        Start a jog in a direction.

        .. warning::
            This function does not limit the speed of the jog. The calling
            function should limit the speed of the jog.

        Parameters
        ----------
        axis : str
            The axis to jog.
        direction : str
            The direction to jog, this can be + or -.

        """
        if self._em_event.is_set():
            return
        id = self._get_axis_id(axis)
        self._lock.acquire()
        # Jogging gives a different confirmation than other commands
        _ = self._send_and_receive("sv{}{}".format(id, int(velocity)), expect_response=True)
        self._lock.release()

    def stop_jog(self, axis: Union[None, str] = None) -> ...:
        """
        Stop a jog.

        Parameters
        ----------
        axis : str or None
            The axis to stop the jog on. If None, all axes will be stopped.
        """
        self._lock.acquire()
        if axis is None:
            self._send_and_receive("x")
        else:
            id = self._get_axis_id(axis)
            self._send_and_receive("sv{}0".format(id), expect_response=True)
        self._lock.release()

    def move_to(self, id: str, position: Union[float, int]) -> ...:
        """
        Move the hardware to a position.

        Parameters
        ----------
        id : str
            The axis to move, can be 'x' or 'y'.
        position : float or int
            The position to move to.
        """
        if self._em_event.is_set():
            return
        id = self._get_axis_id(id)
        self._lock.acquire()
        self._send_and_receive("sp{}{}".format(id.lower(), position))
        self._lock.release()

    def move_by(self, id: str, distance: Union[float, int]) -> ...:
        """
        Move the hardware by a position.

        Parameters
        ----------
        id : str
            The axis to move, can be 'x' or 'y'.
        distance : float or int
            The distance to move by.
        """
        pos = int(self.get_position(id))
        id = self._get_axis_id(id)
        self._lock.acquire()
        print(pos, distance)
        self._send_and_receive("sp{}{}".format(id.lower(), pos + distance))
        self._lock.release()

    def stop(self) -> ...:
        """Unconditionally stop the hardware."""
        self._lock.acquire()
        self._send_and_receive("x")
        self._lock.release()

    def emergency_stop(self) -> ...:
        """
        Unconditionally stop the hardware.

        .. note::
            This function intentionally does not capture the lock. This is
            because the function should be able to run at all times

        .. attention::
            This method will set the emergency flag that all controllers
            will check before executing any commands. This will prevent
            any commands from being executed until the flag is cleared.
        """
        self._send_and_receive("x")  # Stop all motion
        self._send_and_receive('fp0')  # Stop temp control
        self._em_event.set()

    def toggle_vacuum(self, state):
        self._lock.acquire()
        if state:
            self._send_and_receive("su1")
        else:
            self._send_and_receive("su0")
        self._lock.release()
