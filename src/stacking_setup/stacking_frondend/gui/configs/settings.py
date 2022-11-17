import os
from PySide6.QtCore import QSize
from typing import Union
from typeguard import typechecked
import configparser
from ast import literal_eval


class Settings:

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
        self._path = os.path.dirname(os.path.abspath(__file__)) + '\\' + self._filename
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

        self._keep_alive_interval = config.getfloat('BACKEND', 'keep_alive_interval')
        self._pos_auto_update_interval = config.getfloat('BACKEND', 'pos_autoupdate_interval')
        self._temp_auto_update_interval = config.getfloat('BACKEND', 'temp_autoupdate_interval')

        self._max_temp = config.getfloat('WIDGET.TEMPERATURE', 'max_temp')	

        self._mask_vel_presets = config.get('WIDGET.MASK', 'vel_presets')
        self._base_vel_presets = config.get('WIDGET.BASE', 'vel_presets')
        self._foruc_vel_presets = config.get('WIDGET.FOCUS', 'vel_presets')
        self._mask_dist_per_drive_click = config.getfloat('WIDGET.MASK', 'dist_per_drive_click')
        self._base_dist_per_drive_click = config.getfloat('WIDGET.BASE', 'dist_per_drive_click')
        self._focus_dist_per_drive_click = config.getfloat('WIDGET.FOCUS', 'dist_per_drive_click')

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
    def temp_presets(self) -> list:
        """
        Get the temperature presets.

        Returns
        -------
        list
            The temperature presets.
        """
        return self._temp_preset

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
    def dist_per_drive_click(self) -> Union[float, int]:
        """
        Get the distance per drive click.

        Returns
        -------
        int or float
            The distance per drive click.
        """
        return self._dist_per_drive_click

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
    def base_dist_per_drive_click(self) -> Union[float, int]:
        """
        Get the distance per drive click.

        Returns
        -------
        int or float
            The distance per drive click.
        """
        return self._base_dist_per_drive_click

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
        return self._foruc_vel_presets

    @property
    def focus_dist_per_drive_click(self) -> Union[float, int]:
        """
        Get the distance per drive click.

        Returns
        -------
        int or float
            The distance per drive click.
        """
        return self._focus_dist_per_drive_click

