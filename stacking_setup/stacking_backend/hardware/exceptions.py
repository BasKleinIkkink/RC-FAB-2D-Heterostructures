

class NotSupportedError(Exception):
    """
    Exception raised when a method is not supported.
    """
    
    def __init__(self, message=None):
        """
        Initialize the exception.
        """
        super().__init__(message)


class HardwareNotConnectedError(Exception):
    """
    Exception raised when a hardware is not connected.
    """
    
    def __init__(self, message=None):
        """
        Initialize the exception.
        """
        super().__init__(message)


class NotCalibratedError(Exception):
    """
    Exception raised when the hardware is not calibrated for the asked function.

    F.e. trying to do an absolute move when the home point is unknown.
    """
    
    def __init__(self, message=None):
        """
        Initialize the exception.
        """
        super().__init__(message)
