import multiprocessing as mp
from .base_connector import BaseConnector
import errno
from time import sleep

SENTINEL = 'SENTINEL'
EOM_CHAR = 'EOM'


def read_pipe(child_conn, feedback=False):
    """
    Read the data from the pipe.
    
    Parameters
    ----------
    child_conn : multiprocessing.connection.Connection
        The connection to read from.
    n : int, optional
        The number of messages to read. The default is 0, read all messages.
    feedback : bool, optional
        If True, the received data will be sent back to the parent process.
        The default is False.

    Returns
    -------
    result : list
        The received data. I a sentinel command was received, it will be the
        last element in the list.

    """
    result = []
    try:
        # Check if there is a message ready
        if child_conn.poll(): 
            for msg in iter(child_conn.recv, EOM_CHAR):
                result.append(msg)
        else:
            pass
    except IOError as e:
        # Catch the error if the other side closes unexpected
        if e.errno == errno.EPIPE:
            close_pipe(child_conn)
            return result
        else:
            # Raise the error, cause is unknown
            raise IOError(e)

    if feedback:
        # Echo the reived conformation to parent
        write_pipe(child_conn, result)

    # Check if the closing request was given
    if SENTINEL in result:
        close_pipe(child_conn)
        # Put the SENTINEL command at the end
        result.append(result.pop(result.index(SENTINEL)))
    return result


def close_pipe(conn):
    """
    Close the pipe connection.
    
    Parameters
    ----------
    conn : multiprocessing.connection.Connection
        The connection to close.

    Returns
    -------
    None.

    """
    conn.close()


def write_pipe(conn, data):
    """
    Write the data to the pipe.
    
    Parameters
    ----------
    conn : multiprocessing.connection.Connection
        The connection to write to.
    data : list
        The data to write to the pipe.
    
    Returns
    -------
    None.

    """
    conn.send(data)
    conn.send(EOM_CHAR)


def pipe_is_open(conn):
    """
    Check if the pipe is open.
    
    Parameters
    ----------
    conn : multiprocessing.connection.Connection
        The connection to check.

    Returns
    -------
    bool
        True if the pipe is open, False otherwise.

    """
    return conn.poll()


class PipelineConnection(BaseConnector):
    _role = "PARENT"
    _connection_method = "PIPELINE"

    def __init__(self, connection):
        self._connection = connection

        if not self.handshake():
            raise ConnectionError('Handshake failed.')

    def connect(self):
        # The pipe is connected by default
        pass

    def disconnect(self):
        close_pipe(self._connection)

    def is_connected(self):
        return pipe_is_open(self._connection)

    def send(self, data):
        write_pipe(self._connection, data)

    def receive(self):
        # Check if a message is waiting
        if not self._connection.poll():
            return None
        return read_pipe(self._connection)

    def handshake(self):
        write_pipe(self._connection, 'Hello there.')

        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            res = read_pipe(self._connection)
            if len(res) == 0:
                attempts += 1
                sleep(0.1)
            elif res[0] == 'Hello there general Kenobi.':
                return True

        return False

    