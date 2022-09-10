

class NotSupportedError(Exception):
    """
    Exception raised when a method is not supported.
    """
    
    def __init__(self, message):
        """
        Initialize the exception.
        """
        super().__init__(message)


class HardwareNotConnectedError(Exception):
    """
    Exception raised when a hardware is not connected.
    """
    
    def __init__(self, message):
        """
        Initialize the exception.
        """
        super().__init__(message)


