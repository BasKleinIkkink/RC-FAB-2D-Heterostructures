import multiprocessing as mp
import threading as tr
from gcode_parser import GcodeParser
from stacking_setup.hardware.exceptions import NotSupportedError
from .mp_tools import catch_remote_exceptions, pipe_com
from .hardware.PIA13 import PIA13
from .hardware.KIM101 import KIM101
from .hardware.KDC101 import KDC101
from .hardware.PRMTZ8 import PRMTZ8


class StackingSetup():
    """
    The hardware controller

    Is connected to the main process with a pipe. The pipe expects data in the form of strings
    ir bytes containing the gcode command lines. For the supported commands see the gcode_parser function.
    """

    def __init__(self, pipe_to_main):
        self._pipe_lock = tr.Lock()  # Lock to make the pipe thread safe
        self._pipe_to_main = pipe_to_main
        self._emergency_stop_event = mp.Event()
        self._shutdown = False

        # TODO: #10 get the data from the config file
        self._positioning = 'REL'  # Always initiate in relative positining mode

        # Define the connected hardware.
        piezo_controller = KIM101()
        rotation_controller = KDC101()
        self._hardware = [PIA13('X', 1, piezo_controller), 
                          PIA13('Y', 2, piezo_controller), 
                          PIA13('Z', 3, piezo_controller),
                          PRMTZ8('R', rotation_controller)]

    # STARTING AND STOPPING
    def start_controller(self):
        """Start the hardware controller process."""
        self._controller_process = mp.Process(target=self._controller_loop, args=(self._emergency_stop_event,))
        self._controller_process.start()

    def _initiate_all_hardware(self):
        """Connect and initiate the hardware."""
        for axis in self._hardware:
            axis.connect()

    def _disconnect_all_hardware(self):
        """Disconnect the hardware."""
        for axis in self._hardware:
            axis.disconnect()
    
    def _emergemcy_stop(self):
        """Emergency stop the hardware."""
        # Shuts down all connected hardware
        self._disconnect_all_hardware()

    # PROCESSES
    @catch_remote_exceptions
    def _controller_loop(self, emergency_stop_event):
        """The main loop of the hardware controller process."""
        while not emergency_stop_event.is_set():
            # Check if a new command is available
            if self._pipe_to_main.poll():
                command = self._pipe_to_to_main.recv() # Read the command
                parsed_command = GcodeParser.parse_gcode_line(command)  # Parse the command
                self._execute_command(parsed_command) # Execute the command

            if self.shutdown:
                break

        if not self._emergency_stop_event.is_set():
            # Put all the parts in a save position
            raise NotImplementedError('Not implemented')
        else:
            # Emergency stop all the parts
            self._emergemcy_stop()

    def _execute_command(self, parsed_command):
        """
        Execute the parsed command dict.

        Parameters:
        -----------
        parsed_command : dict
            The parsed command dict.
        
        Returns:
        -------
        exit_code : int
            0 if all the commands were executed successfully.
        msg : str
            The error message if any error occured.

        """
        # Excecute the priority commands first
        if 'M112' in parsed_command.keys():
            self._echo(self.M112())
            # Remove the command from the dict
            del parsed_command['M112']

        if 'M999' in parsed_command.keys():
            self._echo_(self.M999())
            # Remove the command from the dict
            del parsed_command['M999']

        # Excecute the machine commands (start with M)
        for command in parsed_command.keys():
            if command[0] != 'M':
                continue
            elif command == 'M0':
                raise NotImplementedError('M0 not implemented.')
            elif command == 'M80':
                # Power on the instrument.
                self._echo(self.M80())
            elif command == 'M81':
                # Power off the instrument.
                self._echo(self.M81())
            elif command == 'M85':
                raise NotImplementedError('M85 not implemented.')
            elif command == 'M92':
                # Set the steps per nm
                raise NotImplementedError('M92 not implemented.')
                self._echo(self.M92(axis, value))
            elif command == 'M105':
                # Get the temperature report.
                self._echo(self.M105())
            elif command == 'M111':
                raise NotImplementedError('M111 not implemented.')
            elif command == 'M112':
                # Emergency stop.
                self.echo(self.M112())
            elif command == 'M113':
                # Keep the host alive
                self._echo(self.M113())
            elif command == 'M114':
                # Get the current position.
                exit_code, msg = self.M114()
            elif command == 'M119':
                raise NotImplementedError('M119 not implemented.')
            elif command == 'M120':
                raise NotImplementedError('M120 not implemented.')
            elif command == 'M121':
                raise NotImplementedError('M121 not implemented.')
            elif command == 'M140':
                raise NotImplementedError('M140 not implemented.')
            elif command == 'M154':
                raise NotImplementedError('M154 not implemented.')
            elif command == 'M155':
                raise NotImplementedError('M155 not implemented.')
            elif command == 'M190':
                raise NotImplementedError('M190 not implemented.')
            elif command == 'M500':
                raise NotImplementedError('M500 not implemented.')
            elif command == 'M501':
                raise NotImplementedError('M501 not implemented.')
            elif command == 'M503':
                # Get the settings.
                self._echo(self.M503())
            elif command == 'M510':
                raise NotImplementedError('M510 not implemented.')
            elif command == 'M511':
                raise NotImplementedError('M511 not implemented.')
            elif command == 'M512':
                raise NotImplementedError('M512 macro not implemented.')
            elif command == 'M810':
                raise NotImplementedError('M810 macro not implemented.')
            elif command == 'M811':
                raise NotImplementedError('M811 macro not implemented.')
            elif command == 'M812':
                raise NotImplementedError('M812 macro not implemented.')
            elif command == 'M813':
                raise NotImplementedError('M813 macro not implemented.')
            elif command == 'M814':
                raise NotImplementedError('M814 macro not implemented.')
            elif command == 'M815':
                raise NotImplementedError('M815 macro not implemented.')
            elif command == 'M816':
                raise NotImplementedError('M816 macro not implemented.')
            elif command == 'M817':
                raise NotImplementedError('M817 macro not implemented.')
            elif command == 'M818':
                raise NotImplementedError('M818 macro not implemented.')
            elif command == 'M819':
                raise NotImplementedError('M819 macro not implemented.')
            elif command == 'M999':
                # Restart the controller from an emergency stop.
                self._echo(self.M999())
            else:
                raise Exception('This point should never be reached.')

            # Delete the command from the dict
            del parsed_command[command]

        # Excecute the movement commands
        for command in parsed_command.keys():
            if exit_code:
                break

            if command == 'G0':
                # Move to all the given axes at the same time
                self._echo(self.G0(parsed_command[command]))
            elif command == 'G1':
                # Make an arc to the given position
                self._echo(self.G1({}))
            elif command == 'G28':
                # Home all axes
                self._echo(self.G28())
            elif command == 'G90':
                # Set to absolute positioning
                self.echo(self.G90())
            elif command == 'G91':
                # Set to relative positioning
                self.echo(self.G91())
            else:
                raise Exception('This point should never be reached.')

            # Delete the command from the dict
            del parsed_command[command]
                
        # Check the exit code
        if exit_code == 1:
            # Command failed
            raise Exception(msg)

        if len(parsed_command) != 0:
            raise Exception('This point should never be reached.')
        
    # MOVEMENT FUNCTIONS
    def G0(self, movements):
        """
        Move to all the given axes at the same time.
        """
        for axis in self._hardware:
            if axis.id in movements.keys():
                # This axis should move
                # Check if the move is relative or absolute
                if 'G91' in movements.keys() or self._positioning == 'REL':
                    # Relative move
                    try:
                        axis.move_by(movements[axis.id])
                        del movements(axis.id)
                    except NotSupportedError as e:
                        # Relative linear movement not supported for this axis
                        return 1, e.message
                elif 'G90' in movements.keys() or self._positioning == 'ABS':
                    # Absolute move
                    try:
                        axis.move_to(movements[axis.id])
                        del movements(axis.id)
                    except NotSupportedError as e:
                        # Absolute linear movement not supported for this axis
                        return 1, e.message
                else:
                    raise Exception('This point should never be reached.')
        
        if len(movements.keys()) != 0:
            # There are still movements left
            return 1, 'Not all movements were executed. {}'.format(movements)
        else:
            return 0, None

    def G1(self, movements):
        """
        Make an arc to the given position (rotate).
        """
        raise NotImplementedError('G1 not implemented.')

    def G28(self):
        """Home all axes."""
        for axis in self._hardware:
            try:
                axis.home()
            except NotSupportedError:
                pass

        return 0, None

    def G90(self):
        """Set to absolute positioning."""
        self._positioning = 'ABS'
        return 0, None

    def G91(self):
        """Set to relative positioning."""
        self._positioning = 'REL'
        return 0, None

    # MACHINE FUNCTIONS
    def M80(self):
        """Power on the instrument."""
        raise NotImplementedError('M80 not implemented.')

    def M81(self):
        """Power off the instrument."""
        raise NotImplementedError('M81 not implemented.')

    def M92(self, axis, value):
        """Set the steps per um for the given axis."""
        for axis in self._hardware:
            if axis.id == axis:
                axis.steps_per_um = value
                return 0, None

        return 1, 'Axis {} not found.'.format(axis)

    def M105(self):
        """Get the temperature report."""
        temperatures = {}
        for axis in self._hardware:
            try:
                temperatures[axis.id] = axis.temperature()
            except NotSupportedError:
                pass

        if len(temperatures.keys()) == 0:
            return 1, 'No temperatures devices with temperature sensors found.'
        
        return 0, temperatures

    def M112(self):
        """Emergency stop."""
        self._emergency_stop()
        return 0, None

    def M113(self, interval):
        """
        Keep the host alive

        If the interval None is given the current settings will be returned if a 
        keep alive timer has been set. Otherwise the keep alive timer will be
        set to the given amount of seconds.
        
        Parameters
        ----------
        interval : int
            The interval in seconds between keep alive messages.
        
        Returns
        -------
        exit_code : int
            0 if the command was executed successfully, 1 otherwise.
        msg : str
            If no error the set interval in seconds, otherwise an error message.

        """
        if isinstance(interval, None):
            try:
                interval = self._keep_host_alive_timer.interval
            except AttributeError:
                return 1, 'No keep alive interval set.'

            return 0, interval
        else:
            self._keep_host_alive_timer = tr.Timer(interval, self._keep_host_alive)
            self._keep_host_alive_timer.start()
            return 0, None

    def _keep_host_alive(self):
        """Send a keep alive message to the host."""
        # With lock method doesnt seem to work.
        self._pipe_lock.acquire()
        self._pipe_to_main.send(b'I am still alive.')
        self._pipe_lock.release()

    def M114(self):
        """Get the current position."""
        positions = {}
        for axis in self._hardware:
            try:
                positions[axis.id] = axis.position
            except NotSupportedError:
                pass

        if len(positions.keys()) == 0:
            return 1, 'No axes found.'
        else:
            return 0, positions

    def M503(self):
        """Report the current settings."""
        raise NotImplementedError('M503 not implemented.')

    def M999(self):
        """Reset the machine."""
        self._disconnect_all_hardware()  # Try to disconnect all the hardware.
        self._emergency_stop_event.clear()  # Reset the emergency stop flag.
        self._shutdown = False  # Reset the shutdown flag.
        self._initiate_all_hardware()  # Reconnect all the hardware.
        return 0, None

    # MACRO FUNCTIONS