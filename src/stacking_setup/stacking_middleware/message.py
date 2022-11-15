import datetime

class Message:
    """Class used to send status messages between the frond and backend."""

    def __init__(self, exit_code, command, msg, *args, **kwargs):
        self._exit_code = exit_code
        self._command = command
        self._msg = msg
        self._args = args
        self._kwargs = kwargs
        self._timestamp = datetime.datetime.now()

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

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def command(self):
        return self._command

    def __str__(self):
        return self._msg

    def items(self):
        return {'exit_code': self._exit_code,
                'command': self._command,
                'msg': self._msg,
                'args': self._args,
                'kwargs': self._kwargs,
                'timestamp': self._timestamp}

    def keys(self):
        return self.items().keys()

    def values(self):
        return self.items().values()
