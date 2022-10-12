import configparser


class BaseConnector(object):
    """
    Class to hold all the expected connection functions.

    This class does not manage the connection it is a base class that should
    be inherited.
    """
    _connection_method = None
    _timeout = 1
    _role = None
    _config = None
    _handshake_complete = False

    def __init__(self, role):
        # Load the config file
        self._role = role
        self._config = configparser.ConfigParser()
        self._config.read("com_config.ini")
        self._load_settings()

    def _load_settings(self):
        """Load the settings from the config file."""
        raise NotImplementedError()

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

    # METHODS
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

    def message_waiting(self):
        """Check if a message is waiting."""
        raise NotImplementedError()

    def receive(self):
        """Receive data from the device."""
        raise NotImplementedError()

    def handshake(self):
        """Perform a handshake with the IO controller (RPI)."""
        raise NotImplementedError()
