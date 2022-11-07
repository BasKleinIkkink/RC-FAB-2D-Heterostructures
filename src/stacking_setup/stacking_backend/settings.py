import configparser
from configs.accepted_commands import ACCEPTED_COMMANDS, ACCEPTED_AXES, ACCEPTED_LINEAR_AXES, ACCEPTED_ROTARY_AXES
from typing import Union
from typeguard import typechecked


class Settings:

    @typechecked
    def __init__(self, filename : str) -> None:
        self._config = configparser.ConfigParser()
        self._config.read(filename)
        self._accepted_commands = ACCEPTED_COMMANDS
        self._accepted_axes = ACCEPTED_AXES
        self._accepted_linear_axes = ACCEPTED_LINEAR_AXES
        self._accepted_rotary_axes = ACCEPTED_ROTARY_AXES

    # ATTRIBUTES
    @property
    def accepted_commands(self) -> dict:
        return self._accepted_commands

    @property
    def accepted_axes(self) -> list:
        return self._accepted_axes

    @property
    def accepted_linear_axes(self) -> list:
        return self._accepted_linear_axes
    
    @property
    def accepted_rotary_axes(self) -> list:
        return self._accepted_rotary_axes
    
    # FUNCTIONS
    def get(self, section : str, key : str):
        """Get the value of a key in a specific section."""
        return self._config[section][key]

    def set(self, section : str, key : str, value : Union[str, int, float, bool]) -> None:
        """Set the value of a key in a specific section."""
        self._config[section][key] = value

    def save(self):
        """Save the settings to the file."""
        with open('settings.ini', 'w') as configfile:
            self._config.write(configfile)