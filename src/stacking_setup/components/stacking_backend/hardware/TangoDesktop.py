import serial
from typing import Union
from typeguard import typechecked
from ..configs.settings import Settings
import time
import threading as tr
import multiprocessing as mp
from .base import NotSupportedError

try:
    from .base import Base, HardwareNotConnectedError
except ImportError:
    from base import Base, HardwareNotConnectedError


class TangoDesktop(Base):
    """
    Class for TangoDesktop hardware.

    .. warning::

        While the manual mentiones the !cal and !rm functions for calibration these are not
        supported and will cause unwanted behaviour if called. For these methods to be
        implemented the Tango desktop needs an AUX IO port for endstops, wich we do not have.

    Communication interface:
    ------------------------
    All TANGO controllers communicate via a serial COM port interface, independent
    of the controller type (RS232C, USB, PCI, PCI-E). The default setting is
    57600,8,2,N.

    Instruction syntax:
    -------------------
    The instructions and parameters are sent as cleartext ASCII strings with a
    terminating carriage return [CR], which is 0x0d hex. Characters may be upper-,
    lower- or camel-case. The parameters are separated by a space character.
    This provides easy access to all functions by using a simple terminal program
    such as HyperTerminal. A typical instruction syntax is as follows:

    [!,?][instruction][SP][optional axis] [parameter1][SP][parameter2] [etc…] [CR]

    A read instruction may return more than one parameter. In many cases the number
    of returned parameters depends on the amount of available axes:

    [axis X] [if available: axis Y] [if available: axis Z] [if available: axis A]

    """

    _id = None
    _type = "TANGODESKTOP"
    _controller = None
    _ser = None

    def __init__(self, id: str, settings: Settings, em_event: mp.Event) -> ...:
        """
        Initialize the tango desktop.

        Parameters:
        -----------
        id: str
            The id of the tango desktop.
        settings: Settings
            The settings of the tango desktop.
        em_event: mp.Event
            The emergency stop event.
        """
        # Check if the tango desktop is connected
        self._id = id
        self._lock = tr.Lock()
        self._em_event = em_event

        # Get the settings
        self._port = settings.get(self._type + ".DEFAULT", "port")
        self._baud_rate = settings.get(self._type + ".DEFAULT", "baud_rate")
        self._timeout = settings.get(self._type + ".DEFAULT", "timeout")
        self._serial_nr = settings.get(self._type + ".DEFAULT", "serial_nr")
        self._max_speed = settings.get(self._type + "." + self._id, "max_vel")
        self._max_acceleration = settings.get(self._type + "." + self._id, "max_acc")
        self._current_speed = None  # Only used for jogging

        if self._controller is None:
            # Controller is not initiated, check if the port can be captured
            try:
                ser = serial.Serial(self._port, self._baud_rate, timeout=self._timeout)
                ser.write("?readsn \r".encode())
                resp = ser.readline().decode().strip()

                # Check the serial nr
                if resp != self._serial_nr:
                    ser.close()
                    raise HardwareNotConnectedError(
                        "The tango desktop that is connected does not match the saved serial nr {}.".format(
                            self._serial_nr
                        )
                    )
                else:
                    ser.close()

            except [serial.SerialException, ConnectionRefusedError] as e:
                raise HardwareNotConnectedError(
                    "Could not connect to port: {}: e {}".format(self._port, e)
                )

    # ATTRIBUTES
    @property
    def steps_per_um(self) -> Union[int, float]:
        """Get the steps per um."""
        self._lock.acquire()
        steps_per_rev = float(
            self._send_and_receive(
                "?motorsteps z", expect_response=True, expect_confirmation=False
            )
        )
        self._lock.release()
        return round(steps_per_rev / self._spindle_pitch, 3)

    @property
    def position(self) -> Union[float, int]:
        """Get the current position in um from 0."""
        raise NotSupportedError()
        # self._lock.acquire()
        # pos = float(
        #     self._send_and_receive(
        #         "?pos z", expect_response=True, expect_confirmation=False
        #     )
        # )
        # self._lock.release()
        # return pos

    @property
    def speed(self) -> Union[float, int]:
        """Get the current speed in um/s."""
        if self._em_event.is_set():
            return None  # Do nothing to give other classes a chance to stop the emergency stop
        self._lock.acquire()
        rev_per_s = float(
            self._send_and_receive(
                "?vel z", expect_response=True, expect_confirmation=False
            )
        )
        self._lock.release()
        return round(rev_per_s / self._spindle_pitch, 3)

    @speed.setter
    def speed(self, speed: Union[float, int]) -> ...:
        """
        Set the speed of the tango desktop (um/s).

        Parameters
        ----------
        speed : float
            The speed in um/s.
        """
        if self._em_event.is_set():
            return None  # Do nothing to give other classes a chance to stop the emergency stop

        # Calculate the needed revolutions per second
        if speed > self._max_speed:
            speed = self._max_speed
        self._lock.acquire()
        rev_per_s = round(speed / self._spindle_pitch, 3)
        self._send_and_receive(
            "!vel z {}".format(rev_per_s),
            expect_confirmation=False,
            expect_response=False,
        )
        self._current_speed = speed  # Only used for jogging
        self._lock.release()

        print("Speed set to {} um/s".format(speed))
        self.acceleration = speed * 2

    @property
    def acceleration(self) -> Union[float, int]:
        """Get the acceleration of the tango desktop (um/s^2)."""
        if self._em_event.is_set():
            return None  # Do nothing to give other classes a chance to stop the emergency stop

        # Tango expects the acceleration in m/s^2
        self._lock.acquire()
        acc = float(
            self._send_and_receive(
                "?accel z", expect_response=True, expect_confirmation=False
            )
        )
        self._lock.release()
        return acc

    @acceleration.setter
    def acceleration(self, acceleration: Union[float, int]) -> ...:
        """
        Set the acceleration of the tango desktop.

        .. note::
            Because consistency was not a priority when writing the tango desktop
            command set the acceleration is set in m/s^2 instead of um/s^2.
        """
        if self._em_event.is_set():
            return None  # Do nothing to give other classes a chance to stop

        if acceleration > self._max_acceleration:
            acceleration = self._max_acceleration
        acceleration /= 10e3
        self._lock.acquire()
        self._send_and_receive(
            "!accel z {}".format(acceleration),
            expect_confirmation=False,
            expect_response=False,
        )
        self._lock.release()

    # CONNECTION FUNCTIONS
    def _message_waiting(self) -> bool:
        """
        Check if a message is waiting.

        .. warning::
            This function is mostly used as a support function and does not capture the lock.
            This means that this function should only be used when the lock is already captured.

        Returns
        -------
        bool
            True if a message is waiting, False otherwise.
        """
        state = True if self._ser.in_waiting > 0 else False
        return state

    def _send_and_receive(
        self,
        command: str,
        expect_confirmation: bool = True,
        expect_response: bool = False,
    ) -> Union[None, str]:
        """
        Send a command to the tango desktop and receive the response.

        .. warning::
            Most functions acquire a lock before sending a command to the tango desktop, this is to prevent
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

        Returns:
        --------
        response: str or None
            The response of the tango desktop.

        Raises:
        -------
        HardwareNotConnectedError:
            If the tango desktop is not connected.
        ValueError:
            If the command caused an error
        """
        if self._ser is None:
            raise HardwareNotConnectedError("The tango desktop is not connected.")
        elif self._em_event.is_set():
            return None  # Do nothing to give other classes a chance to stop the emergency stop

        # Check if the command has a carriage return
        if command[-2:] != "\r":
            command += " \r"

        self._ser.reset_input_buffer()  # Empty the serial buffer
        self._ser.write(command.encode())  # Send the command

        if expect_confirmation or expect_response:
            got_response = False
            etime = time.time() + self._timeout
            while time.time() < etime and not got_response:
                # Check if a confirmation is expected
                time.sleep(0.01)

                if expect_confirmation and not expect_response:
                    if self._message_waiting():
                        resp = self._ser.readline().decode().strip()
                    if resp == "@":
                        continue
                    if resp == "OK...":
                        got_response = True
                    else:
                        raise ValueError(
                            "The command {} was not accepted by the tango desktop and gave response: {}.".format(
                                command, resp
                            )
                        )
                elif expect_response:
                    if self._message_waiting():
                        data_resp = self._ser.readline().decode().strip()
                    if data_resp == "@":
                        continue
                    else:
                        got_response = True

            if not got_response:
                print("The command {} did not receive a response.".format(command))
                raise HardwareNotConnectedError(
                    "The tango desktop did not respond to the command {}.".format(
                        command
                    )
                )

            if expect_response:
                return data_resp
        return None

    def connect(self) -> ...:
        """Connect to the tango desktop."""
        self._lock.acquire()
        if self._em_event.is_set():
            self._lock.release()
            return None
        if self._ser is None:
            # Connect the tango desktop
            self._ser = serial.Serial(
                self._port, self._baud_rate, timeout=self._timeout
            )

            # Check if the right dim and ext modes are set
            resp = self._send_and_receive(
                "?dim", expect_response=True, expect_confirmation=False
            )
            if resp != "1 1 1":
                # Set the dimentions to um
                self._send_and_receive(
                    "!dim 1 1 1", expect_confirmation=False, expect_response=False
                )

            # Disable the autostatus reporting
            self._send_and_receive(
                "!autostatus 0", expect_confirmation=False, expect_response=False
            )

            # Activate extended mode (enables homing)
            resp = self._send_and_receive(
                "?extmode", expect_response=True, expect_confirmation=False
            )
            if resp != "1":
                self._send_and_receive(
                    "!extmode 1", expect_response=False, expect_confirmation=False
                )

            # Activate the software limits so !cal and !rm do not set the limits anymore
            resp = self._send_and_receive(
                "?nosetlimit z", expect_response=True, expect_confirmation=False
            )
            if resp != "1":
                self._send_and_receive(
                    "!nosetlimit z 1", expect_response=False, expect_confirmation=False
                )

            self._spindle_pitch = float(
                self._send_and_receive(
                    "?pitch z", expect_response=True, expect_confirmation=False
                )
            )
        self._lock.release()

    def disconnect(self) -> ...:
        """Disconnect from the tango desktop."""
        if self._em_event.is_set():
            return None  # Do nothing to give other classes a chance to stop the emergency stop

        self._lock.acquire()
        if self._ser is None:
            pass
        else:
            # Make sure nothing is moving
            while self.is_moving():
                pass

            self._ser.close()  # Disconnect the tango desktop
        self._lock.release()

    # STATUS FUNCTIONS
    def is_connected(self) -> bool:
        """Check if the tango desktop is connected."""
        if self._em_event.is_set():
            return None  # Do nothing to give other classes a chance to stop the emergency stop

        self._lock.acquire()
        state = True if self._ser is not None else False
        self._lock.release()
        return state

    def is_moving(self) -> bool:
        """
        Check the status of the axis.

        .. warning::
            This function is mostly used as a support function and does not capture the lock.
            This means that the calling function should capture the lock.

        Possible return states:
        -----------------------
        @: Axis is not moving and ready
        M: Axis is moving
        J: Axis is ready and can also be manually controlled (joystick)
        S: A limit switch is reached and prevents further movement
        A: Oke response after a cal instruction
        D: Oke response after a rm instruction
        E: Error response, move aborted or not executed
        T: Timeout occured
        -: Axis is not enabled or available in the hardware

        Returns:
        --------
        bool:
            True if the axis is moving, False if not.

        Raises:
        -------
        ValueError:
            If the axis responds with E, T or -.
        """
        if self._em_event.is_set():
            return None  # Do nothing to give other classes a chance to stop the emergency stop

        resp = self._send_and_receive(
            "sa z", expect_response=True, expect_confirmation=False
        )
        if resp in ["E", "-", "T"]:
            raise ValueError("The axis responded with: {}".format(resp))
        elif resp == "M":
            state = True
        elif resp in ["@", "J"]:
            state = False
        else:
            raise KeyError("Unknown response: {}".format(resp))
        return state

    # HOMING FUNCTIONS
    def home(self) -> ...:
        """
        Home the tango desktop.

        .. warning::

            This function assumes that there is only one snapshot position saved on the tango desktop.
            otherwise it will move to the first snapshot position in the snapshot array.

        """
        if self._em_event.is_set():
            return None
        self._lock.acquire()

        # Could not find the homing function so move to zero position
        self._send_and_receive(
            "!moa z 0", expect_response=False, expect_confirmation=False
        )
        self._lock.release()

    # MOVEMENT FUNCTIONS
    def start_jog(self, direction: Union[str, int]) -> ...:
        """Start a continuous jog in the given direction."""
        if self._em_event.is_set():
            return None
        if direction not in ["+", "-"]:
            raise ValueError("The direction {} is not allowed.".format(direction))

        self._lock.acquire()
        if self._current_speed is None:
            self._current_speed = (
                self.speed
            )  # Should already be set but just to be sure

        rev_per_s = self._current_speed * self._spindle_pitch
        self._send_and_receive(
            "!speed z {}{}".format(direction, rev_per_s),
            expect_response=False,
            expect_confirmation=False,
        )
        self._lock.release()

    def stop_jog(self) -> None:
        """Stop the continuous jog."""
        self._lock.acquire()
        self._send_and_receive(
            "!speed z 0", expect_response=False, expect_confirmation=False
        )
        self._lock.release()

    def move_to(self, position: Union[float, int]) -> ...:
        """Move the tango desktop to the given position."""
        if self._em_event.is_set():
            return None
        self._lock.acquire()
        self._send_and_receive(
            "!moa z {}".format(position),
            expect_response=False,
            expect_confirmation=False,
        )
        self._lock.release()

    def move_by(self, distance: Union[float, int]) -> ...:
        """Move the tango desktop by the given distance."""
        if self._em_event.is_set():
            return None
        self._lock.acquire()
        self._send_and_receive(
            "!mor z {}".format(distance),
            expect_response=False,
            expect_confirmation=False,
        )
        self._lock.release()

    def emergency_stop(self) -> ...:
        """Stop the tango desktop."""
        # Stop all moves
        self._send_and_receive(
            "!stopaccel", expect_response=False, expect_confirmation=False
        )
        # Stop all other commands
        self._send_and_receive(
            "!stop", expect_response=False, expect_confirmation=False
        )
        self._ser.close()
        self._em_event.set()


if __name__ == "__main__":
    import configparser
    import time

    config = configparser.ConfigParser()
    config.read("..\configs\config.ini")
    tango = TangoDesktop(id="F", settings=config)
    tango.connect()
    print("Position: {}".format(tango.position))
    print("Speed: {}".format(tango.speed))
    print("Acceleration: {}".format(tango.acceleration))
    tango.move_by(10000)  # Move 10mm up
    print("Is moving: {}".format(tango.is_moving()))
    tango.move_to(10)
    while tango.is_moving():
        pass
    print("Is moving: {}".format(tango.is_moving()))

    # Test jogging
    tango.start_jog("-")
    time.sleep(1)
    tango.stop_jog()

    tango.disconnect()
