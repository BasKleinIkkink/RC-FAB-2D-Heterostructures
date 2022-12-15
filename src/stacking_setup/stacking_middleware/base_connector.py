import configparser
import time

SENTINEL = "SENTINEL"  # Sentinel command to close the pipe
EOM_CHAR = "EOM"  # String indicating the end of a message over a pipe


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
        if self._role == "FRONDEND":
            self._frondend_handshake()
            self._handshake_complete = True

            # Empty the buffer
            while self.message_waiting():
                _ = self.receive()

        elif self._role == "BACKEND":
            self._backend_handshake()
            self._handshake_complete = True

            # Empty the buffer
            while self.message_waiting():
                _ = self.receive()

        else:
            raise HandshakeError("Unknown role {}".format(self._role))

    def _frondend_handshake(self):
        if not self.is_connected:
            return False
        # Wait for the response
        while True:
            # Send the hello message
            self.send("Hello there.")

            if self.message_waiting():
                res = self.receive()
            else:
                continue

            if res[0] == "Hello there general Kenobi.":
                return True
            else:
                raise ValueError("Unexpected message: {}".format(res[0]))

        raise ValueError("frondend Handshake failed")

    def _backend_handshake(self):
        # Wait for the hello message
        while True:
            time.sleep(0.1)

            if self.message_waiting():
                res = self.receive()
            else:
                continue

            if res[0] == "Hello there.":
                self.send("Hello there general Kenobi.")
                break
            else:
                raise ValueError("Unexpected message: {}".format(res[0]))
