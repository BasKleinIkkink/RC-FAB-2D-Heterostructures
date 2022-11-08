import configparser
import time

SENTINEL = 'SENTINEL'  # Sentinel command to close the pipe
EOM_CHAR = 'EOM'  # String indicating the end of a message over a pipe


class HandshakeError(Exception):
    
    def __init__(self, message=None):
        self._message = message

    def __str__(self):
        return self._message


class BaseConnector:
    """
    Class to hold all the expected connection functions.

    This class does not manage the connection it is a base class that should
    be inherited.
    """
    _connection_method = None
    _role = None
    _handshake_complete = False
    _SENTINEL = SENTINEL

    # ATTRIBUTES
    @property
    def connection_method(self):
        """Return the connection method."""
        return self._connection_method

    @property
    def role(self):
        """Return the role of the connection."""
        return self._role

    @property
    def handshake_complete(self):
        """Return the handshake status."""
        return self._handshake_complete

    @property
    def is_connected(self):
        """Check if the device is connected."""
        raise NotImplementedError()

    @property
    def SENTINEL(self):
        """Return the sentinel command."""
        return self._SENTINEL

    # METHODS
    def connect(self):
        """Connect to the device."""
        raise NotImplementedError()

    def disconnect(self):
        """Disconnect from the device."""
        raise NotImplementedError()

    def send_sentinel(self):
        """Send a sentinel to the IO controller (RPI)."""
        raise NotImplementedError()

    def send(self, command):
        """Send a command to the device."""
        raise NotImplementedError()

    def message_waiting(self):
        """Check if a message is waiting."""
        raise NotImplementedError()

    def receive(self):
        """Receive data from the device."""
        raise NotImplementedError()

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

