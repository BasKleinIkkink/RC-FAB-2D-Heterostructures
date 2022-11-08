import serial
import typing
from typeguard import typechecked

try:
    from .base_connector import BaseConnector
    from ..stacking_backend.configs.settings import Settings
except ImportError:
    from base_connector import BaseConnector
    from ..stacking_backend.configs.settings import Settings


class SerialConnection(BaseConnector):
    _connection_method = 'SERIAL'

    def __init__(self, settings : Settings, role : str) -> None:
        self._role = role
        self._settings = settings

        # Load some settings
        port = self._settings.get('serial', 'port')
        baudrate = self._settings.get('serial', 'baudrate')
        timeout = self._settings.get('serial', 'timeout')

        # Create the serial connection
        self._ser = serial.Serial(port, baudrate, timeout=timeout)

    def connect(self) -> None:
        if not self._serial.is_open: self._serial.open()

    def disconnect(self) -> None:
        if self._serial.is_open: self._serial.close()

    def is_connected(self) -> bool:
        return self._serial.is_open

    def send(self, command):
        # Check if the command is a string otherwise convert to str
        if not isinstance(command, str): command = str(command)
        self._serial.write(command.encode())

    def message_waiting(self):
        return True if self._serial.in_waiting > 0 else False

    def receive(self):
        if not self.message_waiting(): return None
        return self._serial.read().decode()


if __name__ == '__main__':
    serial_connection = SerialConnection('PARENT')
    serial_connection.connect()
    serial_connection.send('Hello, world!')
    serial_connection.disconnect()
