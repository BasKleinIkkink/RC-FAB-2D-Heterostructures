import multiprocessing as mp
import threading as tr
from gcode_parser import GcodeParser
from .mp_tools import catch_remote_exceptions, pipe_com
from .hardware.PIA13 import PIA13


class StackingStage():
    """
    The hardware controller

    Is connected to the main process with a pipe. The pipe expects data in the form of strings
    ir bytes containing the gcode command lines. For the supported commands see the gcode_parser function.
    """
    _priority_commands = ['M112', 'M999']
    _hardware = [PIA13('X', 1), PIA13('Y', 2), PIA13('Z', 3)]

    def __init__(self, pipe_to_main):
        self._pipe_to_main = pipe_to_main
        self._emergency_stop_event = mp.Event()
        self._shutdown = False
        self._positioning = 'REL'  # Always initiate in relative positining mode

    # STARTING AND STOPPING
    def start_controller(self):
        """
        Start the hardware controller process.
        """
        self._controller_process = mp.Process(target=self._controller_loop, args=(self._emergency_stop_event,))
        self._controller_process.start()

    def _initiate_hardware(self):
        """
        Initiate the hardware.
        """
        raise NotImplementedError('Not implemented')

    def _disconnect_hardware(self):
        """
        Disconnect the hardware.
        """
        raise NotImplementedError('Not implemented')
    
    def _emergemcy_stop(self):
        """
        Emergency stop the hardware.
        """
        raise NotImplementedError('Not implemented')

    # PROCESSES AND THREADERS
    @catch_remote_exceptions
    def _controller_loop(self, emergency_stop_event):
        """
        The main loop of the hardware controller process.
        """
        while not emergency_stop_event.is_set():
            # Check if a new command is available
            if self._pipe_to_main.poll():
                # Read the command
                command = self._pipe_to_to_main.recv()
                # Parse the command
                parsed_command = GcodeParser.parse_gcode_line(command)
                # Execute the command
                self._execute_command(parsed_command)

            if self.shutdown:
                break

        if not self._emergency_stop_event.is_set():
            # Put all the parts in a save position
            raise NotImplementedError('Not implemented')
        else:
            # Emergency stop all the parts
            self._emergemcy_stop()

    def _execute_commands(self, parsed_commands):
        """
        Execute the commands.
        """
        for priority in self._priority_commands:
            # Excecute the priority commands first
            if priority in parsed_commands.keys():
                # Excecute the command
                self._execute_command(parsed_commands[priority])

                # Remove the command from the dict
                del parsed_commands[priority]
            
            # Excecute the machine commands (start with M)
            for command in parsed_commands.keys():
                if command[0] == 'M':
                    if command == 'M0':
                        raise NotImplementedError('M0 not implemented.')
                    elif command == 'M80':
                        # Power on the instrument.
                        exit_code, msg = self.M80()
                    elif command == 'M81':
                        # Power off the instrument.
                        exit_code, msg = self.M81()
                    elif command == 'M85':
                        raise NotImplementedError('M85 not implemented.')
                    elif command == 'M92':
                        # Set the steps per nm
                        raise NotImplementedError('M92 not implemented.')
                        exit_code, msg = self.M92(axis, value)
                    elif command == 'M105':
                        # Get the temperature report.
                        exit_code, msg = self.M105()
                    elif command == 'M111':
                        raise NotImplementedError('M111 not implemented.')
                    elif command == 'M112':
                        # Emergency stop.
                        exit_code, msg, self.M112()
                    elif command == 'M113':
                        # Keep the host alive
                        exit_code, msg = self.M113()
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
                        exit_code, msg = self.M503()
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
                        exit_code, msg = self.M999()
                    else:
                        raise Exception('This point should never be reached.')

                    # Delete the command from the dict
                    del parsed_commands[command]

            # Excecute the movement commands
            for command in parsed_commands.keys():

                if command == 'G0':
                    # Collect all the movement commands
                    # Move to all the given axes at the same time
                    exit_code, msg = self.G0({})
                elif command == 'G1':
                    # Collect all the movement commands
                    # Make an arc to the given position
                    exit_code, msg = self.G1({})
                elif command == 'G28':
                    # Home all axes
                    exit_code, msg = self.G28()
                elif command == 'G90':
                    # Set to absolute positioning
                    exit_code, msg = self.G90()
                elif command == 'G91':
                    # Set to relative positioning
                    exit_code, msg = self.G91()
                else:
                    raise Exception('This point should never be reached.')
                
                # Check the exit code
                if exit_code == 1:
                    # Command failed
                    raise Exception(msg)
    
                # Delete the command from the dict
                del parsed_commands[command]

            if len(parsed_commands) != 0:
                raise Exception('This point should never be reached.')
        
    # MOVEMENT FUNCTIONS
    def G0(self, movements):
        """
        Move to all the given axes at the same time.
        """
        raise NotImplementedError('G0 not implemented.')

    def G1(self, movements):
        """
        Make an arc to the given position.
        """
        raise NotImplementedError('G1 not implemented.')

    def G28(self):
        """
        Home all axes.
        """
        raise NotImplementedError('G28 not implemented.')

    def G90(self):
        """
        Set to absolute positioning.
        """
        self._positioning = 'ABS'

    def G91(self):
        """
        Set to relative positioning.
        """
        self._positioning = 'REL'

    # MACHINE FUNCTIONS
    def M80(self):
        """
        Power on the instrument.
        """
        raise NotImplementedError('M80 not implemented.')

    def M81(self):
        """
        Power off the instrument.
        """
        raise NotImplementedError('M81 not implemented.')

    def M92(self, axis, value):
        """
        Set the steps per nm
        """
        raise NotImplementedError('M92 not implemented.')

    def M105(self):
        """
        Get the temperature report.
        """
        raise NotImplementedError('M105 not implemented.')

    def M112(self):
        """
        Emergency stop.
        """
        self._emergency_stop()

    def M113(self):
        """
        Keep the host alive
        """
        raise NotImplementedError('M113 not implemented.')

    def M114(self):
        """
        Get the current position.
        """
        raise NotImplementedError('M not implemented.')

    def M503(self):
        """
        Report the current settings.
        """
        raise NotImplementedError('M503 not implemented.')

    def M999(self):
        """
        Reset the machine.
        """
        # Try to disconnect all the hardware.
        # Reset the emergency stop flag.
        # Reset the shutdown flag.
        # Reconnect all the hardware.
        raise NotImplementedError('M999 not implemented.')

    # MACRO FUNCTIONS