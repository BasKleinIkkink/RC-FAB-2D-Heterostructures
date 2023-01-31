import multiprocessing as mp
import threading as tr
import time
import logging
from typeguard import typechecked
from typing import Union
from .gcode_parser import GcodeParser, GcodeAttributeError, GcodeParsingError
from .hardware.base import NotSupportedError
from ..stacking_middleware.message import Message
from .hardware.KDC101 import KDC101
from .hardware.KIM101 import KIM101
from .hardware.PIA13 import PIA13
from .hardware.sample_bed import SampleBed
from .hardware.base_stepper import BaseStepper
from .hardware.main_xy_controller import MainXYController
from .hardware.TangoDesktop import TangoDesktop
from ..stacking_middleware.pipeline_connection import PipelineConnection
from ..stacking_middleware.serial_connection import SerialConnection
from .configs.settings import Settings
from queue import Queue
from .repeated_timer import RepeatedTimer
from .catch_remote_exceptions import catch_remote_exceptions



class StackingSetupBackend:
    """
    The main backend class for the stacking setup.

    The class is the main backend class for the stacking setup. It handles the
    communication from the user (frondend) to the hardware. The class is a
    multiprocessing class, so it can be used in a seperate process.

    Used Gcode commands
    -------------------
    - G0 : Lineair movement
    - G1 : Rotational movement
    - G2 : Jogging movement (velocity control)
    - G28 : Home all axes
    - G90 : Set to absolute coordinates
    - G91 : Set to relative coordinates

    - X, Y, Z : Move the mask holder
    - I, J, K : Move the base plate
    - L : Move or control the sample holder

    - M0 : Unconditional stop
    - M105 : Report current temperature
    - M112 : Emergency stop
    - M113 : Keep host alive
    - M114 : Report current position
    - M140 : Set bed temperature
    - M154 : Position auto report
    - M155 : Temperature auto report
    - M190 : Wait for bed temperature
    - M503 : Report settings
    - M510 : Lock machine
    - M511 : Unlock machine
    - M512 : Set password
    - M810 - M819 : G-code macros
    - M999 : STOP restart
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

            .. note::
                All middelware methods that inherit from the base middleware class
                can be used as a as a middleware connection.
        """
        self._con_to_main = to_main
        self._emergency_stop_event = mp.Event()
        self._shutdown = mp.Event()
        self._settings = Settings()
        self._positioning = 'REL'  # Always initiate in relative positioning mode

    def _set_logger(self) -> tr.Thread:
        """
        Set the logger.
        
        .. note::
            The logger has to be set in a seperate function, this has to be done
            because the class will otherwise be pickled when starting the process.
            The logger can't be pickled.

        Returns
        -------
        logger : tr.Thread
            The logger thread.
        """
        logging.basicConfig(level=logging.CRITICAL, filename='log.log', 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
        return logging.getLogger(__name__)

    @typechecked
    def _echo(self, func : callable, command_id : str, command : Union[dict, None]=None) -> ...:
        """
        Echo the command response (error code and msg) to the main process.

        The goal of this function is to excecute actions in a seperate thread and pass the status
        messages to the main process.

        .. attention::
            Actions have to be done in a seperate thread so the backend stays responsive and can 
            respond to the emergency stop command (M112)

        Parameters
        ----------
        func : function
            The function to execute.
        command_id : str
            The command id.
        command : dict, None
            The command.
        """
        if self._emergency_stop_event.is_set():
            self._logger.critical('Cannot execute command {} when the estop is set'.format(command_id))
            return

        # Send the exit code and msg over the pipe to main
        thread = tr.Thread(target=self._threaded_excecution, args=(self._execution_q, func, command_id, command,),
                            daemon=True)
        thread.start()
        return

    def _threaded_excecution(self, q : Queue, func : callable, command_id : str, command : Union[dict, None]=None) -> ...:
        if command is not None:
            exit_code, msg = func(command)
        else:
            exit_code, msg = func()

        if msg is None:
            msg = ''
        elif not isinstance(msg, (str, dict),):
            msg = str(msg)

        q.put(Message(exit_code=exit_code, msg=msg, command_id=command_id, command=command))
        return


    def _init_all_hardware(self, settings : Settings) -> list:
        """
        Initiate the hardware.
        
        Define the connected hardware controllers.

        .. note::
            Just as the emergency_breaker class the emergency breaker has to be initiated in 
            a seperate function because it contains code that cannot be pickled.

        Parameters
        ----------
        settings : Settings
            The  settings.

        Returns
        -------
        hardware : list
            A list of the hardware controllers.
        """
        _hardware = []

        # Initiate the piezos
        if self._settings.get('KIM101.DEFAULT', 'enabled'):
            self._piezo_controller = KIM101(settings=settings, em_event=self._emergency_stop_event)

            if self._settings.get('PIA13.X', 'enabled'):
                _hardware.append(PIA13(id='X', channel=1, hardware_controller=self._piezo_controller, 
                                em_event=self._emergency_stop_event, settings=settings))

            if self._settings.get('PIA13.Y', 'enabled'):
                _hardware.append(PIA13(id='Y', channel=2, hardware_controller=self._piezo_controller, 
                                em_event=self._emergency_stop_event, settings=settings))

            if self._settings.get('PIA13.Z', 'enabled'):
                _hardware.append(PIA13(id='Z', channel=4, hardware_controller=self._piezo_controller, 
                                em_event=self._emergency_stop_event, settings=settings))
        
        # Initiate the sample holder
        if self._settings.get('KDC101.DEFAULT', 'enabled') and settings.get('MAINXYCONTROLLER.DEFAULT', 'enabled'):
            self._motor_controller = KDC101(settings=settings, em_event=self._emergency_stop_event)
            self._base_controller = MainXYController(settings=settings, em_event=self._emergency_stop_event)

            if self._settings.get('SAMPLEHOLDER.L', 'enabled'):
                _hardware.append(SampleBed(id='L', motor_controller=self._motor_controller,
                                        base_controller=self._base_controller,  
                                        em_event=self._emergency_stop_event, settings=settings))

            if self._settings.get('BASESTEPPER.H', 'enabled'):
                _hardware.append(BaseStepper(id='H', controller=self._base_controller,
                                        em_event=self._emergency_stop_event, settings=settings))

            if self._settings.get('BASESTEPPER.J', 'enabled'):
                _hardware.append(BaseStepper(id='J', controller=self._base_controller,
                                        em_event=self._emergency_stop_event, settings=settings))
                
        # Initiate the focus stage
        if self._settings.get('TANGODESKTOP.K', 'enabled'):
            _hardware.append(TangoDesktop(id='K', em_event=self._emergency_stop_event, 
                                        settings=settings))

        # Initiate the base stages

        return _hardware

    def _connect_all_hardware(self) -> ...:
        """Connect all the hardware in the _hardware list."""
        for axis in self._hardware:
            axis.connect()

    def _disconnect_all_hardware(self) -> ...:
        """Disconnect the hardware."""
        for axis in self._hardware:
            try:
                axis.disconnect()
            except NotImplementedError:
                pass
    
    def _emergency_stop(self) -> ...:
        """Emergency stop the hardware."""
        self._logger.critical('Emergency stop initiated')
        self._emergency_stop_event.set()
        for part in self._hardware:
            part.emergency_stop()

    # PROCESSES
    def setup_backend(self, settings : Settings) -> ...:
        """
        Setup the backend components.
        
        Create the hardware objects and connect them to the process. 
        
        .. note::
            The hardware has to be connected in a seperate function so the object 
            can be created after the backend class is pickled for the 
            new process (hardware objects contain parts that cant be pickled).
        """
        self._logger = self._set_logger()
        self._execution_q = mp.Queue()
        self._hardware = self._init_all_hardware(settings)
        self._connect_all_hardware()
        self._logger.info('Stacking setup initiated with connected hardware: {}'.format(self._hardware))

    def start_backend(self) -> ...:
        """
        Start the hardware controller process.
        
        Create a new process and start the controller loop in it.
        """
        self._controller_process = mp.Process(target=self._controller_loop, args=(self._emergency_stop_event,
                                                                        self._shutdown, self._con_to_main, self._settings,))    
        self._controller_process.set_deamon=True
        self._controller_process.start()

    def _check_command_output(self):
        """Check if the command output queue is not empty and send the output to the main process."""
        got_error = False
        while not self._execution_q.empty():
            message = self._execution_q.get()
            if message.exit_code != 0:
                got_error = True
            self._con_to_main.send(message)
        return got_error

    @catch_remote_exceptions
    def _controller_loop(self, emergency_stop_event : mp.Event, shutdown_event : mp.Event, 
                        con_to_main : Union[PipelineConnection, SerialConnection], 
                        settings : Settings) -> ...:
        """
        The main loop of the hardware controller process.

        This loop is responsible for the communication with the main process 
        and the parsing and execution of the commands. This function should 
        not be called directly but through the :func:`start_backend` function.

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
        self._con_to_main = con_to_main
        self._con_to_main.__init_lock__()
        self._con_to_main.handshake()
        self._emergency_stop_event = emergency_stop_event
        self._shutdown = shutdown_event
        self.setup_backend(settings)

        while not emergency_stop_event.is_set() or not shutdown_event.is_set():
            # Check if a new command is available
            if self._con_to_main.message_waiting():
                commands = self._con_to_main.receive()

                # Check if the SENTINEL command is in commands
                if isinstance(commands, (list, tuple,)):
                    if self._con_to_main.SENTINEL in commands:
                        # Power off the insturment and close the connection
                        break
                elif commands == self._con_to_main.SENTINEL:
                    # Power off the insturment and close the connection
                    break

                # Parse and execute the commands
                for command in commands:
                    if command is not None:
                        try:
                            parsed_command = GcodeParser.parse_gcode_line(command) 
                        except (GcodeAttributeError, GcodeParsingError) as e:
                            self._con_to_main.send(Message(exit_code=1, msg=str(e), 
                                        command=command, command_id=''))
                            continue
                        self._execute_command(parsed_command)
                    else:
                        self._con_to_main.send(Message(exit_code=1, msg='Received None command', 
                                            command=command, command_id=''))
            else:
                time.sleep(0.01)


        if self._emergency_stop_event.is_set():
            self._con_to_main.send(Message(exit_code=1, msg='Emergency stop triggered', command_id='M112'))
            self._emergency_stop()
            self._logger.critical('Emergency stop triggered')
        else:
            self._disconnect_all_hardware()
            self._logger.critical('Stacking process stopped.')
            self._con_to_main.disconnect()
        
    @typechecked        
    def _execute_command(self, parsed_command : dict) -> ...:
        """
        Execute the parsed command dict.
        
        The function will always the priority commands first and then the
        machine commands (start with M), then the 'physical' commands (start with G). 
        
        .. attention::
            The priority commands are M112 (emergency stop) and M999 (reset).
            if one of these commands is in the parsed_command dict it will be
            executed first and the rest of the commands will be ignored.
        """
        # Placeholder for the exit code
        exit_code = 0

        # Excecute the priority commands first
        if 'M112' in parsed_command.keys():
            exit_code, msg, = self.M112()
            self._con_to_main.send(Message(exit_code=exit_code, msg='', command_id='M112', command='M112'))
            return

        if 'M999' in parsed_command.keys():
            exit_code, msg = self.M999()
            self._con_to_main.send(Message(exit_code=exit_code, msg='', command_id='M999', command='M999'))
            return

        # Excecute the machine commands (start with M)
        keys = list(parsed_command.keys())
        for command_id in keys:
            if self._check_command_output() or exit_code:
                return

            if command_id[0] != 'M':
                # The command is not a machine command so skip it
                continue
            elif command_id == 'M105':
                # Get the temperature
                self._echo(func=self.M105, command_id='M105')
            elif command_id == 'M113':
                # Keep the host alive
                self._echo(func=self.M113, command_id='M113', 
                        command=parsed_command[command_id])
            elif command_id == 'M114':
                # Get the position
                self._echo(func=self.M114, command_id='M114')
            elif command_id == 'M140':
                # Set the bed temperature
                self._echo(func=self.M140, command_id='M140',
                        command=parsed_command[command_id])
            elif command_id == 'M154':
                # Position autoreport
                self._echo(func=self.M154, command_id='M154', 
                        command=parsed_command[command_id])
            elif command_id == 'M155':
                # Temperature autoreport
                self._echo(func=self.M155, command_id='M155', 
                        command=parsed_command[command_id])
            elif command_id == 'M811':
                # Use jogging
                self._echo(func=self.M811, command_id='M811',
                        command=parsed_command[command_id])
            elif command_id == 'M812':
                # Use jogging
                self._echo(func=self.M812, command_id='M812',
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
            if self._check_command_output() or exit_code:
                # There was an error in one of the previous commands
                break

            if command_id == 'G0':
                # Move to all the given axes at the same time
                self._echo(func=self.G0, command_id='G0', 
                        command=parsed_command[command_id])
            elif command_id == 'G1':
                # Rotate the given axis
                self._echo(func=self.G1, command_id='G1', 
                        command=parsed_command[command_id])
            elif command_id == 'G2':
                # Jog the given axis
                self._echo(func=self.G2, command_id='G2',
                        command=parsed_command[command_id])
            elif command_id == 'G28':
                # Home all axes
                self._echo(func=self.G28, command_id='G28')
            elif command_id == 'G90':
                # Set to absolute positioning
                self._echo(func=self.G90, command_id='G90')
            elif command_id == 'G91':
                # Set to relative positioning
                self._echo(func=self.G91, command_id='G91')	
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

        self._check_command_output()
        if len(parsed_command) != 0:
            message = Message(exit_code=1, msg='Not all commands were executed: {}'.format(parsed_command), 
                            command=parsed_command, command_id='None')
            self._con_to_main.send(message)
        
    # MOVEMENT FUNCTIONS
    def G0(self, movements : dict) -> tuple:
        """
        Move to the given axis in a lineair motion.

        .. note::
            For now this functions does not support simultaneous movement.
            This is because some of the hardware does not support it
            (hold_until_done == True). It could be chanced by figuring out
            out wich axis can move simultaneously and wich can't (for example by class flag), 
            then executing in a safe way, I did not have time to do this...

        Parameters
        ----------
        movements : dict
            A dictionary with the movements for each axis.

        Returns
        -------
        exit_code : int
            0 if the command was executed successfully.
        msg : str
            The error message if any error occured, otherwise None.
        """
        axis_to_move = list(movements.keys())
        for axis in self._hardware:
            if axis.id in movements.keys():
                try:
                    if self._positioning == 'REL':
                        # Relative move
                        axis.move_by(movements[axis.id])
                    elif self._positioning == 'ABS':
                        # Absolute move
                        axis.move_to(movements[axis.id])
                    axis_to_move.remove(axis.id)
                except NotSupportedError:
                    self._logger.debug('Linear movement not supported for axis {}'.format(axis.id))
        
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
            The error message if any error occured, otherwise None.
        """
        axis_to_move = list(movements.keys())
        for axis in self._hardware:
            if axis.id in movements.keys():
                try: 
                    if self._positioning == 'REL':
                        # Relative move
                        axis.rotate_by(movements[axis.id])
                    elif self._positioning == 'ABS':
                        # Absolute move
                        axis.rotate_to(movements[axis.id])
                    axis_to_move.remove(axis.id)
                except NotSupportedError:
                    self._logger.debug('Rotation not supported for axis {}'.format(axis.id))
        
        if len(axis_to_move) != 0:
            # There are still movements left
            return 1, 'Not all movements were executed: {}'.format(axis_to_move)
        else:
            return 0, None

    def G28(self) -> tuple:
        """
        Home all axes that need homing.

        If the axis does not need homing or does not support homing it will be skipped.

        .. note::
            Even though simultaneous homing is way more efficient for now 
            there is no way to do this safely (see :func:`G0`)
            
        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : str
            A message with the result of
        """
        for axis in self._hardware:
            try:
                axis.home()
            except NotSupportedError:
                self._logger.debug('Homing not supported for axis {}'.format(axis.id))

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

        .. important:: 
            This function should not be used as the value should 
            be determinded during the calibration of the machine and set in the
            config file.
        
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
                    self._logger.debug('Steps per um not supported for axis {}'.format(axis.id))
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
                temperatures[axis.id] = {'current' : axis.temperature,
                                        'target' : axis.target_temperature}
            except NotSupportedError:
                self._logger.debug('Temperature not supported for axis {}'.format(axis.id))
        
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
                msg = 'The keep alive timer interval was asked but no timer is set'
                self._logger.debug(msg)
                return 1, msg

            return 0, str(interval)
        elif interval['S'] == 0:
            # Disable the keep alive timer
            try:
                self._keep_host_alive_timer.stop()
            except AttributeError:
                msg = 'Tried to stop the keep alive timer but no timer is set'
                self._logger.debug(msg)
                return 1, msg
            return 0, None
        else:
            self._keep_host_alive_timer = RepeatedTimer(interval=interval['S'], 
                                                   function=self._keep_host_alive)
            self._keep_host_alive_timer.start()
            return 0, None

    def _keep_host_alive(self) -> ...:
        """Send a keep alive message to the host. (support function for M113)"""
        if self._con_to_main.is_connected:
            self._con_to_main.send(Message(exit_code=0, msg='The backend is still alive!!', command_id='M113'))
        else:
            self._keep_host_alive_timer.stop()

    def M114(self) -> tuple:
        """
        Get the current positions.

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
                self._logger.debug('Position not supported for axis {}'.format(axis.id))

        return 0, positions

    def M140(self, command : dict) -> tuple:
        """
        Set the sample bed temperature

        Parameters
        ----------
        command : dict
            A dict with the temperature to set under key 'S'.
        """
        if 'S' not in command.keys():
            return 1, 'No temperature given'
        else:
            for i in self._hardware:
                try:
                    i.target_temperature = command['S']
                except NotSupportedError:
                    self._logger.debug('Temperature not supported for axis {}'.format(i.id))
            return 0, None

    def M999(self) -> tuple:
        """
        Reset the machine.

        .. warning::
            This methos will reset the emergency flag and re-initialize all the hardware.
            It is not recommended to use this method as the emergency flag signals something
            is seriously wrong with the machine and should be fixed before continuing.
        
        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : None
        """
        self._disconnect_all_hardware()  # Try to disconnect all the hardware.
        self._emergency_stop_event.clear()  # Reset the emergency stop flag.
        self._shutdown = False  # Reset the shutdown flag.
        self._initiate_all_hardware()  # Reconnect all the hardware.
        return 0, None

    def M154(self, interval) -> tuple:
        """
        Auto position report.

        The data is returned in the msg variable in the following format:
        {<axis_id> : <position>, ...}

        If the interval None is given the current settings will be returned if a 
        auto position update has been set. Otherwise the auto position timer will be
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
                interval = self._auto_position_timer.interval
            except AttributeError:
                msg = 'The auto position update interval was asked but no timer is set'
                self._logger.debug(msg)
                return 1, msg

            return 0, interval
        elif interval['S'] == 0:
            try:
                # Disable the keep alive timer
                self._auto_position_timer.stop()
                return 0, None
            except AttributeError:
                msg = 'Tried to stop the auto position update timer but no timer was set'
                self._logger.debug(msg)
                return 1, msg
        else:
            self._auto_position_timer = RepeatedTimer(interval=interval['S'], 
                                                function=self._auto_position_report)
            self._auto_position_timer.start()
            return 0, None

    def _auto_position_report(self) -> ...:
        """Send a position update to the host. (support function for M154)"""
        if not self._shutdown.is_set() and not self._emergency_stop_event.is_set() and \
                self._con_to_main.is_connected:
            exit_code, positions = self.M114()
            if exit_code == 0:
                self._con_to_main.send(Message(exit_code=0, msg=positions, command_id='M154', 
                                    command=''))
            else:
                self._con_to_main.send(Message(exit_code=1, msg='Could not get all positions, got {}'.format(positions), 
                                    command_id='M154', command=''))
        else:
            self._auto_position_timer.stop()

    def M155(self, interval) -> tuple:
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
                msg = 'The auto temperature update interval was asked but no timer is set'
                self._logger.debug(msg)
                return 1, msg

            return 0, interval
        elif interval['S'] == 0:
            try:
                # Disable the keep alive timer
                self._auto_temperature_timer.stop()
                return 0, None
            except AttributeError:
                msg = 'Tried to stop the auto temperature update timer but no timer was set'
                self._logger.debug(msg)
                return 1, msg
        else:
            self._auto_temperature_timer = RepeatedTimer(interval=interval['S'], 
                                                function=self._auto_temperature_report)
            self._auto_temperature_timer.start()
            return 0, None

    def _auto_temperature_report(self) -> ...:
        """Send a position update to the host. (support function for M154)"""
        if not self._shutdown.is_set() and not self._emergency_stop_event.is_set() and \
                self._con_to_main.is_connected:
            exit_code, temps = self.M105()
            if exit_code == 0:
                self._con_to_main.send(Message(exit_code=0, msg=temps, command_id='M155', command=''))
            else:
                self._con_to_main.send(Message(exit_code=1, msg='Could not get temperatures.', command_id='M155', command=''))
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
                    self._logger.debug('No speed given for axis {}'.format(axis.id))
                    pass

        return 0, None

    def M813(self, command : dict) -> tuple:
        """
        Unconditionally stop all movement without triggering the emergency event

        Parameters
        ----------
        command : dict
            Not used but added for compatibility with the excecution loop and echo functions

        Returns
        -------
        exit_code : int
            0 if the command was successful, 1 if not.
        msg : str
            A message with the result of the command.
        """
        for axis in self._hardware:
            axis.stop()
        return 0, None