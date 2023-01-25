from typing import Union
from typeguard import typechecked

try:
    from .configs.accepted_commands import (
        ACCEPTED_COMMANDS,
        ACCEPTED_ATTRIBUTES,
        ACCEPTED_AXES,
    )
except ImportError:
    from configs.accepted_commands import (
        ACCEPTED_COMMANDS,
        ACCEPTED_ATTRIBUTES,
        ACCEPTED_AXES,
    )


class GcodeAttributeError(Exception):
    """Exception raised when there is an issue with a given attribute."""

    def __init__(self, msg):
        self._msg = msg


class GcodeParsingError(Exception):
    """Exception raised when there is an issue parsing a gcode command."""

    def __init__(self, msg):
        self._msg = msg


class GcodeParser:
    """
    Class to manage the parsing of gcode lines from the main code.

    Heavily inspired by marlin gcode https://marlinfw.org/meta/gcode/
    """

    @classmethod
    @typechecked
    def parse_gcode_line(cls, line: Union[str, bytes]) -> dict:
        """
        Parse the gcode command lines from the main process.

        Parameters
        ----------
        line : str or bytes
            The gcode command line.

        Raises
        ------
        GcodeParsingError:
            If the line is not a string or bytes or is empty.
        GcodeAttributeError:
            If the entry is not a valid command or attribute.
        Exception:
            If an unknown parsing error occurs.

        Returns
        -------
        commands : dict
            The parsed gcode commands with the hardware id as the dict key.

        """

        if not isinstance(
            line, (str, bytes)
        ):  # Check that the line is not empty and a string or bytes.
            raise GcodeParsingError(
                "Line is not a string or bytes or is empty. {}, {}".format(
                    line, type(line)
                )
            )

        if isinstance(line, bytes):  # If the line is in bytes convert to string.
            line = line.decode("utf-8")

        content = line.split(" ")
        if len(content) == 0:
            raise GcodeParsingError("Line is empty.")

        # Sort the commands so the right functions are called.
        commands = {}
        for cnt, command in enumerate(content):
            # Check if the command is a known command.
            if not cls._is_valid(command):
                raise GcodeAttributeError(
                    "Entry {} is not a valid command or attribute.".format(command)
                )

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
                raise Exception("This point should never be reached.")

        return commands

    @staticmethod
    @typechecked
    def _is_valid(entry: str) -> bool:
        """
        Check if the entry is a valid command or attribute.

        Uses the definitions from the accepted_commands.py file in the configs folder
        to check if the entry is a valid command or attribute.

        Parameters
        ----------
        entry : str
            The entry to check.

        Returns
        -------
        bool
            True if the entry is a valid command or attribute, otherwise False.

        """
        # Check if the entry is None or an empty string
        if entry is None or entry == "":
            return False

        # Check if the entry is a known command or attribute.
        if (
            entry not in ACCEPTED_COMMANDS.keys()
            and entry[0] not in ACCEPTED_AXES
            and entry[0] not in ACCEPTED_ATTRIBUTES
        ):
            return False
        else:
            # Check if the movment commands and attributes have a value attached.
            if entry[0] in ACCEPTED_AXES or entry[0] in ACCEPTED_ATTRIBUTES:
                if len(entry) < 2:
                    return False

            return True

    @staticmethod
    @typechecked
    def _add_attribute(cnt: int, command_dict: dict, content: list) -> dict:
        """
        Add an attribute to the command dict.

        Parameters
        ----------
        cnt : int
            The index of the command in the content list.
        command_dict : dict
            The command dict to add the attribute to.
        content : list
            The content of the command line split on ' '.

        Raises
        ------
        GcodeParsingError:
            If the attribute does not follow the set rules for parsing.
        GcodeAttributeError:
            If the attribute is not a valid attribute or follows a command that
            does not allow for the attribute.
        NotImplementedError:
            If the attribute is of a datatype that is not implemented.

        Returns
        -------
        command_dict : dict
            The command dict with the attribute added.

        """
        # Check if this is the first entry.
        if len(command_dict.keys()) == 0:
            raise GcodeParsingError(
                "Entry {} is an attribute but is the first entry in the command.".format(
                    content[cnt]
                )
            )

        # Check what the last added command was
        i = 0
        while True:
            i += 1
            if (
                content[cnt - i][0] in ACCEPTED_ATTRIBUTES
                or content[cnt - i][0] in ACCEPTED_AXES
            ):
                # Is also an attribute or a movement attribute
                continue
            else:
                break
        last_command = content[cnt - i]

        # Check if the last command allows the attribute.
        if last_command[0] in ACCEPTED_AXES:
            # Command is a movement command.
            raise GcodeAttributeError(
                "Movement commands ({}) are not allowed to have attributes. {}".format(
                    last_command, content[cnt]
                )
            )

        elif content[cnt][0] not in ACCEPTED_COMMANDS[last_command].keys():
            print(last_command, content[cnt])
            # The attribute is not allowed for the last command.
            raise GcodeAttributeError(
                "The attribute {} is not allowed for the last command".format(
                    content[cnt]
                )
            )

        # Convert the attribute data to the right type.
        attribute_id = content[cnt][0]
        data = content[cnt][1:]

        # TODO: #5 Convert the attribute to the right data type
        # Get the allowed data types for the attribute.
        types = ACCEPTED_COMMANDS[last_command][attribute_id]
        if int in types or float in types:
            # Try converting to int
            # Check if there is a . in the numer
            if "." in data:
                if float in types:
                    data = float(data)
            else:
                data = int(data)
        elif bool in types:
            # Check if the data is given in text or numeric.
            if data.isdigit():
                if data == "0":
                    data = False
                elif data == "1":
                    data = True
                else:
                    raise GcodeAttributeError(
                        "The data {} is not a valid boolean.".format(data)
                    )
            elif data.lower() == "true":
                data = True
            elif data.lower() == "false":
                data = False
            else:
                raise GcodeAttributeError(
                    "The data {} is not a valid boolean.".format(data)
                )
        elif bytes in types:
            # Convert to bytes if allowed
            data = bytes(data)
        else:
            raise NotImplementedError(
                "The data type {} is not implemented.".format(types)
            )

        command_dict[last_command][attribute_id] = data
        return command_dict

    @staticmethod
    @typechecked
    def _add_movement(cnt: int, command_dict: dict, content: list) -> dict:
        """
        Add a movement command to the command dict.

        Parameters
        ----------
        cnt : int
            The index of the command in the content list.
        command_dict : dict
            The command dict to add the attribute to.
        content : list
            The content of the command line.

        Raises
        ------
        GcodeParsingError:
            If the movement command is an invalid value.
        GcodeAttributeError:
            If the movement aready exists in the command dict, if the
            movement follows a command that does not allow for movement
            commands.

        Returns
        -------
        command_dict : dict
            The command dict with the attribute added.

        """
        # Convert the movement value to the right type.
        data = content[cnt][1:]

        try:
            data = int(data)
        except ValueError:
            data = float(data)
        except:
            raise GcodeParsingError(
                "Movement command {} is not a valid value.".format(content[cnt][0])
            )

        # Look for the last non axis non attribute command.
        i = 0
        while True:
            i -= 1
            last_command = content[cnt + i]

            # Check if the command is an attribute
            if last_command[0] in ACCEPTED_ATTRIBUTES:
                raise GcodeAttributeError(
                    "Movement commands ({}) are not allowed to have attributes.".format(
                        last_command
                    )
                )

            # Check if the command is an axis command.
            if last_command[0] in ACCEPTED_AXES:
                continue
            else:
                break

        # Check if the command is allowed to have a movement command.
        try:
            if content[cnt][0] not in ACCEPTED_COMMANDS[last_command]["ACCEPTED_AXES"]:
                raise GcodeAttributeError(
                    "Movent attribute {} is not allowed for command {}.".format(
                        content[cnt], last_command
                    )
                )
        except KeyError:
            raise GcodeAttributeError(
                "Command {} is not allowed to have movement attributes.".format(
                    last_command
                )
            )

        # Check if there already is a movement command with the same id.
        if content[cnt][0] in command_dict[last_command].keys():
            raise GcodeAttributeError(
                "Movement command {} already exists.".format(content[cnt][0])
            )

        # Add the movement command to the command dict.
        command_dict[last_command][content[cnt][0]] = data
        return command_dict
