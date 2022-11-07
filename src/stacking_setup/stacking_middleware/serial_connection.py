import serial
from .base_connector import BaseConnector


class SerialConnection(BaseConnector):
    _connection_method = 'SERIAL'

    def __init__(self, role):
        super().__init__(role)

    #def _load_settings(self):
    #    return None
    #    section = 'SERIAL.PARENT' if self.role == 'PARENT' else 'SERIAL.CHILD'
    #    self._port = self._config.get(section, 'port')
    #    self._baud = self._config.get(section, 'baudrate')
    #    self._timeout = self._config.get(section, 'timeout')

    def connect(self):
        self._serial.open()

    def disconnect(self):
        self._serial.close()

    def is_connected(self):
        return self._serial.is_open

    def send(self, command):
        self._serial.write(command.encode())

    def message_waiting(self):
        return True if self._serial.in_waiting > 0 else False

    def receive(self):
        if not self.message_waiting():
            return None

        return self._serial.read().decode()


if __name__ == '__main__':
    serial_connection = SerialConnection('PARENT')
    serial_connection.connect()
    serial_connection.send('Hello, world!')
    serial_connection.disconnect()
