

class BaseConnector(object):
    """
    Class to hold all the expected connection functions.

    This class does not manage the connection it is a base class that should
    be inherited.
    """
    _connection_method = None
    _timeout = 1

    @property
    def connection_method(self):
        """Return the connection method."""
        return self._connection_method

    def connect(self):
        """Connect to the device."""
        raise NotImplementedError()

    def disconnect(self):
        """Disconnect from the device."""
        raise NotImplementedError()

    def is_connected(self):
        """Check if the device is connected."""
        raise NotImplementedError()

    def send(self, command):
        """Send a command to the device."""
        raise NotImplementedError()

    def receive(self):
        """Receive data from the device."""
        raise NotImplementedError()

    def handshake(self):
        """Perform a handshake with the IO controller (RPI)."""
        raise NotImplementedError()
