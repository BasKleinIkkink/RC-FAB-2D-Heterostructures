from pylablib.devices.Thorlabs.kinesis import KinesisPiezoMotor, list_kinesis_devices, TPZMotorDriveParams, TPZMotorJogParams
from typing import Union
from typeguard import typechecked
from ..configs.settings import Settings
import threading as tr

try:
    from .base import HardwareNotConnectedError
except ImportError:
    from base import HardwareNotConnectedError


class KIM101():
    """Class to control communication with the KIM101 piezocontroller."""
    _controller = None
    _connected = False
    _type = 'KIM101'

    @typechecked
    def __init__(self, settings : Settings) -> None:
        """
        Initialize the KIM101.
        
        Parameters
        ----------
        settings : Settings
            The settings to use.

        Raises
        ------
        HardwareNotConnectedError
            If the KIM101 is not connected.
        """
        self._settings = settings
        self._serial_nr = self._settings.get(self._type+'.DEFAULT')
        self._lock = tr.Lock()
        if self._serial_nr == 'None':
            raise HardwareNotConnectedError('It could not be determined if the device is connected because of missing serial nr in config.')

        # Check if the controller is connected.
        connected_devices = list_kinesis_devices()
        device_found = False
        for connection in connected_devices:
            if connection[0] == self._serial_nr:
                device_found = True
                break

        if not device_found:
            print('The connected deviced: {}'.format(list_kinesis_devices()))
            raise HardwareNotConnectedError('The external controller is not connected.')

    # CONNECTION FUNCTIONS
    def connect(self) -> None:
        """Connect the KIM101."""
        self._lock.acquire()
        self._controller = KinesisPiezoMotor(self._serial_nr)
        self._lock.release()

    def disconnect(self) -> None:
        """Disconnect the KIM101."""
        raise NotImplementedError()

    def emergency_stop(self) -> None:
        """Stop all the connected piezos and disconnect the controller."""
        self._lock.acquire()
        for i in range(4):
            self._controller.stop(channel=i)
        self._lock.release()

    # STATUS FUNCTIONS
    @typechecked
    def is_connected(self) -> bool:
        """
        Check if the KIM101 is connected.
        
        Returns
        -------
        bool
            True if the KIM101 is connected.
        """
        self._lock.acquire()
        if self._connected:
            state = self._controller.is_connected()
        else:
            state = False
        self._lock.release()
        return state

    @typechecked
    def is_moving(self, channel : int) -> bool:
        """
        Check if the piezo is moving.
        
        Parameters
        ----------
        channel : int
            The channel of the piezo to check.
        
        Returns
        -------
        bool
            True if the piezo is moving, False otherwise.

        """
        self._lock.acquire()
        state = self._controller.is_moving(channel=channel)
        self._lock.release()
        return state

    @typechecked
    def get_position(self, channel : int) -> Union[float, int]:
        """
        Get the position of the piezo.
        
        Return list of status strings, which can include ``"sw_fw_lim"`` (forward limit switch reached), ``"sw_bk_lim"`` (backward limit switch reached),
        ``"moving_fw"`` (moving forward), ``"moving_bk"`` (moving backward), ``"jogging_fw"`` (jogging forward), ``"jogging_bk"`` (jogging backward),
        ``"homing"`` (homing), ``"homed"`` (homing done), ``"tracking"``, ``"settled"``,
        ``"motion_error"`` (excessive position error), ``"current_limit"`` (motor current limit exceeded), or ``"enabled"`` (motor is enabled).
        
        Parameters
        ----------
        channel : int
            The channel of the piezo to check.

        Returns
        -------
        float, int
            The position of the piezo.

        """
        self._lock.acquire()
        pos = self._controller.get_position(channel=channel)
        self._lock.release()
        return pos

    @typechecked
    def _wait_move(self, channel : int) -> None:
        """
        Wait until the piezo is not moving anymore.
        
        Parameters
        ----------
        channel : int
            The channel of the piezo to check.

        Returns
        -------
        bool
            True if the piezo is not moving anymore, False otherwise.

        """
        self._lock.acquire()
        self._controller.wait_move(channel=channel)
        self._lock.release()

    # JOG AND DRIVE PARAMETERS
    @typechecked
    def setup_jog(self, velocity : Union[float, int, None]=None, 
                  acceleration : Union[float, int, None]=None) -> None:
        """
        Set the jog paramters of the piezo.
        
        Parameters
        ----------
        velocity : float, int, None
            The velocity of the piezo in um/s. If None, the velocity is not changed.
        acceleration : float, int, None
            The acceleration of the piezo in um/s^2. If None, the acceleration is not changed.
        """
        self._lock.acquire()
        self._controller.setup_jog(velocity=velocity, acceleration=acceleration)
        self._lock.release()

    @typechecked
    def get_jog_parameters(self) -> dict:
        """
        Get the jog parameters of the piezo.
        
        Returns
        -------
        dict
            The jog parameters of the piezo. Velpocity (vel) and acceleration (acc) 
            are in um/s and um/s^2.
        """
        self._lock.acquire()
        params = self._controller.get_jog_parameters()
        self._lock.release()
        return {'step_size': params[1], 'vel': params[3], 'acc': params[4]}

    @typechecked
    def setup_drive(self, max_voltage : Union[float, int, None]=None, 
                    velocity : Union[float, int, None]=None, 
                    acceleration : Union[float, int, None]=None) -> None:
        """
        Set the drive parameters of the piezo.
        
        The drive parameters are used for detemining the movement behavoir when moving by relative or absolute positioning.
        
        Parameters
        ----------
        max_voltage : float, int, None
            The maximum voltage of the piezo in V. If None, the max voltage is not changed.
        velocity : float, int, None
            The velocity of the piezo in um/s. If None, the velocity is not changed.
        acceleration : float, int, None
            The acceleration of the piezo in um/s^2. If None, the acceleration is not changed.
        """
        self._lock.acquire()
        self._controller.setup_drive(max_voltage=max_voltage, velocity=velocity, acceleration=acceleration,)
        self._lock.release()
    
    @typechecked
    def get_drive_parameters(self) -> dict:
        """
        Get the drive parameters of the piezo.
        
        The drive parameters are used for detemining the movement behaviour when moving by relative or absolute positioning.
        
        Returns
        -------
        dict
            The drive parameters of the piezo. Velocity (vel) and acceleration (acc)
        """
        self._lock.acquire()
        params = self._controller.get_drive_parameters()
        self._lock.release()
        return {'vel': params[1], 'acc': params[2]}

    # MOVEMENT FUNCTIONS
    @typechecked
    def start_jog(self, channel : int, direction : Union[str, int, bool], kind : str='continuous') -> None:
        """
        Start a jog.
        
        .. attention:: 
            The jog has to be terminated by the stop method.

        If ``kind=="continuous"``, simply start motion in the given direction at the standard jog speed
        until either the motor is stopped explicitly, or the limit is reached.
        If ``kind=="builtin"``, use the built-in jog command, whose parameters are specified by :meth:`get_jog_parameters`.
        Note that ``kind=="continuous"`` is still implemented through the builtin jog, so it changes its parameters;
        hence, afterwards the jog parameters need to be manually restored.
        
        Parameters
        ----------
        channel : int
            The channel of the piezo to move.
        direction : str, int, bool
            The direction of the jog. Can be ``"forward"``, ``"backward"``, ``1``, ``-1``, ``True``, or ``False``.
        kind : str
            The kind of the jog. Can be ``"continuous"`` or ``"builtin"``.
        """
        self._lock.acquire()
        self._controller.jog(direction=direction, kind=kind, channel=channel)
        self._lock.release()

    def stop_jog(self, channel : Union[None, int]=None) -> None:
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

    @typechecked
    def move_to(self, channel : int, position : Union[float, int], 
                wait_until_done : bool=True) -> None:
        """
        Move one of the connected piezos.
        
        Position is the distance in steps from the zero point (home).

        Parameters
        ----------
        channel : int
            The channel of the piezo to move.
        position : int
            The position to move to (in steps).
        wait_until_done : bool
            If True, wait until the movement is done.
        """
        self._lock.acquire()
        self._controller.move_to(position=position, channel=channel)
        if wait_until_done:
            self._wait_move(channel=channel)
        self._lock.release()

    @typechecked
    def move_by(self, channel : int, distance : Union[float, int], 
                wait_until_done : bool=True) -> None:
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
        self._controller.move_by(distance=distance, channel=channel)
        if wait_until_done:
            self._wait_move(channel=channel)
        self._lock.release()

    @typechecked
    def stop(self, channel : Union[int, None]=None) -> None:
        """
        Stop one of the connected piezos.
        
        Parameters
        ----------
        channel : int, None
            The channel of the piezo to stop. If None, all piezos are stopped.
        """
        self._lock.acquire()
        if channel is None:
            for i in range(4):
                self._controller.stop(channel=i)
        else:
            self._controller.stop(channel=channel)
        self._lock.release()

    
if __name__ == '__main__':
    from time import sleep
    import configparser
    config = configparser.ConfigParser()
    config.read('..\configs\hardware_config.ini')
    # Connect to the controller.
    controller = KIM101(config)
    controller.connect()

    # Test drive functions.
    drive_params = controller.get_drive_parameters()
    print('original drive settings: {}'.format(drive_params))
    controller.setup_drive(velocity=200, acceleration=40)
    print('new drive settings: {}'.format(controller.get_drive_parameters()))
    controller.move_by(channel=1, distance=1000)
    controller.move_to(channel=1, position=0)

    # Reset the driving params
    controller.setup_drive(velocity=10, acceleration=10)
    print('reset drive settings: {}'.format(controller.get_drive_parameters()))

    # Test jog functions.
    jog_params = controller.get_jog_parameters()
    print('original jog settings: {}'.format(jog_params))
    controller.setup_jog(velocity=20, acceleration=20)
    print('new jog settings: {}'.format(controller.get_jog_parameters()))
    controller.start_jog(channel=2, direction='+')
    sleep(3)
    controller.stop_jog(channel=2)
    controller.start_jog(channel=2, direction='-')
    sleep(3)
    controller.stop_jog(channel=2)

    # Reset the jog params
    controller.setup_jog(velocity=15, acceleration=15)
    print('reset jog settings: {}'.format(controller.get_jog_parameters()))	