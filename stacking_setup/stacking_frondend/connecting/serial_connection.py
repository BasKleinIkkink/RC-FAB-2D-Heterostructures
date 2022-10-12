import serial
from base_connector import BaseConnector


class SerialConnection(BaseConnector):
    _role = 'PARENT'
    _connection_method = 'SERIAL'

    def __init__(self, config):
        self._load_from_config(config)
        self._serial = serial.Serial(self._port, self._baud, timeout=self._timeout)

    def _load_from_config(self, config):
        self._port = config.get('SERIAL', 'port')
        self._baud = config.get('SERIAL', 'baudrate')
        self._timeout = config.get('SERIAL', 'timeout')

    def connect(self):
        self._serial.open()

    def disconnect(self):
        self._serial.close()

    def is_connected(self):
        return self._serial.is_open

    def send(self, command):
        self._serial.write(command.encode())

    def _message_waiting(self):
        return True if self._serial.in_waiting > 0 else False

    def receive(self):
        if not self._message_waiting():
            return None

        return self._serial.read().decode()

    

