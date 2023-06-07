import os
from PySide6.QtCore import QSize
from typing import Union
from typeguard import typechecked
import configparser
from ast import literal_eval
from typing import Tuple


class GuiSettings:

    @typechecked
    def __init__(self, filename : str='gui_config.ini') -> None:
        """
        Initialize the settings.

        Parameters
        ----------
        filename: str
            The filename of the settings file.
        """
        # Create the path to file
        self._filename = filename
        # Check if the os is linux or windows
        filler = '/' if os.name == 'posix' else '\\'
        self._path = os.path.dirname(os.path.abspath(__file__)) + filler + self._filename
        if not self._file_exists(self._path):
            raise FileNotFoundError(f'File {self._path} not found.')

        self._load_from_file()

    def _file_exists(self, path : str) -> bool:
        """
        Check if the file exists.

        Parameters
        ----------
        path: str
            The path to the file.

        Returns
        -------
        file_exists: bool
            True if the file exists, False otherwise.
        """
        return os.path.isfile(path)
        
    def _load_from_file(self):
        """
        Load all the needed settings from file
        
        .. note::
            The main reason for loading the settings from the config into the settings 
            object is so the points of failure will show on startup and not during
            operation
        """
        config = configparser.ConfigParser()
        config.read(self._path)

        # Load the settings
        lcd_size = literal_eval(config.get('WIDGET.SIZE', 'lcd_size'))
        self._lcd_size = QSize(lcd_size[0], lcd_size[1])
        buttons_size = literal_eval(config.get('WIDGET.SIZE', 'button_size'))
        self._button_size = QSize(buttons_size[0], buttons_size[1])

        # General backend settings
        self._keep_alive_interval = config.getfloat('BACKEND', 'keep_alive_interval')
        self._pos_auto_update_interval = config.getfloat('BACKEND', 'pos_autoupdate_interval')
        self._temp_auto_update_interval = config.getfloat('BACKEND', 'temp_autoupdate_interval')
        self._known_units = literal_eval(config.get('BACKEND', 'known_units'))

        # Temp settings
        self._max_temp = config.getfloat('WIDGET.TEMPERATURE', 'max_temp')
        self._temp_presets = literal_eval(config.get('WIDGET.TEMPERATURE', 'temp_presets'))

        # Mask settings
        self._mask_vel_presets = literal_eval(config.get('WIDGET.MASK', 'vel_presets'))
        self._mask_drive_step_presets = literal_eval(config.get('WIDGET.MASK', 'drive_step_presets'))
        if not self._check_units_known(self._mask_vel_presets) and \
                self._check_units_known(self._mask_drive_step_presets):
            raise ValueError('Unknown units in mask presets.')

        # Base settings
        self._base_vel_presets = literal_eval(config.get('WIDGET.BASE', 'vel_presets'))
        self._base_drive_step_presets = literal_eval(config.get('WIDGET.BASE', 'drive_step_presets'))
        if not self._check_units_known(self._base_vel_presets) and \
                self._check_units_known(self._base_drive_step_presets):
            raise ValueError('Unknown units in base presets.')

        # Focus settings
        self._focus_vel_presets = literal_eval(config.get('WIDGET.FOCUS', 'vel_presets'))
        self._focus_drive_step_presets = literal_eval(config.get('WIDGET.FOCUS', 'drive_step_presets'))
        if not self._check_units_known(self._focus_vel_presets) and \
                self._check_units_known(self._focus_drive_step_presets):
            raise ValueError('Unknown units in focus presets.')

    def _check_units_known(self, presets : list) -> bool:
        """
        Check if the units are known.

        Parameters
        ----------
        presets: list
            The presets to check.

        Returns
        -------
        units_known: bool
            True if the units are known, False otherwise.
        """
        for preset in presets:
            unit = preset.split(' ')[1]
            if '/' in unit:
                unit = unit.split('/')[0]

            if preset[1] not in self._known_units.keys():
                return False
        return True

    # SOME GENERAL BACKEND SETTINGS
    @property
    def keep_alive_interval(self) -> Union[float, int]:
        """
        Get the interval for the keep alive message.
        
        Returns
        -------
        int or float
            The interval in seconds.
        """
        return self._keep_alive_interval

    @property
    def pos_auto_update_interval(self) -> Union[float, int]:
        """
        Get the interval for the position auto update.
        
        Returns
        -------
        int or float
            The interval in seconds.
        """
        return self._pos_auto_update_interval

    @property
    def temp_auto_update_interval(self) -> Union[float, int]:
        """
        Get the interval for the temperature auto update.
        
        Returns
        -------
        int or float
            The interval in seconds.
        """
        return self._temp_auto_update_interval

    @property
    def known_units(self) -> dict:
        """
        Get the known units.
        
        Returns
        -------
        list
            The list of known units.
        """
        return self._known_units

    # GENERAL SIZE INFORMATION
    @property
    def lcd_size(self) -> QSize:
        """
        Get the size of the lcd.

        Returns
        -------
        QSize
            The size of the lcd display.
        """
        return self._lcd_size

    @property
    def button_size(self) -> QSize:
        """
        Get the size of the buttons.

        Returns
        -------
        QSize
            The size of the buttons.
        """
        return self._button_size

    # SETTINGS FOR TEMPERATURE WIDGET
    @property
    def temp_presets(self) -> Tuple[int]:
        """
        Get the temperature presets.

        Returns
        -------
        list
            The temperature presets.
        """
        return self._temp_presets

    # SETTINGS FOR THE MASK WIDGET
    @property
    def mask_vel_presets(self) -> list:
        """
        Get the mask velocity presets.

        Returns
        -------
        list
            The mask velocity presets.
        """
        return self._mask_vel_presets

    @property
    def mask_drive_step_presets(self) -> list:
        """
        Get the distance per drive click presets.

        Returns
        -------
        int or float
            The distance per drive click.
        """
        return self._mask_drive_step_presets

    # SETTINGS FOR THE BASE WIDGET
    @property
    def base_vel_presets(self) -> list:
        """
        Get the base velocity presets.

        Returns
        -------
        list
            The base velocity presets.
        """
        return self._base_vel_presets

    @property
    def base_drive_step_presets(self) -> list:
        """
        Get the distance per drive click.

        Returns
        -------
        int or float
            The distance per drive click.
        """
        return self._base_drive_step_presets

    # SETTINGS FOR THE FOCUS WIDGET
    @property
    def focus_vel_presets(self) -> list:
        """
        Get the focus velocity presets.

        Returns
        -------
        list
            The focus velocity presets.
        """
        return self._focus_vel_presets

    @property
    def focus_drive_step_presets(self) -> list:
        """
        Get the distance per drive click.

        Returns
        -------
        int or float
            The distance per drive click.
        """
        return self._focus_drive_step_presets

