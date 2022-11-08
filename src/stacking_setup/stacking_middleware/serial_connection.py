import serial
from typing import Union
from typeguard import typechecked
import time

try:
    from .base_connector import BaseConnector, HandshakeError
    from ..stacking_backend.configs.settings import Settings
except ImportError:
    from base_connector import BaseConnector, HandshakeError
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
        self.connect()

    def connect(self) -> None:
        if not self._serial.is_open: self._serial.open()

    def disconnect(self) -> None:
        if self._serial.is_open: self._serial.close()

    def is_connected(self) -> bool:
        return self._serial.is_open

    def send_sentinel(self):
        self.send(self.SENTINEL)

    def send(self, command):
        # Check if the command is a string otherwise convert to str
        if not isinstance(command, str): command = str(command)
        self._serial.write(command.encode())

    def message_waiting(self):
        return True if self._serial.in_waiting > 0 else False

    def receive(self) -> Union[str, None]:
        return self._serial.read().decode()

    def handshake(self):
        # Depending on the role of the connector decide
        # what to send and what to receive
        if self._role == 'FRONDEND':
            if not self._frondend_handshake():
                raise HandshakeError('Frondend handshake failed')
            else: self._handshake_complete = True

        elif self._role == 'BACKEND':
            if not self._backend_handshake():
                raise HandshakeError('Backend handshake failed')
            else: self._handshake_complete = True

        else:
            raise HandshakeError('Unknown role {}'.format(self._role))

    def _frondend_handshake(self):
        if not self.is_connected: return False

        # Send the hello message
        self.send('Hello there.')

        # Wait for the response
        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            res = self.receive()
            if len(res) == 0:
                attempts += 1
                time.sleep(0.1)
            elif res[0] == 'Hello there general Kenobi.':
                return True

    def _backend_handshake(self):
        # Wait for the hello message
        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            res = self.receive()
            if len(res) == 0:
                attempts += 1
                time.sleep(0.1)
            elif res[0] == 'Hello there.':
                break
        
        # If the handshake failed keep waiting for the hello message
        # and send 'Im still here' every 5 seconds
        if attempts == max_attempts:
            while True:
                res = self.receive()
                if len(res) == 0:
                    time.sleep(5)
                    self.send('Im still here')
                elif res[0] == 'Hello there.':
                    # Break out of the loop
                    break

        # Send the response
        self.send('Hello there general Kenobi.')
        return True


if __name__ == '__main__':
    def test_frondend():
        serial_connection = SerialConnection('FRONDEND')
        serial_connection.handshake()
        print(serial_connection._handshake_complete)

    def test_backend():
        serial_connection = SerialConnection('BACKEND')
        serial_connection.handshake()
        print(serial_connection._handshake_complete)
    
    test_frondend()
    # test_backend()
