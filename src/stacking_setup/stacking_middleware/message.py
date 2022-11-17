import datetime
from typing import Union
from typeguard import typechecked
import pickle


class Message:
    """Class used to send status messages between the frond and backend."""

    @typechecked
    def __init__(self, exit_code : int, command_id : str, msg : Union[str, dict],
            command : Union[str, dict, None]=None):
        self.exit_code = exit_code
        self.command = command
        self.command_id = command_id
        self.msg = msg
        self.timestamp = str(datetime.datetime.now())

    def items(self):
        return self.__dict__.items()

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

if __name__ == '__main__':
    msg = Message(0, 'test', 'test', 'test')
    print(msg.__dict__)
