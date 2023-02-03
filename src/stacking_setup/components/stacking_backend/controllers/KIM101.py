from pylablib.devices.Thorlabs.kinesis import (
    KinesisPiezoMotor,
    list_kinesis_devices,
)
from typing import Union
from typeguard import typechecked
from ..configs.settings import Settings
import threading as tr
import multiprocessing as mp
from ..exceptions import HardwareNotConnectedError


class KIM101:
    """Class to control communication with the KIM101 piezocontroller."""

    _controller = None
    _connected = False
    _type = "KIM101"

    @typechecked
    def __init__(self, settings: Settings, em_event: mp.Event) -> ...:
        """
        Initialize the KIM101.

        Parameters
        ----------
        settings : Settings
            The settings to use.
        em_event : multiprocessing.Event
            The event to use for emergency stop.

        Raises
        ------
        HardwareNotConnectedError
            If the KIM101 is not connected.
        """
        self._settings = settings
        self._serial_nr = self._settings.get(self._type + ".DEFAULT", "serial_nr")
        self._serial_nr = self._settings.get(self._type + ".DEFAULT", "serial_nr")
        self._check_interval = self._settings.get(
            self._type + ".DEFAULT", "check_interval"
        )
        self._connected = False
        self._lock = tr.Lock()
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
            print("The connected deviced: {}".format(list_kinesis_devices()))
            raise HardwareNotConnectedError("The external controller is not connected.")

    # CONNECTION FUNCTIONS
    def connect(self) -> ...:
        """Connect the KIM101."""
        self._lock.acquire()
        self._controller = KinesisPiezoMotor(self._serial_nr)
        self._connected = True
        self._lock.release()

    def disconnect(self) -> ...:
        """Disconnect the KIM101."""
        raise NotImplementedError()

    # STATUS FUNCTIONS
    @typechecked
    def is_connected(self) -> bool:
        """Check if the KIM101 is connected."""
        self._lock.acquire()
        if self._connected:
            state = True
        else:
            state = False
        self._lock.release()
        return state

    @typechecked
    def is_moving(self, channel: int) -> bool:
        """Check if the piezo on the given channel is moving."""
        state = self._controller.is_moving(channel=channel)
        return state

    @typechecked
    def get_position(self, channel: int) -> Union[float, int]:
        """Get the position of the piezo on the given channel."""
        self._lock.acquire()
        pos = self._controller.get_position(channel=channel)
        self._lock.release()
        return pos

    @typechecked
    def _wait_move(self, channel: int) -> ...:
        """Wait until the piezo is on the given channel is not moving anymore."""
        # Because this function was originally blocking it had to be made non blocking
        # to be able to respond to the emergency stop event.
        while True:
            if not self._em_event.is_set():
                # self._controller.wait_move(channel=channel)
                if not self.is_moving(channel):
                    break
                else:
                    continue
            else:
                # Emergency stop was triggered
                self._controller.stop()
                break


    # JOG AND DRIVE PARAMETERS
    @typechecked
    def setup_jog(
        self,
        channel: int,
        velocity: Union[float, int, None] = None,
    ) -> ...:
        """
        Set the jog paramters of the piezo.

        The jogging parameters are used for jogging in buildin mode.

        .. note::
            This mode is not used in the current implementation.

        Parameters
        ----------
        velocity : float, int, None
            The velocity of the piezo in steps/s. If None, the velocity is not changed.
        """
        if velocity is not None:
            velocity = int(round(velocity, 0))
        self._lock.acquire()
        self._controller.setup_jog(
            velocity=velocity, acceleration=10000, channel=channel
        )
        self._lock.release()

    @typechecked
    def get_jog_parameters(self) -> dict:
        """
        Get the jog parameters of the piezo.

        Returns
        -------
        dict
            The jog parameters of the piezo. Velocity (vel) and acceleration (acc)
            are in um/s and um/s^2.
        """
        self._lock.acquire()
        params = self._controller.get_jog_parameters()
        self._lock.release()
        return {"step_size": params[1], "vel": params[3], "acc": params[4]}

    @typechecked
    def setup_drive(
        self,
        channel: int,
        max_voltage: Union[float, int, None] = None,
        velocity: Union[float, int, None] = None,
    ) -> ...:
        """
        Set the drive parameters of the piezo.

        The drive parameters are used for detemining the movement behavoir
        when moving by relative or absolute positioning.

        .. note::
            This mode is used for driving and jogging in the current implementation.

        Parameters
        ----------
        max_voltage : float, int, None
            The maximum voltage of the piezo in V. If None, the max voltage is not changed.
        velocity : float, int, None
            The velocity of the piezo in steps/s. If None, the velocity is not changed.
        """
        if velocity is not None:
            velocity = int(round(velocity, 0))
        self._lock.acquire()
        self._controller.setup_drive(
            max_voltage=max_voltage,
            velocity=velocity,
            acceleration=10000,
            channel=channel,
        )
        self._lock.release()

    @typechecked
    def get_drive_parameters(self) -> dict:
        """
        Get the drive parameters of the piezo.

        The drive parameters are used for detemining the movement behaviour
        when moving by relative or absolute positioning.

        Returns
        -------
        dict
            The drive parameters of the piezo. Velocity (vel) and acceleration (acc)
        """
        self._lock.acquire()
        params = self._controller.get_drive_parameters()
        self._lock.release()
        return {"vel": params[1], "acc": params[2]}

    # MOVEMENT FUNCTIONS
    @typechecked
    def start_jog(
        self, channel: int, direction: Union[str, int, bool], kind: str = "continuous"
    ) -> ...:
        """
        Start a jog.

        .. Warning::
            The jog has to be terminated by the :meth:`stop_jog method`. If not called
            the piezo can damage itself.

        .. attention::
            If the buildin jog mode is used the the internal drive parameters on the
            controller will be changed. This can lead to unexpected behaviour.

        Parameters
        ----------
        channel : int
            The channel of the piezo to move.
        direction : str, int, bool
            The direction of the jog. Can + or -.
        kind : str
            The kind of the jog. Can be ``"continuous"`` or ``"builtin"``.
        """
        if self._em_event.is_set():
            return None
        self._lock.acquire()
        self._controller.jog(direction=direction, kind=kind, channel=channel)
        self._lock.release()

    def stop_jog(self, channel: Union[None, int] = None) -> ...:
        """
        Stop the jog movement.

        Parameters
        ----------
        channel : int, None
            The channel of the piezo to stop. If None, all channels are stopped.
        """
        self._lock.acquire()
        self._controller.stop(channel=channel)
        self._lock.release()

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
    def move_to(
        self, channel: int, position: Union[float, int], wait_until_done: bool = True
    ) -> ...:
        """
        Move one of the connected piezos.

        Position is the distance in steps from the zero point (home). Due to 
        safety issues the function does not actually call an absolute move
        but a relative move. The position is calculated by subtracting the
        current position from the target position.

        Parameters
        ----------
        channel : int
            The channel of the piezo to move.
        position : int
            The position to move to (in steps).
        wait_until_done : bool
            If True, wait until the movement is done.
        """
        pos = self.get_position(channel=channel)
        self._lock.acquire()
        intervals = self._get_movement_intervals(distance=(pos - position))
        for i in range(intervals):
            if self._em_event.is_set():
                break
            self._controller.move_by(distance=self._check_interval, channel=channel)
            if wait_until_done:
                self._wait_move(channel=channel)
        self._lock.release()

    @typechecked
    def move_by(
        self, channel: int, distance: Union[float, int], wait_until_done: bool = True
    ) -> ...:
        """
        Move one of the connected piezos.

        Distance is the distance in steps to move.

        Parameters
        ----------
        channel : int
            The channel of the piezo to move.
        distance : int
            The distance to move (in steps).
        wait_until_done : bool
            If True, wait until the movement is done.
        """
        
        self._lock.acquire()
        intervals = self._get_movement_intervals(distance)
        for i in range(intervals):
            if self._em_event.is_set():
                break
            # Distance has to be given in steps
            self._controller.move_by(distance=self._check_interval, channel=channel)
            if wait_until_done:
                self._wait_move(channel=channel)
        self._lock.release()

    @typechecked
    def stop(self, channel: Union[int, None] = None) -> ...:
        """
        Stop one or all the piezos.

        Parameters
        ----------
        channel : int, None
            The channel of the piezo to stop. If None, all piezos are stopped.
        """
        self._lock.acquire()
        if channel is None:
            for i in range(4):
                self._controller.stop(channel=i, sync=False)
        else:
            self._controller.stop(channel=channel)
        self._lock.release()

    def emergency_stop(self) -> ...:
        """Stop all connected piezos."""
        self._controller.stop(sync=False)
        self._em_event.set()


if __name__ == "__main__":
    from time import sleep
    import configparser

    config = configparser.ConfigParser()
    config.read("..\configs\hardware_config.ini")
    # Connect to the controller.
    controller = KIM101()
    controller.connect()

    # Test drive functions.
    drive_params = controller.get_drive_parameters()
    print("original drive settings: {}".format(drive_params))
    controller.setup_drive(velocity=200, acceleration=40)
    print("new drive settings: {}".format(controller.get_drive_parameters()))
    controller.move_by(channel=1, distance=1000)
    controller.move_to(channel=1, position=0)

    # Reset the driving params
    controller.setup_drive(velocity=10, acceleration=10)
    print("reset drive settings: {}".format(controller.get_drive_parameters()))

    # Test jog functions.
    jog_params = controller.get_jog_parameters()
    print("original jog settings: {}".format(jog_params))
    controller.setup_jog(velocity=20, acceleration=20)
    print("new jog settings: {}".format(controller.get_jog_parameters()))
    controller.start_jog(channel=2, direction="+")
    sleep(3)
    controller.stop_jog(channel=2)
    controller.start_jog(channel=2, direction="-")
    sleep(3)
    controller.stop_jog(channel=2)

    # Reset the jog params
    controller.setup_jog(velocity=15, acceleration=15)
    print("reset jog settings: {}".format(controller.get_jog_parameters()))
