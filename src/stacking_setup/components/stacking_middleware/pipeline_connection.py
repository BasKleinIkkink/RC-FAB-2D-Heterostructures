import multiprocessing as mp
from .base_connector import BaseConnector, SENTINEL, EOM_CHAR
import errno
import os
from time import sleep
from queue import Empty, Full
import threading as tr


class PipeCom:
    @staticmethod
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

    @classmethod
    def read_pipe(cls, child_conn, feedback=False):
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
                cls.close_pipe(child_conn)
                return result
            else:
                # Raise the error, cause is unknown
                raise IOError(e)

        if feedback:
            # Echo the reived conformation to parent
            cls.write_pipe(child_conn, result)

        # Check if the closing request was given
        if SENTINEL in result:
            cls.close_pipe(child_conn)
            # Put the SENTINEL command at the end
            result.append(result.pop(result.index(SENTINEL)))
        return result

    @staticmethod
    def write_pipe(conn, data):
        """
        Write the data to the pipe.

        Parameters
        ----------
        conn : multiprocessing.connection.Connection
            The connection to write to.
        data : list, str or bytes
            The data to write to the pipe.

        Returns
        -------
        None.

        """
        try:
            if isinstance(data, str) and isinstance(data, bytes):
                raise TypeError(
                    "The data to write to the pipe must be a list, str or bytes."
                )
            elif isinstance(data, list):
                for item in data:
                    conn.send(item)
            else:
                conn.send(data)
            conn.send(EOM_CHAR)
        except (OSError, BrokenPipeError):
            print("Pipe closed unexpectedly.")
            conn.close()
            

    @staticmethod
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
        # Essentialy checks if a message is waiting.
        try:
            state = conn.poll()
        except (OSError, BrokenPipeError):
            return False

        return True

    @classmethod
    def in_waiting(cls, conn):
        """
        Check if there is a message waiting.

        Parameters
        ----------
        conn : multiprocessing.connection.Connection
            The connection to check.

        Returns
        -------
        bool
            True if a message is waiting, False otherwise.
        """
        if cls.pipe_is_open(conn):
            return conn.poll()
        else:
            cls.close_pipe(conn)
            return False


class PipelineConnection(BaseConnector):
    """
    Connection method using a multiprocessing pipe.

    This connection method is most suited for when the frond and backend are running
    on the same machine.
    """

    _connection_method = "PIPELINE"

    def __init__(self, connection, role, settings=None):
        """
        Initialize the connection.

        Parameters
        ----------
        connection : multiprocessing.connection.Connection
            The connection to use.
        role : str
            The role of the connection. Either "FRONDEND" or "BACKEND".
        settings : ConfigParser
            Not used in this connection method but added for compatibility.
        """
        self._connection = connection
        self._role = role
        if role == "FRONTEND":
            self.__init_lock__()
        else:
            # The lock cannot be pickled, so it is created on the backend
            self._lock = None

    def __init_lock__(self):
        self._lock = tr.Lock()

    @property
    def is_connected(self):
        self._lock.acquire()
        state = PipeCom.pipe_is_open(self._connection)
        self._lock.release()
        return state

    def connect(self):
        # The pipe is connected on init and cannot reconnect
        pass

    def send_sentinel(self):
        print("Sending sentinel")
        self._lock.acquire()
        PipeCom.write_pipe(self._connection, self.SENTINEL)
        self._lock.release()

    def disconnect(self):
        self._lock.acquire()
        PipeCom.close_pipe(self._connection)
        self._lock.release()

    def send(self, data):
        self._lock.acquire()
        PipeCom.write_pipe(self._connection, data)
        self._lock.release()

    def message_waiting(self):
        """
        Check if a message is waiting.

        Returns:
        --------
        bool
            True if a message is waiting, False otherwise.

        """
        self._lock.acquire()
        state = PipeCom.in_waiting(self._connection)
        self._lock.release()
        return state

    def receive(self):
        """
        Receive the data from the pipe.

        Returns:
        --------
        data : list
            The received data.

        """
        # Check if a message is waiting
        self._lock.acquire()
        if not self._connection.poll():
            return None
        state = PipeCom.read_pipe(self._connection)
        self._lock.release()
        return state
