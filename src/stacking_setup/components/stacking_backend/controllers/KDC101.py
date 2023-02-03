from pylablib.devices.Thorlabs.kinesis import (
    KinesisMotor,
    list_kinesis_devices,
)
from typing import Union
from typeguard import typechecked
from configparser import ConfigParser
from ..configs.settings import Settings
import threading as tr
import multiprocessing as mp
from ..exceptions import HardwareNotConnectedError


class KDC101:
    """Class to control communication with the KCD101 motorcontroller."""

    _type = "KDC101"
    _connected = False
    _controller = None

    @typechecked
    def __init__(self, settings: Settings, em_event: mp.Event) -> ...:
        """
        Initialize the KCD101.

        Parameters
        ----------
        settings : Settings
            The settings to use.
        em_event : mp.Event
            The emergency event.

        Raises
        ------
        HardwareNotConnectedError
            If the KCD101 is not connected.
        """
        self._lock = tr.Lock()  # To ensure threadsafe serial communication
        self._settings = settings
        self._serial_nr = self._settings.get(self._type + ".DEFAULT", "serial_nr")
        self._em_event = em_event
        if self._serial_nr == "None":
            raise HardwareNotConnectedError(
                "It could not be determined if the device is connected because of missing serial nr in config."
            )

        # Check if the controller is connected.
        connected_devices = list_kinesis_devices()
        device_found = False
        for connection in connected_devices:
            if connection[0] == self._serial_nr:
                device_found = True
                break

        if not device_found:
            print("The connected devices: {}".format(list_kinesis_devices()))
            raise HardwareNotConnectedError("The external controller is not connected.")

    # CONNECTION FUNCTIONS
    def connect(self) -> ...:
        """Connect the KCD101."""
        # Device model PRM1-Z8 is used bcause the PRMTZ8/M is not officially supported by pylablib.
        self._lock.acquire()
        self._controller = KinesisMotor(self._serial_nr, scale="PRM1-Z8")
        self._connected = True
        self._lock.release()

    def disconnect(self) -> ...:
        """Disconnect the KCD101."""
        self._lock.acquire()
        self._controller.stop()
        self._lock.release()

    def emergency_stop(self) -> ...:
        """Stop all the connected motors and disconnect the controller."""
        self._em_event.set()
        self.disconnect()

    # STATUS FUNCTIONS
    @typechecked
    def is_connected(self) -> bool:
        """Check if the KCD101 is connected."""
        self._lock.acquire()
        state = self._connected
        self._lock.release()
        return state

    def is_moving(self) -> bool:
        """
        Check if the motor is moving.

        .. important::
            This function is mostly used as a support function for other functions,
            and does not capture the lock. This means this function alone is not thread safe.

        Returns
        -------
        bool
            True if the motor is moving, False otherwise.
        """
        state = self._controller.is_moving()
        return state

    def get_position(self) -> Union[int, float]:
        """
        Get the position of the motor.

        Returns
        -------
        int, float
            The position of the motor.
        """
        self._lock.acquire()
        pos = self._controller.get_position()
        self._lock.release()
        return pos

    def is_homed(self) -> bool:
        """
        Check if the motor is homed.

        Returns
        -------
        bool
            True if the motor is homed, False otherwise.
        """
        self._lock.acquire()
        state = self._controller.is_homed()
        self._lock.release()
        return state

    def is_homing(self) -> bool:
        """
        Check if the motor is homing.

        .. important::
            This function is mostly used as a support function for other functions,
            and does not capture the lock. This means this function alone is not thread safe.

        Returns
        -------
        bool
            True if the motor is homing, False otherwise.
        """
        state = self._controller.is_homing()
        return state

    # HOMING FUNCTIONS
    def home(self, hold_until_done: bool = False) -> ...:
        """
        Home the motor.

        Parameters
        ----------
        hold_until_done : bool
            If True, the function will wait until the motor is homed.
        """
        if self._em_event.is_set():
            return None
        self._lock.acquire()
        self._controller.home()
        if hold_until_done:
            self._controller.wait_for_home()
        self._lock.release()

    def get_homing_parameters(self) -> dict:
        """
        Get the homing parameters.

        Returns
        -------
        dict
            The homing parameters. Homing velocity (vel) and homing direction (dir).
        """
        self._lock.acquire()
        params = self._controller.get_homing_parameters()
        self._lock.release()
        return {"vel": params[2], "dir": params[0]}

    @typechecked
    def setup_homing(
        self,
        velocity: Union[float, int, None] = None,
        acceleration: Union[float, int, None] = None,
    ) -> ...:
        """
        Set the homing parameters.

        If the value is None, the parameter will not be changed.

        Parameters
        ----------
        velocity : float
            The velocity to home with.
        acceleration : float
            The acceleration to home with.
        """
        self._lock.acquire()
        self._controller.setup_homing(velocity=velocity, acceleration=acceleration)
        self._lock.release()

    # JOG AND DRIVE PARAMETERS
    @typechecked
    def get_drive_parameters(self, scale: bool = True) -> dict:
        """
        Get the drive parameters.

        Parameters
        ----------
        scale : bool
            If True, the parameters will be scaled to the correct units.

        Returns
        -------
        dict
            Dictionary containing the velocity (vel) and acceleration (acc)
        """
        self._lock.acquire()
        # Format the parameters to dict format.
        params = self._controller.get_velocity_params(scale=scale)
        self._lock.release()
        return {"vel": params[2], "acc": params[1]}

    @typechecked
    def setup_drive(
        self,
        velocity: Union[float, int] = None,
        scale: bool = True,
    ) -> ...:
        """
        Set the drive parameters of the rotation plate.

        Parameters
        ----------
        velocity : float
            The velocity to move with.
        acceleration : float
            The acceleration to move with.
        scale : bool
            If True, the parameters will be scaled to the correct units.
        """
        self._lock.acquire()
        self._controller.setup_velocity(
            max_velocity=velocity, acceleration=25, scale=scale
        )
        self._lock.release()

    @typechecked
    def get_jog_parameters(self, scale: bool = True) -> dict:
        """
        Get the jog parameters.

        Parameters
        ----------
        scale : bool
            If True, the parameters will be scaled to the correct units.

        Returns
        -------
        dict
            The jog parameters. Step size, velocity (vel) and acceleration (acc).
        """
        self._lock.acquire()
        params = self._controller.get_jog_params(scale=scale)
        self._lock.release()
        return {"step_size": params[1], "vel": params[2], "acc": params[3]}

    @typechecked
    def setup_jog(
        self,
        velocity: Union[float, int, None] = None,
        scale: bool = True,
    ) -> ...:
        """
        Set the jog parameters of the rotation plate.

        Parameters
        ----------
        velocity : float
            The velocity to move with.
        acceleration : float
            The acceleration to move with.
        scale : bool
            If True, the parameters will be scaled to the correct units.
        """
        self._lock.acquire()
        self._controller.setup_jog(
            max_velocity=velocity, acceleration=25, scale=scale
        )
        self._lock.release()

    # MOVEMENT FUNCTIONS
    @typechecked
    def start_jog(
        self, direction: Union[str, int, bool], kind: str = "continuous"
    ) -> ...:
        """
        Start a jog movement.

        .. attention::
            The jog has to be terminated by the :func:`stop_jog` method.

        Parameters
        ----------
        direction : str
            The direction to move in. Can be forward=1 or + or backward=0 or -.
        kind : str
            The kind of movement. Can be 'continuous' or 'single'.
        """
        self._lock.acquire()
        self._controller.jog(direction=direction, kind=kind)
        self._lock.release()

    def stop_jog(self) -> ...:
        """Stop the jog movement."""
        self._lock.acquire()
        self._controller.stop()
        self._lock.release()

    def _wait_move(self):
        # Wait until the movement is done but keep checking the error flag
        while True:
            if not self._em_event.is_set():
                if not self._controller.is_moving():
                    break
                else:
                    continue
            else:
                self.emergency_stop()
                break

    def _get_movement_intervals(self, distance: int) -> int:
        """
        Get the amount of intervals that should be moved

        Intervals are used to divide a distance into smaller steps.
        This is done so the emergency flag gan be polled between movements.

        Parameters
        ----------
        distance : int
            The distance to move.

        Returns
        -------
        interval
            The amount of times the check_interval distance should be moved.
        """
        return distance // self._check_interval

    @typechecked
    def rotate_to(
        self,
        position: Union[float, int],
        hold_until_done: bool = True,
        scale: bool = True,
    ) -> ...:
        """
        Move the motor to the given position.

        Parameters
        ----------
        channel : int
            The channel of the motor to move.
        position : float
            The position to move to.
        velocity : float
            The velocity to move with.
        acceleration : float
            The acceleration to move with.
        hold_until_done : bool
            If True, the function will wait until the movement is done.
        """
        pos = self.get_position()
        distance = position - pos
        intervals = self._get_movement_intervals(distance)
        self._lock.acquire()
        for i in range(intervals):
            if self._em_event.is_set():
                self._lock.release()
                self.stop()
                self._lock.acquire()
                break
            self._controller.move_to(position=position, scale=scale)
            if hold_until_done:
                self._wait_move()
        self._lock.release()

    @typechecked
    def rotate_by(
        self,
        distance: Union[float, int],
        hold_until_done: bool = True,
        scale: bool = True,
    ) -> ...:
        """
        Move the motor by the given distance.

        Parameters
        ----------
        channel : int
            The channel of the motor to move.
        distance : float
            The distance to move.
        hold_until_done : bool
            If True, the function will wait until the movement is done.
        """
        intervals = self._get_movement_intervals(distance)
        self._lock.acquire()
        for i in range(intervals):
            if self._em_event.is_set():
                self._lock.release()
                self.stop()
                self._lock.acquire()
                break
            self._controller.move_by(distance=distance, scale=scale)
            if hold_until_done:
                self._wait_move()
        self._lock.release()

    def stop(self) -> ...:
        """Stop the motor."""
        self._lock.acquire()
        self._controller.stop()
        

    def emergency_stop(self) -> ...:
        """
        Emergency stop the motor.

        Parameters
        ----------
        channel : int
            The channel of the motor to stop.
        """
        self._controller.stop(immediate=True)


if __name__ == "__main__":
    from time import sleep
    import configparser

    # Connect to the controller.
    config = configparser.ConfigParser()
    config.read("..\configs\config.ini")
    controller = KDC101(config, "27263640")
    controller.connect()

    # Test drive functions.
    drive_params = controller.get_drive_parameters()
    print("original drive settings: {}".format(drive_params))
    controller.setup_drive(velocity=20, acceleration=15)
    print("new drive settings: {}".format(controller.get_drive_parameters()))
    controller.rotate_by(1000, scale=False)
    controller.rotate_to(25000, scale=False)

    # Reset the driving params
    controller.setup_drive(velocity=10, acceleration=10)
    print("reset drive settings: {}".format(controller.get_drive_parameters()))

    # Test jog functions.
    jog_params = controller.get_jog_parameters()
    print("original jog settings: {}".format(jog_params))
    controller.setup_jog(velocity=20, acceleration=20)
    print("new jog settings: {}".format(controller.get_jog_parameters()))
    controller.start_jog("+")
    sleep(3)
    controller.stop_jog()
    controller.start_jog("-")
    sleep(3)
    controller.stop_jog()

    # Reset the jog params
    controller.setup_jog(velocity=15, acceleration=15)
    print("reset jog settings: {}".format(controller.get_jog_parameters()))

    controller.home()
