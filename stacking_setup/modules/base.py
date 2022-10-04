

class BaseModule():
    """Class that should be inherited by all module classes."""
    _id = None
    _type = 'CONTROLLER BASE CLASS'
    _hardware = []

    # ATTRIBUTES
    @property
    def id(self):
        """Get the class identifier."""
        return self._id

    @property
    def type(self):
        """Get the type of the hardware."""
        return self._type