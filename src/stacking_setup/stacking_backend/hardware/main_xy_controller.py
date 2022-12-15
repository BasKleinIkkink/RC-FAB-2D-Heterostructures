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
        self._temp_control_active = False
        self._lock = tr.Lock()
        self._homed = False
        self._zeroed = False
        self._vacuum_state = False

    # COMMUNICATION
    def _send_and_receive(
        self,
        command: str,
        expect_confirmation: bool = True,
        expect_response: bool = False,
    ) -> Union[None, list]:
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
            raise HardwareNotConnectedError(
                "The Base stage controller is not connected."
            )
        elif self._em_event.is_set():
            return None  # Do nothing to give other classes a chance to stop the emergency stop

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
                time.sleep(0.001)

                if expect_confirmation or expect_response:
                    if self._ser.in_waiting > 0:
                        data_resp = self._ser.readlines()
                        for i in range(len(data_resp)):
                            data_resp[i] = data_resp[i].strip()

                        to_remove = []
                        for cnt, i in enumerate(data_resp):
                            if i == b"":
                                to_remove.append(cnt)
                        for i in to_remove[::-1]:
                            data_resp.pop(i)

                        if expect_confirmation and not data_resp[0][-2:] == b"OK":
                            raise ValueError(
                                "Received an unexpected confirmation {}".format(
                                    data_resp
                                )
                            )
                        if not expect_response:
                            return
                        else:
                            return data_resp[1:]  # Leave out the confirmation

            if not got_response:
                # Waiting for response timed out
                print("The command {} did not receive a response.".format(command))
                raise HardwareError(
                    "The tango desktop did not respond to the command {}.".format(
                        command
                    )
                )

    def check_error(self) -> ...:
        """Check if the controller has an error."""
        self._lock.acquire()
        res = self._send_and_receive("e", expect_response=True)

        # Check critical error codes
        if res[0] != b"0":
            self.emergency_stop()
        elif res[1] != b"0":
            raise HardwareError(
                "The stepper drivers on the base control box are not powered or switched off."
            )
        elif res[2] != b"0" or res[3] != b"0":
            raise HardwareError("The heater respons timed out while the PID is active.")
        elif res[4] != b"0":
            raise HardwareError("The stepper response timed out while zero-ing.")

        # Get the non critical error codes
        res = self._send_and_receive("gb", expect_response=True)
        if res[14] != b"0" or res[1] != b"0":
            raise HardwareError("One or both of the stepper motors have stalled.")

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
        return float(res[3].decode()) / 10

    @target_temperature.setter
    def target_temperature(self, temperature: Union[float, int]) -> ...:
        """Set the target temperature of the hardware."""
        self._lock.acquire()
        if not self._temp_control_active:
            # Activate the temp control
            self._send_and_receive("fp1")

        self._send_and_receive("st{}".format(temperature * 100))
        self._lock.release()

    # CONNECTION FUNCTIONS
    def connect(self, zero: bool = True) -> ...:
        """Connect the hardware."""
        self._lock.acquire()
        # time.sleep(0.1)
        self._ser = serial.Serial(self._port, self._baud_rate, timeout=self._timeout)
        m3 = b"Base Stage Controller10\r\n"

        # Reset the input buffer
        time.sleep(2)
        self._ser.reset_input_buffer()
        self._ser.write(b"gid\r\n")
        msg_list = self._ser.readlines()
        if not m3 in msg_list:
            raise HardwareError(
                "The base controller did not respond with the correct id. {}".format(
                    msg_list
                )
            )

        # Enter run mode so the controller can be used
        self._send_and_receive("n", expect_confirmation=True)
        self._is_connected = True
        self._lock.release()

    def disconnect(self) -> ...:
        """Disconnect the hardware."""
        self._send_and_receive("p", expect_confirmation=True)
        self._ser.close()
        self._is_connected = False

    def is_connected(self) -> bool:
        """Check if the hardware is connected."""
        return self._is_connected

    # STATUS FUNCTIONS
    def is_heating(self) -> bool:
        """Check if the hardware is heating."""
        raise NotImplementedError()
        self._lock.acquire()
        res = self._send_and_receive("ga", expect_response=True)
        self._lock.release()

    def is_cooling(self) -> bool:
        """Check if the hardware is cooling."""
        raise NotImplementedError()
        self._lock.acquire()
        res = self._send_and_receive("ga", expect_response=True)
        self._lock.release()

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
        if axis.lower() not in ["x", "y", "z"]:
            raise HardwareError(
                "Unknown axis {}, could not determine if moving".format(axis)
            )
        else:
            if axis.lower() == "x":
                if res[15] == b"1":
                    return True
                else:
                    return False
            elif axis.lower() == "y":
                if res[31] == b"1":
                    return True
                else:
                    return False
            elif axis.lower() == "z":
                if res[47] == b"1":
                    return True
                else:
                    return False

    # HOMING FUNCTIONS
    def zero(self) -> ...:
        """
        Zero the connected stepper motors.

        .. note::
            The axis will be homed seperately, first the x-axis and then the y-axis.
            The stepper will move to home switch -> range_switxh -> home_switch.

        Raises
        ------
        HardwareError
            If the stepper motors do not succesfully zero.
        """
        self._lock.acquire()
        self._send_and_receive("z", expect_confirmation=True)

        # Wait for the homing to finish
        x_homed = False
        y_homed = False

        etime = time.time() + 20  # Max 20 seconds to home
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
        if not self._zeroed:
            self.zero()
        else:
            self._lock.acquire()
            self._send_and_receive("spx0")
            self._lock.release()
            while self.is_moving(axis="x"):
                time.sleep(0.1)
            self._lock.acquire()
            self._send_and_receive("spy0")
            self._lock.release()
            while self.is_moving(axis="y"):
                time.sleep(0.1)

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
        self._lock.acquire()
        res1 = self._send_and_receive("gpx", expect_response=True)[0]
        res2 = self._send_and_receive("gpy", expect_response=True)[0]
        self._lock.release()

        if axis.lower() == "x":
            return int(res1)
        elif axis.lower() == "y":
            return int(res2)
        else:
            return int(res1), int(res2)

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
        self._lock.acquire()
        self._send_and_receive("sv{}{}".format(axis, velocity))
        self._lock.release()

    def stop_jog(self, axis: Union[None, str] = None) -> ...:
        """
        Stop a jog.

        Parameters
        ----------
        axis : str or None
            The axis to stop the jog on. If None, all axes will be stopped.
        """
        if axis is None:
            self.stop()
        elif axis.lower() == "x":
            self._send_and_receive("svx0")
        elif axis.lower() == "y":
            self._send_and_receive("svy0")

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
        pos = self.get_position(id)
        self._lock.acquire()
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
        self.send_and_receive("x")

    def vacuum_on(self) -> ...:
        """Turn the vacuum on."""
        self._lock.acquire()
        self._send_and_receive("su1")
        self._lock.release()

    def vacuum_off(self) -> ...:
        """Turn the vacuum off."""
        self._lock.acquire()
        self._send_and_receive("su0")
        self._lock.release()
