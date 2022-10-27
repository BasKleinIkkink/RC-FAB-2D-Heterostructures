

class Message:
    """Class used to send status messages between the frond and backend."""

    def __init__(self, exit_code, msg, *args, **kwargs):
        self._exit_code = exit_code
        self._msg = msg
        self._args = args
        self._kwargs = kwargs

    @property
    def exit_code(self):
        return self._exit_code

    @property
    def msg(self):
        return self._msg

    @property
    def args(self):
        return self._args

    @property
    def kwargs(self):
        return self._kwargs