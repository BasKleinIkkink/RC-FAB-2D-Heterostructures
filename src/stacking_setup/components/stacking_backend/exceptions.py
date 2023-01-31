class NotSupportedError(Exception):
    """Exception raised when a method is not supported."""

    def __init__(self, msg=None) -> ...:
        """Initialize the exception."""
        self._msg = msg

    def __str__(self) -> str:
        return self._msg


class HardwareNotConnectedError(Exception):
    """Exception raised when a hardware is not connected."""

    def __init__(self, msg=None) -> ...:
        """Initialize the exception."""
        self._msg = msg

    def __str__(self) -> str:
        return self._msg


class HardwareError(Exception):
    """General exception raised when the hardware is not working properly."""

    def __init__(self, msg=None) -> ...:
        """Initialize the exception."""
        self._msg = msg

    def __str__(self) -> str:
        return self._msg
