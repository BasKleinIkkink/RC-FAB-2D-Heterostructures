import multiprocessing as mp
import threading as tr
import traceback
import functools
import sys
import time
from typeguard import typechecked
from typing import Union
import configparser

try:
    from .gcode_parser import GcodeParser, GcodeAttributeError, GcodeParsingError
    from .hardware.base import NotSupportedError
    from ..stacking_middleware.message import Message
    from .hardware.KDC101 import KDC101
    from .hardware.KIM101 import KIM101
    from .hardware.PIA13 import PIA13
    from .hardware.PRMTZ8 import PRMTZ8
    from .hardware.TangoDesktop import TangoDesktop
    from .hardware.emergency_breaker import EmergencyBreaker
    from ..stacking_middleware.pipeline_connection import PipelineConnection
    from ..stacking_middleware.serial_connection import SerialConnection
    from .configs.settings import Settings
except ImportError:
    from gcode_parser import GcodeParser, GcodeAttributeError, GcodeParsingError
    from hardware.base import NotSupportedError
    from stacking_middleware.message import Message
    from hardware.KDC101 import KDC101
    from hardware.KIM101 import KIM101
    from hardware.PIA13 import PIA13
    from hardware.PRMTZ8 import PRMTZ8
    from hardware.emergency_breaker import EmergencyBreaker
    from stacking_middleware.pipeline_connection import PipelineConnection
    from stacking_middleware.serial_connection import SerialConnection
    from configs.settings import Settings
    

class RepeatedTimer:
    """
    Class to repeat a task every x seconds.
    
    The class is a wrapper around a threading.Timer object and resets
    it every time the function is called.
    """

    def __init__(self, interval : Union[int, float], function : callable, *args, **kwargs) -> None:
        """
        Initiate the timer.
        
        Parameters
        ----------
        interval : float, int
            The interval in seconds.
        function : callable
            The function to repeat.
        args
            The arguments for the function.
        kwargs
            The keyword arguments for the function.
        """
        self._timer = None
        self._interval = interval
        self._function = function
        self._args = args
        self._kwargs = kwargs
        self._is_running = False
        self._next_call = time.time()
        self.start()

    @property
    def interval(self) -> Union[int, float]:
        """
        Get the interval.
        
        Returns
        -------
        float, int
            The interval in seconds.
        """
        return self._interval

    @property
    def is_running(self) -> bool:
        """
        Get the running status.
        
        Returns
        -------
        bool
            True if the timer is running, False otherwise.
        """
        return self._is_running

    
    @property
    def next_call(self) -> Union[int, float]:
        """
        Get the next call.
        
        Returns
        -------
        float, int
            The next call in seconds.
        """
        return self._next_call

    def _run(self) -> None:
        """Run the function."""
        self._is_running = False
        self.start()
        self._function(*self._args, **self._kwargs)

    def start(self) -> None:
        """Wait for the next run."""
        if not self.is_running:
            self._next_call += self._interval
            self._timer = tr.Timer(self.next_call - time.time(), self._run)
            self._timer.setDaemon(True)
            self._timer.start()
            self._is_running = True

    
    def stop(self) -> None:
        """Stop the timer."""
        self._timer.cancel()
        self._timer.join()
        self._is_running = False


def catch_remote_exceptions(wrapped_function : callable) -> callable:
    """
    Catch and propagate the remote exeptions.

    https://stackoverflow.com/questions/6126007/python-getting-a-traceback

    Parameters
    ----------
    wrapped_function : function
        The function to wrap.

    Raises
    ------
    Exception
        The remote exception that should be send to the main process.

    Returns
    -------
    function
        The wrapped function.

    """

    @functools.wraps(wrapped_function)
    def new_function(*args, **kwargs):
        try:
            return wrapped_function(*args, **kwargs)

        except:
            raise Exception(
                "".join(traceback.format_exception(*sys.exc_info())))

    return new_function


class StackingSetupBackend:
    """
    The hardware controller

    Is connected to the main process with a connector. The connector expects data in the form of strings
    or bytes containing the gcode command lines. For the supported commands see the accepted_commands.py file.
    """
    _emergency_breaker = None
    _hardware = None

    def __init__(self, to_main : Union[PipelineConnection, SerialConnection]) -> None:
        """
        Initiate the backend class.

        Parameters
        ----------
        to_main : PipelineConnection, SerialConnection
            The pipe to the main process.
        settings : Settings
           The settings object.
        """
        self._con_to_main = to_main
        self._emergency_stop_event = mp.Event()
        self._shutdown = mp.Event()
        self._settings = Settings()

        # TODO: #10 get the data from the config file
        self._positioning = 'REL'  # Always initiate in relative positining mode

    def _set_logger(self) -> tr.Thread:
        """
        Set the logger.
        
        Set the logger, this has to be done in a function because the class will be pickled and 
        send to another process (logger can't be pickled).

        Returns
        -------
        logger : tr.Thread
            The logger thread.
        """
        import logging  # Import the logger here because it can't be pickled
        logging.basicConfig(level=logging.DEBUG, filename='log.log', 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
        return logging.getLogger(__name__)

    @typechecked
    def _echo(self, func : callable, command_id : str, command : Union[dict, None]=None) -> tuple:
        """
        Echo the command response (error code and msg) to the main process.

        Parameters
        ----------
        func : function
            The function to execute.
        command_id : str
            The command id.
        command : dict, None
            The command.
        *args : list
            The arguments to pass to the function.
        **kwargs : dict
            The keyword arguments to pass to the function.

        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : str
            A message with the result of the command.
        """
        # Wrap the function
        @functools.wraps(func)
        def new_function(*args, **kwargs):
            return func(*args, **kwargs)

        # Send the exit code and msg over the pipe to main
        if command is not None:
            exit_code, msg = new_function(command)
        else:
            exit_code, msg = new_function()

        self._con_to_main.send(Message(exit_code=exit_code, command_id=command_id, 
                msg=str(msg), command=command))

        # Return the exit code and msg
        return exit_code, msg

    # STARTING AND STOPPING
    def _init_emergency_breaker(self) -> EmergencyBreaker:
        """Initiate the emergency breaker."""
        # return EmergencyBreaker(self._emergency_stop_event)
        pass

    def _init_all_hardware(self) -> list:
        """
        Initiate the hardware.
        
        Define the connected hardware controllers.

        Returns
        -------
        hardware : list
            A list of the hardware controllers.
        """
        # Define the connected components.
        _hardware = []
        if self._settings.get('KIM101.DEFAULT', 'enabled'):
            self._piezo_controller = KIM101()

            if self._settings.get('PIA13.X', 'enabled'):
                _hardware.append(PIA13(id='X', channel=1, hardware_controller=self._piezo_controller, settings=self._settings))

            if self._settings.get('PIA13.Y', 'enabled'):
                _hardware.append(PIA13(id='Y', channel=2, hardware_controller=self._piezo_controller, settings=self._settings))

            if self._settings.get('PIA13.Z', 'enabled'):
                _hardware.append(PIA13(id='Z', channel=3, hardware_controller=self._piezo_controller, settings=self._settings))
        
        if self._settings.get('KDC101.DEFAULT', 'enabled'):
            self._motor_controller = KDC101(settings=self._settings)

            if self._settings.get('PRMTZ8/M.L', 'enabled') and self._settings.get('KDC101.DEFAULT', 'enabled'):
                _hardware.append(PRMTZ8(id='L', hardware_controller=self._motor_controller, settings=self._settings))

        return _hardware

    def _connect_all_hardware(self) -> None:
        """Connect all the hardware in the _hardware list."""
        for axis in self._hardware:
            axis.connect()

    def _disconnect_all_hardware(self) -> None:
        """Disconnect the hardware."""
        for axis in self._hardware:
            axis.disconnect()
    
    def _emergency_stop(self) -> None:
        """Emergency stop the hardware."""
        # Shuts down all connected hardware
        self._emergency_stop_event.set()
        self._disconnect_all_hardware()

    # PROCESSES
    def setup_backend(self) -> None:
        """
        Setup the backend components.
        
        Create the hardware objects and connect them to the main process. 
        
        .. note::
            The hardware has to be connected in a seperate function so the object 
            can be created after the backend class is pickled for the 
            new process (hardware objects contain parts that cant be pickled).
        """
        self._logger = self._set_logger()
        self._emergency_breaker = self._init_emergency_breaker()
        self._hardware = self._init_all_hardware()
        self._connect_all_hardware()
        self._logger.info('Stacking setup initiated with connected hardware: {}'.format(self._hardware))

    def start_backend(self) -> None:
        """Start the hardware controller process."""
        self._controller_process = mp.Process(target=self._controller_loop, args=(self._emergency_stop_event,
                                                                        self._shutdown, self._con_to_main, self._settings,))    
        self._controller_process.set_deamon=True
        self._controller_process.start()

    @catch_remote_exceptions
    @typechecked
    def _controller_loop(self, emergency_stop_event : mp.Event, shutdown_event : mp.Event, 
                        con_to_main : Union[PipelineConnection, SerialConnection], settings : Settings) -> None:
        """
        The main loop of the hardware controller process.

        This loop is responsible for the communication with the main process 
        and the parsing and execution of the commands.

        Parameters
        ----------
        emergency_stop_event : multiprocessing.Event
            The event that is set when the emergency stop is triggered.
        shutdown_event : multiprocessing.Event
            The event that is set when the shutdown is triggered.
        con_to_main : multiprocessing.Pipe
            The pipe to the main process.
        settings : Settings
            The settings object.
        """
        # When starting a process the class is pickled and a new instance is created in the new process.
        # This means that attributes that were changed in the main process are not changed in the new process.
        # To fix this the attributes are set again in the new process.
        self._con_to_main = con_to_main
        self._con_to_main.handshake()
        self._emergency_stop_event = emergency_stop_event
        self._shutdown = shutdown_event
        self.setup_backend()

        # Start the execution loop
        while not emergency_stop_event.is_set() or not shutdown_event.is_set():
            # Check if a new command is available
            if self._con_to_main.message_waiting():
                commands = self._con_to_main.receive() # Read the command

                # Check if the SENTINEL command is in commands
                if isinstance(commands, (list, tuple,)):
                    if self._con_to_main.SENTINEL in commands:
                        # Power off the insturment and close the connection
                        break
                elif commands == self._con_to_main.SENTINEL:
                    # Power off the insturment and close the connection
                    break

                for command in commands:
                    # Excecute all the commands
                    if command is not None:
                        try:
                            parsed_command = GcodeParser.parse_gcode_line(command)  # Parse the command
                        except (GcodeAttributeError, GcodeParsingError) as e:
                            self._con_to_main.send(Message(exit_code=1, msg=str(e), command=command, command_id=''))
                            continue
                        self._execute_command(parsed_command) # Execute the command
                    else:
                        self._con_to_main.send(Message(exit_code=1, msg='Received None command', command=command, command_id=''))

        self._disconnect_all_hardware()
        self._logger.info('Stacking process stopped.')
        self._con_to_main.disconnect()
        
    @typechecked        
    def _execute_command(self, parsed_command : dict) -> None:
        """
        Execute the parsed command dict.

        Parameters
        ----------
        parsed_command : dict
            The parsed command dict.
        
        Returns
        -------
        exit_code : int
            0 if all the commands were executed successfully.
        msg : str
            The error message if any error occured.
        """
        # Placeholder for the exit code
        exit_code = 0

        # Excecute the priority commands first
        if 'M112' in parsed_command.keys():
            exit_code, msg = self._echo(func=self.M112, command_id='M112')
            # Remove the command from the dict
            del parsed_command['M112']

        if 'M999' in parsed_command.keys():
            exit_code, msg = self._echo_(func=self.M999, command_id='M999')
            # Remove the command from the dict
            del parsed_command['M999']

        # Excecute the machine commands (start with M)
        keys = list(parsed_command.keys())
        for command_id in keys:
            if exit_code:
                # There was an error in the previous command
                break

            if command_id[0] != 'M':
                continue
            elif command_id == 'M105':
                # Get the temperature
                exit_code, msg = self._echo(func=self.M105, command_id='M105')
            elif command_id == 'M113':
                # Keep the host alive
                exit_code, msg = self._echo(func=self.M113, command_id='M113', 
                        command=parsed_command[command_id])
            elif command_id == 'M114':
                # Get the position
                exit_code, msg = self._echo(func=self.M114, command_id='M114')
            elif command_id == 'M154':
                # Position autoreport
                exit_code, msg = self._echo(func=self.M154, command_id='M154', 
                        command=parsed_command[command_id])
            elif command_id == 'M155':
                # Temperature autoreport
                exit_code, msg = self._echo(func=self.M155, command_id='M155', 
                        command=parsed_command[command_id])
            elif command_id == 'M811':
                # Use jogging
                exit_code, msg = self._echo(func=self.M811, command_id='M811',
                        command=parsed_command[command_id])
            elif command_id == 'M812':
                # Set driving parameters
                exit_code, msg = self._echo(func=self.M812, command_id='M812',
                        command=parsed_command[command_id])
            else:
                exit_code = 1
                self._con_to_main.send(Message(exit_code=exit_code, msg='Unknown command', command_id=command_id))

            # Delete the command from the list
            keys.remove(command_id)

        # Check wich keys are not in the list anymore and remove these from the command dict
        keys_left = list(parsed_command.keys())
        for key in keys_left:
            if key not in keys:
                del parsed_command[key]

        # Excecute the movement commands
        for command_id in keys:
            if exit_code:
                # There was an error in one of the previous commands
                break

            if command_id == 'G0':
                # Move to all the given axes at the same time
                exit_code, msg = self._echo(func=self.G0, command_id='G0', 
                        command=parsed_command[command_id])
            elif command_id == 'G1':
                # Make an arc to the given position
                exit_code, msg = self._echo(func=self.G1, command_id='G1', 
                        command=parsed_command[command_id])
            elif command_id == 'G28':
                # Home all axes
                exit_code, msg = self._echo(func=self.G28, command_id='G28')
            elif command_id == 'G90':
                # Set to absolute positioning
                exit_code, msg = self._echo(func=self.G90, command_id='G90')
            elif command_id == 'G91':
                # Set to relative positioning
                exit_code, msg = self._echo(func=self.G91, command_id='G91')	
            else:
                exit_code = 1
                self._con_to_main.send(Message(exit_code=exit_code, msg='Unknown command', 
                    command_id=command_id))

            # Delete the command from the dict
            keys.remove(command_id)

        # Check wich keys are not in the list anymore and remove these from the command dict
        keys_left = list(parsed_command.keys())
        for key in keys_left:
            if key not in keys:
                del parsed_command[key]


        if not exit_code and len(parsed_command) != 0:
            # Send the error message to the main process
            msg = Message(exit_code=1, msg='Not all commands were executed: {}'.format(parsed_command), command=parsed_command, command_id='None')
            self._con_to_main.send(msg)
        
    # MOVEMENT FUNCTIONS
    @typechecked
    def G0(self, movements : dict) -> tuple:
        """
        Move to the given axis in a lineair motion.

        Parameters
        ----------
        movements : dict
            A dictionary with the movements for each axis.

        Returns
        -------
        exit_code : int
            0 if the command was executed successfully.
        msg : str
            The error message if any error occured.
        """
        axis_to_move = list(movements.keys())
        for axis in self._hardware:
            if axis.id in movements.keys():
                # This axis should move
                # Check if the move is relative or absolute
                if self._positioning == 'REL':
                    # Relative move
                    try:
                        axis.move_by(movements[axis.id])
                        axis_to_move.remove(axis.id)
                    except NotSupportedError as e:
                        # Relative linear movement not supported for this axis
                        self._logger.critical(e)
                elif self._positioning == 'ABS':
                    # Absolute move
                    try:
                        axis.move_to(movements[axis.id])
                        axis_to_move.remove(axis.id)
                    except NotSupportedError as e:
                        # Absolute linear movement not supported for this axis
                        self._logger.critical(e)
                else:
                    raise Exception('This point should never be reached.')
        
        if len(axis_to_move) != 0:
            # There are still movements left
            return 1, 'Not all movements were executed: {}'.format(axis_to_move)
        else:
            return 0, None

    @typechecked
    def G1(self, movements : dict) -> tuple:
        """
        Make an arc to the given position (rotate).

        Parameters
        ----------
        movements : dict
            A dictionary with the movements for each axis.

        Returns
        -------
        exit_code : int
            0 if the command was executed successfully.
        msg : str
            The error message if any error occured.
        """
        axis_to_move = list(movements.keys())
        for axis in self._hardware:
            if axis.id in movements.keys():
                # This axis should move
                # Check if the move is relative or absolute
                if self._positioning == 'REL':
                    # Relative move
                    try:
                        axis.rotate_by(movements[axis.id])
                        axis_to_move.remove(axis.id)
                    except NotSupportedError as e:
                        # Relative linear movement not supported for this axis
                        self._logger.critical(e)
                        return 1, e
                elif self._positioning == 'ABS':
                    # Absolute move
                    try:
                        axis.rotate_to(movements[axis.id])
                        axis_to_move.remove(axis.id)
                    except NotSupportedError as e:
                        # Absolute linear movement not supported for this axis
                        self._logger.critical(e)
                        return 1, e.message
                else:
                    raise Exception('This point should never be reached.')
        
        if len(axis_to_move) != 0:
            # There are still movements left
            return 1, 'Not all movements were executed: {}'.format(axis_to_move)
        else:
            return 0, None

    def G28(self) -> tuple:
        """
        Home all axes that need homing.
        
        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : str
            A message with the result of the command.
        """
        for axis in self._hardware:
            try:
                axis.home()
            except NotSupportedError:
                pass

        return 0, None

    def G90(self) -> tuple:
        """
        Set to absolute positioning.
        
        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : str
            A message with the result of the command.
        """
        if self._positioning == 'REL':
            self._positioning = 'ABS'
            return 0, 'Now in absolute positioning mode.'
        else:
            return 0, 'Already in absolute positioning mode.'

    def G91(self) -> tuple:
        """
        Set to relative positioning.
    
        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : str
            A message with the result of the command.
        """
        if self._positioning == 'ABS':
            self._positioning = 'REL'
            return 0, 'Now in relative positioning mode.'
        else:
            return 0, 'Already in relative positioning mode.'

    # MACHINE FUNCTIONS
    @typechecked
    def M92(self, factors : dict) -> tuple:
        """
        Set the steps per um for the given axis. If no factors are
        given, the current factors are returned.

        IMPORTANT: This function should not be used as the value should 
        be determinded during the calibration of the machine.
        
        Parameters
        ----------
        factors : dict
            A dictionary with the steps per um for each axis that
            should be changed.

        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : str
            A message with the result of the command.
        """
        # Check if the factor list is empty
        if len(factors.keys()) == 0:
            # Return the current steps_per_um values
            current = {}
            for axis in self._hardware:
                try:
                    current[axis.id] = axis.steps_per_um
                except NotSupportedError:
                    pass
            return 0, current

        else:
            axis_to_set = list(factors.keys())
            for axis in self._hardware:
                if axis.id in axis_to_set:
                    axis.steps_per_um = factors[axis.id]
                    axis_to_set.remove(axis.id)

                if len(axis_to_set) == 0: break

            if len(axis_to_set) != 0:
                return 1, 'Not all step factor changes were executed: {} .'.format(axis)
            else:
                return 0, None

    def M105(self) -> tuple:
        """
        Get the temperature report.

        .. note::
            The temperature report is returned in the following format:
            {<axis_id> : {'current' : <current_temperature>, 'target' : <target_temperature>}}
        
        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : str
            A message with the result of the command.

        """
        temperatures = {}
        for axis in self._hardware:
            try:
                part_temp = {'current' : axis.temperature,
                             'target' : axis.target_temperature}
                temperatures[axis.id] = part_temp
            except NotSupportedError:
                pass
        
        return 0, temperatures

    def M112(self) -> tuple:
        """Emergency stop."""
        self._emergency_stop()
        return 0, None

    @typechecked
    def M113(self, interval : dict) -> tuple:
        """
        Keep the host alive

        If the interval None is given the current settings will be returned if a 
        keep alive timer has been set. Otherwise the keep alive timer will be
        set to the given amount of seconds. If 0 is given the timer is disabled.
        
        Parameters
        ----------
        interval : dict
            A dict with the interval to set under key 'S'.
        
        Returns
        -------
        exit_code : int
            0 if the command was executed successfully, 1 otherwise.
        msg : str
            If no error the set interval in seconds, otherwise an error message.
        """
        if 'S' not in interval.keys():
            # Return the current interval
            try:
                interval = self._keep_host_alive_timer.interval
            except AttributeError:
                return 1, 'No keep alive interval set.'

            return 0, interval
        elif interval['S'] == 0:
            # Disable the keep alive timer
            self._keep_host_alive_timer.stop()
            return 0, None
        else:
            self._keep_host_alive_timer = RepeatedTimer(interval=interval['S'], 
                                                   function=self._keep_host_alive)
            self._keep_host_alive_timer.start()
            return 0, None

    def _keep_host_alive(self) -> None:
        """Send a keep alive message to the host. (support function for M113)"""
        if self._con_to_main.is_connected:
            self._con_to_main.send(Message(exit_code=0, msg='The backend is still alive!!', command_id='M113'))
        else:
            self._keep_host_alive_timer.stop()

    def M114(self) -> tuple:
        """
        Get the current positions.

        .. note::
            The positions are returned in the following format:
            {<axis_id> : <position>, ...}
        
        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : dict
            A dict with the positions of the axes.
        """
        positions = {}
        for axis in self._hardware:
            try:
                positions[axis.id] = axis.position
            except NotSupportedError:
                pass

        return 0, positions

    def M999(self) -> tuple:
        """
        Reset the machine.
        
        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : str
            A message with the result of the command.
        """
        self._disconnect_all_hardware()  # Try to disconnect all the hardware.
        self._emergency_stop_event.clear()  # Reset the emergency stop flag.
        self._shutdown = False  # Reset the shutdown flag.
        self._initiate_all_hardware()  # Reconnect all the hardware.
        return 0, None

    def M154(self, interval):
        """
        Auto position report.

        If the interval None is given the current settings will be returned if a 
        auto position update has been set. Otherwise the auto position timer will be
        set to the given amount of seconds. If 0 is given the timer is disabled.

        .. note::
            The data is returned in the msg variable in the following format:
            {<axis_id> : <position>, ...}
        
        Parameters
        ----------
        interval : dict
            A dict with the interval to set under key 'S'.
        
        Returns
        -------
        exit_code : int
            0 if the command was executed successfully, 1 otherwise.
        msg : str
            If no error the set interval in seconds, otherwise an error message.
        """
        if 'S' not in interval.keys():
            # Return the current interval
            try:
                interval = self._auto_position_timer.interval
            except AttributeError:
                return 1, 'Auto position update interval set.'

            return 0, interval
        elif interval['S'] == 0:
            # Disable the keep alive timer
            self._auto_position_timer.stop()
            return 0, None
        else:
            self._auto_position_timer = RepeatedTimer(interval=interval['S'], 
                                                function=self._auto_position_report)
            self._auto_position_timer.start()
            return 0, None

    def _auto_position_report(self) -> None:
        """Send a position update to the host. (support function for M154)"""
        exit_code, positions = self.M114()
        if self._con_to_main.is_connected:
            if exit_code == 0:
                self._con_to_main.send(Message(exit_code=0, msg=positions, command_id='M154', command=''))
            else:
                self._con_to_main.send(Message(exit_code=1, msg='Could not get positions.', command_id='M154', command=''))
        else:
            self._auto_position_timer.stop()

    def M155(self, interval):
        """
        Auto temperature report.

        If the interval None is given the current settings will be returned if a 
        auto temperature update has been set. Otherwise the auto temperature timer will be
        set to the given amount of seconds. If 0 is given the timer is disabled.

        .. note::
            The data is returned in the msg variable in the following format:
            {<axis_id> : {'current' : <current_temperature>, 'target' : <target_temperature>}, ...}
        
        Parameters
        ----------
        interval : dict
            A dict with the interval to set under key 'S'.
        
        Returns
        -------
        exit_code : int
            0 if the command was executed successfully, 1 otherwise.
        msg : str
            If no error the set interval in seconds, otherwise an error message.
        """
        if 'S' not in interval.keys():
            # Return the current interval
            try:
                interval = self._auto_temperature_timer.interval
            except AttributeError:
                return 1, 'Auto temperature update interval set.'

            return 0, interval
        elif interval['S'] == 0:
            # Disable the keep alive timer
            self._auto_temperature_timer.stop()
            return 0, None
        else:
            self._auto_temperature_timer = RepeatedTimer(interval=interval['S'], 
                                                function=self._auto_temperature_report)
            self._auto_temperature_timer.start()
            return 0, None

    def _auto_temperature_report(self) -> None:
        """Send a position update to the host. (support function for M154)"""
        exit_code, positions = self.M105()
        if self._con_to_main.is_connected:
            if exit_code == 0:
                self._con_to_main.send(Message(exit_code=0, msg=positions, command_id='M155', command=''))
            else:
                self._con_to_main.send(Message(exit_code=1, msg='Could not get positions.', command_id='M155', command=''))
        else:
            self._auto_temperature_timer.stop()

    # JOGGING AND DRIVING FUNCTIONS
    def M811(self, command : dict) -> tuple:
        """
        Jog the given axis at at the set speed.

        Will jog the given axis if the axis value is one and stop moving if the value is 0.
        
        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : str
            A message with the result of the command.
        """
        for axis in self._hardware:
            if axis.id in command.keys():
                if abs(command[axis.id]) == 1:
                    if command[axis.id] < 0:
                        dir = '-'
                    else:
                        dir = '+'
                    try:
                        axis.start_jog(dir)
                    except NotSupportedError:
                        pass
                elif command[axis.id] == 0:
                    try:
                        axis.stop_jog()
                    except NotSupportedError:
                        pass
        return 0, None

    @typechecked
    def M812(self, command : dict) -> tuple:
        """
        Macro function to set the driving parameters for the stepper or actuator.

        Parameters
        ----------
        command : dict
            A dictionary with the axis id(s) and the speed and acceleration to set. If only 
            specific settings should be changed leave the other settings out of the dict
        
        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : str
            A message with the result of the command.
        """
        for axis in self._hardware:
            if axis.id in command.keys():
                try:
                    axis.speed = command[axis.id]
                except KeyError:
                    print('No speed given for axis {}'.format(axis.id))
                    pass

        return 0, None

    def M813(self, command : dict) -> tuple:
        """
        Custom function to set the acceleration of the given axes.

        .. attention::
            This function is currently not supported by the backend.

        Parameters
        ----------
        command : dict
            A dictionary with the axis id(s) and the acceleration to set
        
        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : str
            A message with the result of the command.
        """
        for axis in self._hardware:
            if axis.id == axis:
                try:
                    axis.acceleration = command[axis.id]
                except KeyError:
                    pass

        return 0, None