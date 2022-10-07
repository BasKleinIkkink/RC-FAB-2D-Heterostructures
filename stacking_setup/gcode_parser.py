from .configs.accepted_commands import ACCEPTED_COMMANDS, ACCEPTED_ATTRIBUTES, ACCEPTED_AXES


class GcodeParser():
    """
    Class to manage the parsing of gcode lines from the main code.
    
    Gcode docs https://marlinfw.org/meta/gcode/

    Used Gcode commands:
    -------------------
    G0 - G1 : Lineair movement
    G28 : Home all axes
    G90 : Set to absolute coordinates
    G91 : Set to relative coordinates

    X, Y, Z : Move the mask holder
    I, J, K : Move the base plate
    L : Move the sample holder

    M0 : Unconditional stop
    M80 : Power on
    M81 : Power off
    M85 : Inactivity shutdown
    M92 : Set axis steps per unit
    M105 : Report current temperature
    M111 : Debug level
    M112 : Emergency stop
    M113 : Keep host alive
    M114 : Report current position
    M119 : Report endstop status
    M120 : Enable endstops
    M121 : Disable endstops
    M140 : Set bed temperature
    M154 : Position auto report
    M155 : Temperature auto report
    M190 : Wait for bed temperature
    M500 : Save settings
    M501 : Restore settings
    M503 : Report settings
    M510 : Lock machine
    M511 : Unlock machine
    M512 : Set password
    M810 - M819 : G-code macros
    M999 : STOP restart
    """

    @classmethod
    def parse_gcode_line(cls, line):
        """
        Parse the gcode command lines from the main process.

        Parameters:
        ----------
        line : str or bytes
            The gcode command line.

        Returns:
        -------
        commands : dict
            The parsed gcode commands with the hardware id as the dict key.

        Raises:
        -------
        TypeError:
            If the line is not a string or bytes.
        ValueError:
            If the line contains no gcode commands.
        """
        # Check that the line is not empty and a string or bytes.
        if not isinstance(line, (str, bytes)):
            raise TypeError('Line is not a string or bytes or is empty.')

        # If the line is in bytes convert to string.
        if isinstance(line, bytes):
            line = line.decode('utf-8')

        content = line.split(' ')
        if len(content) == 0:
            raise ValueError('Line is empty.')
        
        # Sort the commands so the right functions are called.
        commands = {}
        for cnt, command in enumerate(content):
            # Check if the command is a known command.
            if not cls._is_valid(command):
                raise ValueError('Entry {} is not a valid command or attribute.'.format(command))

            # Check if the entry is an attribute.
            if command[0] in ACCEPTED_ATTRIBUTES:
                commands = cls._add_attribute(cnt, commands, content)
                
            # Check if the first letter corresponds to a command (movement commands).
            elif command[0] in ACCEPTED_AXES:
                commands = cls._add_movement(cnt, commands, content)

            # Check if the complete command corresponds to a command (f.e. M commands).
            elif command in ACCEPTED_COMMANDS.keys():
                if command not in commands.keys():
                    commands[command] = {}

            else:
                raise Exception('This point should never be reached.')

        return commands

    @staticmethod
    def _is_valid(entry):
        """
        Check if the entry is a valid command or attribute.

        Parameters:
        ----------
        entry : str
            The entry to check.

        Returns:
        -------
        bool
            True if the entry is a valid command or attribute.

        """
        # Check if the entry is a known command or attribute.
        if entry not in ACCEPTED_COMMANDS.keys() and entry[0] not in ACCEPTED_AXES \
                and entry[0] not in ACCEPTED_ATTRIBUTES:
            return False
        else:
            # Check if the movment commands and attributes have a value attached.
            if entry[0] in ACCEPTED_AXES or entry[0] in ACCEPTED_ATTRIBUTES:
                if len(entry) < 2:
                    return False

            return True


    @staticmethod
    def _add_attribute(cnt, command_dict, content):
        """
        Add an attribute to the command dict.

        Parameters:
        ----------
        cnt : int
            The index of the command in the content list.
        command_dict : dict
            The command dict to add the attribute to.
        content : list
            The content of the command line.

        Returns:
        -------
        command_dict : dict
            The command dict with the attribute added.

        """
        # Check if this is the first entry.
        if len(command_dict.keys()) == 0:
            raise ValueError('Entry is an attribute but is the first entry.')

        # Check what the last added command was
        i = 0
        while True:
            i += 1
            if content[cnt - i][0] in ACCEPTED_ATTRIBUTES or \
                    content[cnt -i][0] in ACCEPTED_AXES:
                # Is also an attribute or a movement attribute
                continue
            else:
                break
        last_command = content[cnt - i]

        # Check if the last command allows the attribute.
        if last_command[0] in ACCEPTED_AXES:
            # Command is a movement command.
            raise AttributeError('Movement commands ({}) are not allowed to have attributes.'.format(last_command, attribute_entry))

        elif content[cnt][0] not in ACCEPTED_COMMANDS[last_command].keys():
            # The attribute is not allowed for the last command.
            raise AttributeError('The attribute {} is not allowed for the last command.'.format(last_command, attribute_entry))

        # Convert the attribute data to the right type.
        attribute_id = content[cnt][0]
        data = content[cnt][1:]

        # TODO: #5 Convert the attribute to the right data type
        # Get the allowed data types for the attribute.
        types = ACCEPTED_COMMANDS[last_command][attribute_id]
        if int in types or float in types:
            # Try converting to int
            # Check if there is a . in the numer
            if '.' in data:
                if float in types:
                    data = float(data)
            else:
                data = int(data)
        elif bool in types:
            # Check if the data is given in text or numeric.
            if data.isdigit():
                if data == '0':
                    data = False
                elif data == '1':
                    data = True
                else:
                    raise AttributeError('The data {} is not a valid boolean.'.format(data))
            elif data == 'True' or data == 'TRUE' or data == 'true':
                data = True
            elif data == 'False' or data == 'FALSE' or data == 'false':
                data = False
            else:
                raise ValueError('The data {} is not a valid boolean.'.format(data))
        elif bytes in types:
            # Convert to bytes
            data = bytes(data)
        else:
            raise NotImplementedError('The data type {} is not implemented.'.format(types))

        # Add the attribute to the last command
        if isinstance(data, str):
            raise Exception('The data {} is not a valid type.'.format(data))
        command_dict[last_command][attribute_id] = data
        return command_dict

    @staticmethod
    def _add_movement(cnt, command_dict, content):
        """
        Add a movement command to the command dict.
        """
        # Convert the movement value to the right type.
        data = content[cnt][1:]
        
        try:
            data = int(data)
        except ValueError:
            data = float(data)
        except:
            raise ValueError('Movement command {} is not a valid number.'.format(content[cnt][0]))

        # Look for the last non movement non attribute command.
        i = 0
        while True:
            i -= 1
            last_command = content[cnt + i]

            # Check if the command is an attribute
            if last_command[0] in ACCEPTED_ATTRIBUTES:
                raise AttributeError('Movement commands ({}) are not allowed to have attributes.'.format(last_command))
            
            # Check if the command is a movement command.
            if last_command[0] in ACCEPTED_AXES:
                continue
            else:
                break

        # Check if the command is allowed to have a movement command.
        try:
            if content[cnt][0] not in ACCEPTED_COMMANDS[last_command]['ACCEPTED_AXES']:
                raise AttributeError('Movent attribute {} is not allowed for command {}.'.format(content[cnt], last_command))
        except KeyError:
            raise AttributeError('Command {} is not allowed to have movemt attributes.'.format(last_command))

        # Check if there already is a movement command with the same id.
        if content[cnt][0] in command_dict[last_command].keys():
            raise ValueError('Movement command {} already exists.'.format(content[cnt][0]))

        # Add the movement command to the command dict.
        command_dict[last_command][content[cnt][0]] = data
        return command_dict
